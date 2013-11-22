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

import gtk
import logging

from commiecc.conf import MASTER_DEFAULT_PLUGINS
from commiecc.classcontrol.plugin_system import ListSlavesPlugin, \
    SubMenuPlugin, MenuItemsPlugin
from commiecc.masterlib import Dispatcher
from commiecc.classcontrol import do_work, RPC_TIMEOUT, TEXTBUFFER_LOGGER

class MessageSubMenu(SubMenuPlugin, ListSlavesPlugin):
    ui = MASTER_DEFAULT_PLUGINS + 'messagemenu.ui'
    icon = gtk.STOCK_ADD
    name = 'Extra'
    description = 'Extra functions'
    capabilities = SubMenuPlugin.capabilities + ListSlavesPlugin.capabilities
    default_enabled = True
        
    def __init__(self):
        SubMenuPlugin.__init__(self, MessageSubMenu.ui, toplevel_widget='menu',
            extra_objects=['hello_image', 'session_image'])
        ListSlavesPlugin.__init__(self)
        self.logger = logging.getLogger(TEXTBUFFER_LOGGER)

    def hello_menuitem_activate_cb(self, widget, data=None):
        for slave in self.selected_slaves():
            do_work('helloworld', slave.address, slave.port, ['returnme'], 
                RPC_TIMEOUT, self.cb)
            self.logger.debug('HelloWorld sended to %s' % slave.host)

    def session_menuitem_activate_cb(self, widget, data=None):
        for slave in self.selected_slaves():
            do_work('listener', slave.address, slave.port, None, RPC_TIMEOUT, 
                self.cb)
            self.logger.debug('Listener sended to %s' % slave.host)
            
    def cb(self, result):
        self.logger.info('Recived %s' % result)
        
class TestMenuItems(MenuItemsPlugin):
    ui = MASTER_DEFAULT_PLUGINS + 'messagemenu.ui'
    name = 'Test'
    description = 'Test menuitems'
    default_enabled = True

    def __init__(self):
        MenuItemsPlugin.__init__(self, TestMenuItems.ui, 
            toplevel_widget='menu1')
        
    def menuitem1_activate_cb(self, widget, data=None):
        print "menuitem1 callback"
    
    def menuitem2_activate_cb(self, widget, data=None):
        print "menuitem2 callback"
