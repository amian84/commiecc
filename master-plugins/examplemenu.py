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
    SubMenuPlugin, MenuItemsPlugin, NotifierPlugin
from commiecc.masterlib import Dispatcher
from commiecc.classcontrol import do_work, RPC_TIMEOUT, TEXTBUFFER_LOGGER


'''
class MessageSubMenu(SubMenuPlugin, ListSlavesPlugin, NotifierPlugin):
    ui = MASTER_DEFAULT_PLUGINS + 'messagemenu.ui'
    icon = gtk.STOCK_ADD
    name = 'Extra'
    description = 'Extra functions'
    capabilities = SubMenuPlugin.capabilities + ListSlavesPlugin.capabilities \
     + NotifierPlugin.capabilities
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
        self.notify(title='Recived', text=result, actions=['hi', 'Hi', 
            'bye', 'Bye'])

    def action_cb(self, dispatcher, action_key):
        print 'Action key:', action_key
'''

         
class MessagesMenuItems(MenuItemsPlugin, ListSlavesPlugin):
    ui = MASTER_DEFAULT_PLUGINS + 'messagemenu.ui'
    name = 'Desktop Messages'
    description = 'Notifies messages to slaves desktop'
    default_enabled = True
    capabilities = MenuItemsPlugin.capabilities + ListSlavesPlugin.capabilities
    
    def __init__(self):
        MenuItemsPlugin.__init__(self, MessagesMenuItems.ui, 
            toplevel_widget='menu1', extra_objects=['image1', 'image2', 
                'message_dialog'])
                
        self.message_dialog = self.builder.get_object('message_dialog')
        self.message_entry = self.builder.get_object('message_entry')
        
    def sayhello_menuitem_activate_cb(self, widget, data=None):
        for slave in self.selected_slaves():
            do_work('message', slave.address, slave.port, [_('Hello slave!')])
   
    def message_menuitem_activate_cb(self, widget, data=None):
        if self.selected_slaves():
            message = ''
            self.message_entry.set_text(message)
            if self.message_dialog.run() == gtk.RESPONSE_OK:
                message = self.message_entry.get_text()
            self.message_dialog.hide()
    
            if message:    
                for slave in self.selected_slaves():
                    do_work('message', slave.address, slave.port, [message])
