#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# CommieCC is the legal property of J. Félix Ontañón <felixonta@gmail.com>
# Copyright (c) 2009 J. Félix Ontañón
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
###

import gobject
import time
import datetime
import logging
import pwd
import dbus
from dbus.mainloop.glib import DBusGMainLoop

from utils import LOG_MAIN

PROP_IFACE_URI = 'org.freedesktop.DBus.Properties'

NM_URI = 'org.freedesktop.NetworkManager'
NM_PATH = '/org/freedesktop/NetworkManager'
NM_IFACE_URI = NM_URI
NM_ACTIVE_CONN_IFACE_URI = NM_URI + '.Connection.Active'
NM_DEVICE_IFACE_URI = NM_URI + '.Device'
NM_WIRED_IFACE_URI = NM_DEVICE_IFACE_URI + '.Wired'
NM_WIRELESS_IFACE_URI = NM_DEVICE_IFACE_URI + '.Wireless'

CK_URI = 'org.freedesktop.ConsoleKit'
CK_PATH = '/org/freedesktop/ConsoleKit'
CK_MANAGER_URI = CK_URI + '.Manager'
CK_MANAGER_PATH = CK_PATH + '/Manager'

SEAT_IFACE_URI = 'org.freedesktop.ConsoleKit.Seat'
SESSION_IFACE_URI = 'org.freedesktop.ConsoleKit.Session'

DBusGMainLoop(set_as_default=True)
        
class EventDispatcher(gobject.GObject):
    SIGNAL = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                (gobject.TYPE_PYOBJECT,))
    SIGNAL3 = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING))
                
    __gsignals__ = {
        'new_x11_session' : SIGNAL3,
        'losed_x11_session' : SIGNAL3,
        'connection_changed': SIGNAL,
        'locking_changed': SIGNAL,
    }
    
    def __init__(self):
        gobject.GObject.__init__(self)
Dispatcher = EventDispatcher()

class NMController():
    def __init__(self):
        self.logger = logging.getLogger(LOG_MAIN)        
        self.active_ifaces = self.get_active_ifaces()
        bus = dbus.SystemBus()
        bus.add_signal_receiver(self.__prop_changed, 'PropertiesChanged', 
            NM_ACTIVE_CONN_IFACE_URI)

    def __prop_changed(self, props):
        if (props.has_key('State') and props['State'] == 2) or \
            (props.has_key('Default') and props['Default']):

            current_ifaces = self.get_active_ifaces()
            
            if current_ifaces != self.active_ifaces:
                self.active_ifaces = current_ifaces
                self.logger.info('New connection available')
                Dispatcher.emit('connection_changed', self.active_ifaces)
        
    @staticmethod
    def get_active_ifaces():
        iface = {}
        bus = dbus.SystemBus()
        nm_iface = dbus.Interface(bus.get_object(NM_URI, NM_PATH), 
            dbus_interface=PROP_IFACE_URI)

        active_conns_path = nm_iface.Get(NM_IFACE_URI, 'ActiveConnections')
                
        for active_conn_path in active_conns_path:
            active_conn_iface = dbus.Interface(bus.get_object(NM_URI, 
                active_conn_path), dbus_interface=PROP_IFACE_URI)
                
            active_devs_path = active_conn_iface.Get(NM_ACTIVE_CONN_IFACE_URI, 
                'Devices')
            
            for active_dev_path in active_devs_path:
                active_dev_iface = dbus.Interface(bus.get_object(NM_URI,
                    active_dev_path), dbus_interface=PROP_IFACE_URI)
                
                devicetype = active_dev_iface.Get(NM_DEVICE_IFACE_URI, 'DeviceType')
                interface = active_dev_iface.Get(NM_DEVICE_IFACE_URI, 'Interface')
                
                #Wired
                if devicetype == 1:
                    hwaddr = active_dev_iface.Get(NM_WIRED_IFACE_URI, 'HwAddress')
                    
                #Wireless
                elif devicetype == 2:
                    hwaddr = active_dev_iface.Get(NM_WIRELESS_IFACE_URI, 'HwAddress')
                    
                iface[str(interface)] = str(hwaddr)
               
        return iface

    @staticmethod
    def get_all_macs():
        iface = []
        bus = dbus.SystemBus()
        nm_iface = dbus.Interface(bus.get_object(NM_URI, NM_PATH), 
            dbus_interface=NM_URI)

        devices_path = nm_iface.GetDevices()
                
        for device_path in devices_path:
            device_iface = dbus.Interface(bus.get_object(NM_URI, 
                device_path), dbus_interface=PROP_IFACE_URI)
                
            devicetype = device_iface.Get(NM_DEVICE_IFACE_URI, 'DeviceType')
            interface = device_iface.Get(NM_DEVICE_IFACE_URI, 'Interface')
                
            #Wired
            if devicetype == 1:
                hwaddr = device_iface.Get(NM_WIRED_IFACE_URI, 'HwAddress')
                    
            #Wireless
            elif devicetype == 2:
                hwaddr = device_iface.Get(NM_WIRELESS_IFACE_URI, 'HwAddress')
                    
            iface.append(str(hwaddr))
       
        return iface
        
class CKController():
    def __init__(self):
        self.active_sessions = {}
        self.bus = dbus.SystemBus()
        self.logger = logging.getLogger(LOG_MAIN)
                
        ck_manager = dbus.Interface(self.bus.get_object(CK_URI, CK_MANAGER_PATH), 
            dbus_interface=CK_MANAGER_URI)

        for seat_path in ck_manager.GetSeats():
            seat = dbus.Interface(self.bus.get_object(CK_URI, seat_path), 
                dbus_interface=SEAT_IFACE_URI)
            seat.connect_to_signal('SessionAdded', self.new_session)
            seat.connect_to_signal('SessionRemoved', self.closed_session)
           
            for session_path in seat.GetSessions():
                session = dbus.Interface(self.bus.get_object(CK_URI, session_path), 
                    dbus_interface=SESSION_IFACE_URI)

                ret = self.local_x11_user(session)
                if ret:
                    username, creation_time, display = [str(x) for x in ret]

                    Dispatcher.emit('new_x11_session', username, creation_time,
                        display)

                    self.active_sessions[session_path] = (username, creation_time,
                        display)
                        
    def local_x11_user(self, session):
        if session.IsLocal() and session.GetX11Display():
            pwduser = pwd.getpwuid(session.GetUnixUser())
            username =  pwduser.pw_name
            creation_time = session.GetCreationTime()
            display = session.GetX11Display()
            return username, creation_time, display
            
        return None
        
    def new_session(self, session_path):
        session = dbus.Interface(self.bus.get_object(CK_URI, session_path), 
            dbus_interface=SESSION_IFACE_URI)

        ret = self.local_x11_user(session)
        if ret:
            username, creation_time, display = [str(x) for x in ret]
            Dispatcher.emit('new_x11_session', username, creation_time, display)
            self.logger.info('New x11 session found on %s', display)

            self.active_sessions[session_path] = (username, creation_time,
                display)
            
    def closed_session(self, session_path):
        if self.active_sessions.has_key(session_path):
            username, creation_time, display = self.active_sessions.pop(session_path)
            Dispatcher.emit('losed_x11_session', username, creation_time, display)
            self.logger.info('Closed x11 session on %s', display)
        else:
            pass
                   
if __name__ == '__main__':
    def new_x11(dispatcher, data):
        print 'Discovered:', data
        
    def losed_x11(dispatcher, data):
        print 'Losed:', data
 
    def changed_connection(dispatcher, data):
        print 'Connections', data
    
    nm = NMController()           
    ck = CKController()
    
    print ck.active_sessions
    print NMController.get_active_ifaces()
    
    Dispatcher.connect('new_x11_session', new_x11)
    Dispatcher.connect('losed_x11_session', losed_x11)
    Dispatcher.connect('connection_changed', changed_connection)
    gobject.MainLoop().run()
