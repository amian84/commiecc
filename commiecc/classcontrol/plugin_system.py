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

import sys
import os
import gtk
import exceptions
import glob

_instances = {}
_abstract = []

class Plugin(object):
    capabilities = []
    name = None
    description = None
    icon = None
    default_enabled = True

    def setup(self):
        """called before the plugin is asked to do anything"""
        raise NotImplementedError
     
    def teardown(self):
        """called to allow the plugin to free anything"""
        raise NotImplementedError
    
    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.capabilities
        )    
        
_abstract.append(Plugin)

from utils import SlaveUIState

class ListSlavesPlugin(Plugin):
    capabilities = ['slaves_getter']
    filter_dead = True
    get_slaves = lambda: (None, None)

    def selected_slaves(self):
       return [slave for slave, state in self.get_slaves() if not \
                (self.filter_dead and state.status == SlaveUIState.ST_DEAD)]

_abstract.append(ListSlavesPlugin)

class NotifierPlugin(Plugin):
    capabilities = ['notify']
    notify_func = None

    def notify(self, **kwargs):
        try:
            return self.notify_func(**kwargs)
        except:
            print "Excepcion"

    def action_cb(self, **kwargs):
        raise NotImplementedError

_abstract.append(NotifierPlugin)

class UIPlugin(Plugin):
    def __init__(self, ui_file, toplevel_widget, extra_objects=[]):
        builder = gtk.Builder()
        if not builder.add_objects_from_file(ui_file, 
                [toplevel_widget] + extra_objects):
            raise PluginError, 'Cant load %s' % ui_file
        builder.connect_signals(self)
        
        self.toplevel_widget = builder.get_object(toplevel_widget)
        if not self.toplevel_widget:
            raise PluginError, 'Cant find toplevel widget %s' % toplevel_widget

        self.builder = builder

_abstract.append(UIPlugin)

class TabPlugin(UIPlugin):
    capabilities = ['tab']

_abstract.append(TabPlugin)

class MenuItemsPlugin(UIPlugin):
    capabilities = ['menuitems']
    separator = True
            
    @property
    def menuitems(self):
        items = [menuitem for menuitem in self.toplevel_widget]
        
        if self.separator:
            sep = gtk.SeparatorMenuItem()
            sep.show()
            items.insert(0, sep)

        return items

_abstract.append(MenuItemsPlugin)

class SubMenuPlugin(UIPlugin):
    capabilities = ['submenu']
    name = 'submenu'
    
    @property
    def submenu(self):
        if self.icon:
            menu = gtk.ImageMenuItem(self.name)
            menu.set_always_show_image (True)
            #The defined icon stands for a STOCK_ICON
            if self.icon in gtk.stock_list_ids():
                menu.set_image(gtk.image_new_from_stock(self.icon, 
                    gtk.ICON_SIZE_MENU))
            #Else it stands for a image file
            else:
                menu.set_image(self.icon)
        else:
            menu = gtk.MenuItem(self.name)

        #FIXME: This raises GtkWarning: gtk_menu_attach_to_widget()
        menu.set_submenu(self.toplevel_widget)
        menu.show()
        return menu
        
_abstract.append(SubMenuPlugin)    

def load_plugins(plugins):
    for plugin in [x for x in plugins if not x.startswith('__')]:
        __import__(plugin, None, None, [''])

def init_plugin_system(plugin_path):
    if not plugin_path in sys.path:
        sys.path.insert(0, plugin_path)
        
    load_plugins([os.path.basename(os.path.splitext(x)[0]) 
        for x in glob.glob(os.path.join(plugin_path, '*py'))])
    
def find_plugins():
    subklasses = []
    for klass in _abstract:
        subklasses += [k for k in klass.__subclasses__() if not k in _abstract]
    return set(subklasses)

def get_plugins_by_capability(capability):
    result = []
    for plugin in find_plugins():
        if capability in plugin.capabilities:
            if not plugin in _instances:
                _instances[plugin] = plugin()
            result.append(_instances[plugin])
    result.sort()
    return result
    
class PluginError(exceptions.Exception):
    def __init__(self, mesg=None, *args):
        self.mesg = mesg
        self.args = args

    def __str__(self):
        if self.args:
            return self.mesg + repr(self.args)
        else:
            return self.mesg
