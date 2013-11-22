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

import dbus 
import dbus.service
import logging

from utils import log

from commiecc.slavelib import Dispatcher

# DBus service parameters
COMMIECC_URI = "org.gnome.CommieCC"
COMMIECC_PATH = "/org/gnome/CommieCC"
LOCKER_IFACE_URI = COMMIECC_URI + '.ScreenLocker'
NOTIFIER_IFACE_URI = COMMIECC_URI + '.DesktopNotifier'

class DBusManager(dbus.service.Object):
    def __init__(self, bus_name):
        try:
            dbus.service.Object.__init__(self, bus_name, COMMIECC_PATH)
        except KeyError:
            # KeyError is thrown when the dbus interface is taken
            # that is there is other commiecc COMMIECC running somewhere
            print "D-Bus interface registration failed - other commiecc slave \
                running somewhere"
            pass

    # FIXME: How to decorate it?
    #@log('Lock order received', logging.INFO)
    @dbus.service.method(LOCKER_IFACE_URI)
    def Lock(self):
        self.Locked(True)
        Dispatcher.emit('locking_changed', True)

    #@log('Unlock order received', logging.INFO)
    @dbus.service.method(LOCKER_IFACE_URI)
    def Unlock(self):
        self.Locked(False)
        Dispatcher.emit('locking_changed', False)
        
    #@log('Stop lockers order received', logging.INFO)
    @dbus.service.method(LOCKER_IFACE_URI)
    def Stop(self):
        self.Stoped()
            
    @dbus.service.signal(LOCKER_IFACE_URI, signature='b')
    def Locked(self, locking_state):
        pass

    @dbus.service.signal(LOCKER_IFACE_URI)
    def Stoped(self):
        pass

    @dbus.service.signal(LOCKER_IFACE_URI)
    def Pinged(self):
        pass

    @dbus.service.method(NOTIFIER_IFACE_URI)
    def SendNotification(self, title, text, icon, urgency):
        self.NotificationSended(title, text, icon, urgency)
    
    @dbus.service.signal(NOTIFIER_IFACE_URI)
    def NotificationSended(self, title, text, icon, urgency):
        pass

if __name__ == '__main__':
    import gobject
    import dbus.mainloop.glib
    
    try:
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        name = dbus.service.BusName(COMMIECC_URI, dbus.SystemBus())
        controller = DBusManager(bus_name = name)
    except dbus.DBusException, e:
        print "can't init dbus: %s" % e

    gobject.MainLoop().run()
