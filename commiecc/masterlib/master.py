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

from service_discover import service_discover

STYPE = '_xmlrpc._tcp'

class EventDispatcher(gobject.GObject):
    SIGNAL = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                (gobject.TYPE_PYOBJECT,))

    SIGNAL2 = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                (gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT))
    
    __gsignals__ = {
        'slave_discovered' : SIGNAL,
        'slave_losed' : SIGNAL,
        'slave_alive': SIGNAL,
        'slave_dead': SIGNAL,
        'slave_locked': SIGNAL,
        'slave_unlocked': SIGNAL,
    }
    
    def __init__(self):
        gobject.GObject.__init__(self)
Dispatcher = EventDispatcher()

class Slave:
    def __init__(self, address, port, name, host, txt=''):
        #FIXME: It's better make immutable the attributes used in __hash__ 
        self.address = address
        self.port = port
        self.name = name
        self.host = host
    
        for i in txt: 
            val = ''.join([chr(x) for x in i]).split('=')
            self.__dict__[val[0].lower()] = val[1]

    def __repr__(self):
        return '<%s @ http://%s:%s>' % (self.name, self.address, self.port)
        
    def __eq__(self, other):
        return self.address == other.address and self.port == other.port \
                and self.name == other.name
    
    def __hash__(self):
        return hash(repr(self))
        
class Master:
    def __init__(self):
        self.slaves = {}
        service_discover.connect_service(STYPE, self.connect, self.disconnect)

    def get_slaves(self):
        return self.slaves.values()
        
    def connect(self, *args):
        print args
        try:
            address, port, name, host, txt = service_discover.resolve(*args)
        except Exception, err:
            print "Cant discover: ", err
            return
        slave = Slave(address, port, name, host, txt)
        self.slaves[args[:-1]] = slave
        Dispatcher.emit('slave_discovered', slave)
                        
    def disconnect (self, *args):
        slave = self.slaves[args[:-1]]
        Dispatcher.emit('slave_losed', slave)
        del self.slaves[args[:-1]]
                
if __name__ == '__main__':
    def discovered(dispatcher, slave, get_slaves):
        print 'Discovered:', slave
        print 'Current slaves:', get_slaves()
        
    def losed(dispatcher, slave, get_slaves):
        print 'Losed:', slave
        print 'Current slaves:', get_slaves()
        
    def rediscover(master):
        for args, slave in master.slaves.items():
            try:
                address, port, name, host, txt = service_discover.resolve(*args)
                print address, port, name, host                
            except:
                print 'wee'
        return True
        
    master = Master()
    #Dispatcher.connect('slave_discovered', discovered, master.get_slaves)
    #Dispatcher.connect('slave_losed', losed, master.get_slaves)
    gobject.timeout_add(5000, rediscover, master)
    gobject.MainLoop().run()
