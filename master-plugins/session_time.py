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
import gobject

from commiecc.conf import MASTER_DEFAULT_PLUGINS
from commiecc.classcontrol.plugin_system import ListSlavesPlugin, \
    SubMenuPlugin, MenuItemsPlugin, NotifierPlugin
from commiecc.masterlib import Dispatcher
from commiecc.classcontrol import do_work, RPC_TIMEOUT, TEXTBUFFER_LOGGER


class MessagesMenuItems(MenuItemsPlugin, ListSlavesPlugin, NotifierPlugin):
    ui = MASTER_DEFAULT_PLUGINS + 'session_time.ui'
    name = 'Session Time'
    description = 'Establish session time'
    default_enabled = True
    capabilities = MenuItemsPlugin.capabilities + ListSlavesPlugin.capabilities + NotifierPlugin.capabilities
    separator = False
    
    def __init__(self):
        MenuItemsPlugin.__init__(self, MessagesMenuItems.ui, 
            toplevel_widget='menu2', extra_objects=['messagedialog1','image1','image2','liststore1']) 

        self.time_dialog = self.builder.get_object('messagedialog1')
        self.time_combo = self.builder.get_object('combobox1')
        self.combo_list = self.builder.get_object('liststore1')

        self.logger = logging.getLogger(TEXTBUFFER_LOGGER)

    def session_time_menuitem_activate_cb(self, widget, data=None):
        if self.selected_slaves():
            result = self.time_dialog.run()
            if result == gtk.RESPONSE_OK:
                print self.time_combo.get_active_text()

                for slave in self.selected_slaves():
                    do_work('sess_time', slave.address, slave.port, [self.time_combo.get_active_text()],
                        RPC_TIMEOUT, self.cb)
                    if (self.cb):
                        if self.time_combo.get_active_text() == '00:00':
                            self.notify(title=_('Control de Puestos'), 
                                    text='Se ha eliminado el tiempo de sesion del equipo %s correctamente' % slave.host,
                                    icon='commiecc', urgency=1)
                            self.logger.info('Session time for slave %s has been removed' % slave.host)
                        else:
                            self.notify(title=_('Control de Puestos'), 
                                    text='Se ha establecido el tiempo de sesion del equipo %s a %s' % (slave.host, self.time_combo.get_active_text()),
                                    icon='commiecc', urgency=1)
                            self.logger.info('Session time for slave %s has been set to %s' % (slave.host, self.time_combo.get_active_text())) 
                    else:
                        self.notify(title=_('Control de Puestos'),
                                    text='No se ha establecido el tiempo de sesion del equipo %s correctamente' % slave.host,
                                    icon='commiecc', urgency=1)
                        self.logger.error('Session time for slave %s goes wrong' % slave.host)
            else:
                print 'Cancelled from ui'
            
            self.time_dialog.hide()


    def session_time_menuitem2_activate_cb(self, widget, data=None):
        for slave in self.selected_slaves():
            do_work('sess_time', slave.address, slave.port, ['00:00'],
                RPC_TIMEOUT, self.cb)
            if (self.cb):
                self.notify(title=_('Control de Puestos'),
                                text='Se ha eliminado el tiempo de sesion del equipo %s correctamente' % slave.host,
                                icon='commiecc', urgency=1)
                self.logger.info('Session time for slave %s has been removed' % slave.host)
            else:
                self.notify(title=_('Control de Puestos'),
                                text='Ha sido imposible desactivar el tiempo de sesion del equipo %s' % slave.host,
                                icon='commiecc', urgency=1)
                self.logger.error('Remove of session time for slave %s goes wrong' % slave.host)

    def cb(self, result):
        self.logger.info('Received %s' % result)
        if (result):
            return True
        else:
            return False
