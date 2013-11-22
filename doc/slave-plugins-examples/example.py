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

import logging

from commiecc.slavelib.plugin_system import RPCPlugin
from commiecc.slavelib import Dispatcher, log

class HelloWorld(RPCPlugin):
    name = 'helloworld'
    description = 'A Helloworld test RPC'
    default_enabled = True

    @log('Helloworld example order received', logging.INFO)
    def rpc(self, param=''):
        return 'Hello World!: %s' % param

class SignalListener(RPCPlugin):
    name = 'listener'
    description = 'A capable signal listener RPC'
    default_enabled = True

    def __init__(self):
        Dispatcher.connect('new_x11_session', self.new_x11)
        self.username, self.creation_time, self.display = None, None, None
        
    def new_x11(self, dispatcher, username, creation_time, display):
        print username, creation_time, display
        self.username, self.creation_time, self.display = username, creation_time, display

    @log('Listener example order received', logging.INFO)
    def rpc(self):
        return self.username, self.creation_time, self.display
