# -*- coding: utf-8 -*-
# vim: ts=4 

import logging
import commands
import os
import time

from commiecc.slavelib.plugin_system import RPCPlugin, NotifierPlugin
from commiecc.slavelib import log

class SetPassClient(RPCPlugin, NotifierPlugin):
    name = 'setpass'
    description = 'Set random password for volunteers'
    default_enabled = True
    capabilities = RPCPlugin.capabilities + NotifierPlugin.capabilities    
    
    @log('Setting password...', logging.INFO)
    
    def rpc(self, newpassword, expire_date):
        try:
#            newpassword = commands.getoutput('pwgen -s -B -A -N 1 6')
            os.popen('usermod -p `mkpasswd ' + newpassword +'` voluntario')
            os.popen('chage -E '+expire_date+' voluntario')
            
            return True

        except:
            return False


