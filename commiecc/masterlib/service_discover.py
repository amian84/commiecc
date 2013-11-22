# -*- coding: utf-8 -*-
###
#
# Copyright (c) 2006 Mehdi Abaakouk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA
#
###

import gobject
try:
    import avahi, dbus
    if getattr(dbus, 'version', (0,0,0)) >= (0,41,0):
        import dbus.glib
except ImportError: dbus_imported = False
else: dbus_imported=True

class ServiceDiscover:
    domain = 'local'
    
    def __init__(self): 
        if dbus_imported:
            try:self.bus = dbus.SystemBus()
            except:self.bus=None    
        if dbus_imported and self.bus:
            try:
                self.server = dbus.Interface(self.bus.get_object(
                    avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER), 
                    avahi.DBUS_INTERFACE_SERVER)
            except:
                print 'No avahi support'
        else:
            print 'No avahi support'
    
        self.services =  {}
        self.connected_services = {}
        self.id = 0
        
    def connect_service(self, stype, connect, disconnect):

        if dbus_imported:
            browser = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, 
                        self.server.ServiceBrowserNew(avahi.IF_UNSPEC, 
                                avahi.PROTO_UNSPEC, stype, 
                                self.domain, dbus.UInt32(0))), 
                        avahi.DBUS_INTERFACE_SERVICE_BROWSER)
                        
            browser.connect_to_signal('ItemNew', connect)
            browser.connect_to_signal('ItemRemove', disconnect)
        
    def resolve(self, interface, protocol, name, stype, domain, flags=None):
        interface, protocol, name, stype, domain, host, aprotocol, address, \
            port, txt, flags = self.server.ResolveService(interface, protocol, 
                        name, stype, domain, avahi.PROTO_INET, dbus.UInt32(0))

        return address, port, name, host, txt
    
service_discover = ServiceDiscover()
