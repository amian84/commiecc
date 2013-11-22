# -*- coding: utf-8 -*-
# vim: ts=4 

import dbus
import logging
import time
import gobject

from commiecc.slavelib.plugin_system import RPCPlugin
from commiecc.slavelib import log

NM_URI = 'org.freedesktop.NetworkManager'
NM_PATH = '/org/freedesktop/NetworkManager'
NM_IFACE_URI = NM_URI

#Network Manager States

NM_STATE_UNKNOWN = 0
NM_STATE_ASLEEP = 1
NM_STATE_CONNECTING = 2
NM_STATE_CONNECTED = 3
NM_STATE_DISCONNECTED = 4

class RenewalIP(RPCPlugin):
    name = 'renewal'
    description = 'Renewal the IP address'


    default_enabled = True
    bus = dbus.SystemBus()
    nm_iface = dbus.Interface(bus.get_object(NM_URI, NM_PATH),dbus_interface=NM_IFACE_URI)
 


    @log('Renewal IP order received', logging.INFO)
    def rpc(self):
        def do_renewal():
            self.nm_iface.sleep()            
            time.sleep(3)

           # if self.nm_iface.state()==NM_STATE_ASLEEP:
           # Se ha detectado un fallo de segmentacion en la llamada a la funcion state
	   # no afecta cuando se llama de manera local, es totalmente aleatoria 
	   # intentar reproducir mas tarde, es posible que sea debido a las llamadas rpc
	   # o por los hilos. Hemos optado aqui por no llamar a dicha funcion
            self.nm_iface.wake()
            print "Renewal done"
	    return False
   
	for i in range (1,3):
   
	    try:           
		gobject.timeout_add(1000, do_renewal)
                return True
	           		
            except e: 
		print "Exception %s" %e
	 	time.sleep(10)
		return False

    	if self.nm_iface is None:
 	    print "Unable to connect to the NetworkManager"  
	    return False  		
