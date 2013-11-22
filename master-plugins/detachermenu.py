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


class MessagesMenuItems(MenuItemsPlugin, ListSlavesPlugin, NotifierPlugin):
    ui = MASTER_DEFAULT_PLUGINS + 'detachermenu.ui'
    name = 'Client Detacher'
    description = 'Detach client from server'
    default_enabled = True
    capabilities = MenuItemsPlugin.capabilities + ListSlavesPlugin.capabilities + NotifierPlugin.capabilities
    separator = False

    def __init__(self):
        MenuItemsPlugin.__init__(self, MessagesMenuItems.ui, 
            toplevel_widget='menu2', extra_objects=['image1']) 
        self.logger = logging.getLogger(TEXTBUFFER_LOGGER)
                
    def detacher_menuitem_activate_cb(self, widget, data=None):
        for slave in self.selected_slaves():
            do_work('detach', slave.address, slave.port, '',
                RPC_TIMEOUT, self.cb)
            if (self.cb):
                self.notify(title=_('Control de Puestos'), text='El cliente %s ha sido desacoplado del centro correctamente' % slave.host,
                        icon='commiecc', urgency=1)
                self.logger.info('Slave %s has been detached' % slave.host) 
            else:
                print "not so good!" 

    def cb(self, result):
        self.logger.info('Recived %s' % result)
        if (result):
            return True
        else:
            return False
