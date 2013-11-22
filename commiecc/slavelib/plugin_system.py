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
import glob

_instances = {}
_abstract = []

class Plugin(object):
    capabilities = []
    name = None
    description = None
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

# FIXME: Add logging capabilities
class RPCPlugin(Plugin):
    capabilities = ['rpc']
    
    def rpc(self, *args):
        """do whatever the rpc does"""
        raise NotImplementedError

_abstract.append(RPCPlugin)

class NotifierPlugin(Plugin):
    capabilities = ['notify']
    notify_func = None

    def notify(self, **kwargs):
        return self.notify_func(**kwargs)

_abstract.append(NotifierPlugin)

class ScreenLockerPlugin(Plugin):
    capabilities = ['screenlock']
    lock_func = None
    unlock_func = None

    def lock(self):
        return self.lock_func()

    def unlock(self):
        return self.unlock_func()

_abstract.append(ScreenLockerPlugin)

# TODO: Maybe in a future
"""
class DBusPlugin(Plugin):
    def __init__(self):
        pass

_abstract.append(DBusPlugin)
"""

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
        
    return subklasses

def get_plugins_by_capability(capability):
    result = []
    for plugin in find_plugins():
        if capability in plugin.capabilities:
            if not plugin in _instances:
                _instances[plugin] = plugin()
            result.append(_instances[plugin])
    return result
