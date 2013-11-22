# -*- coding: utf-8 -*-
# vim: ts=4 

import logging
import commands
import os
import time

from commiecc.slavelib.plugin_system import RPCPlugin, NotifierPlugin
from commiecc.slavelib import log

class DetachClient(RPCPlugin, NotifierPlugin):
    name = 'detach'
    description = 'Detach client from server'
    default_enabled = True
    capabilities = RPCPlugin.capabilities + NotifierPlugin.capabilities    
    
    @log('Detach client order received', logging.INFO)
    
    def rpc(self):
        try:
            os.popen('sed -i \'s/DEFAULT_RUNLEVEL=[0-9]/DEFAULT_RUNLEVEL=4/\' /etc/init/rc-sysinit.conf')
            os.popen('telinit 4')
            result = commands.getoutput('pidof nm-applet')
            if result != 0:
                os.kill(self.pidofnmapplet, signal.SIGKILL)
                time.sleep(5)
                os.popen('su $SUDO_USER -c nm-applet &')
            self.notify(title=_('Message received from master'), text='El equipo ha sido desacoplado del centro',
                    icon='commiecc-slave-desktop', urgency=1)
            return True

        except:
            return False


