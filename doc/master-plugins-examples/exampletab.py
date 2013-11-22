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

from commiecc.conf import MASTER_DEFAULT_PLUGINS
from commiecc.classcontrol.plugin_system import TabPlugin
from commiecc.masterlib import Dispatcher

class CalendarTab(TabPlugin):
    ui = MASTER_DEFAULT_PLUGINS + 'exampletab.ui'
    name = 'Calendar'
    description = 'Shows a calendar'
    default_enabled = False
    
    def __init__(self):
        TabPlugin.__init__(self, CalendarTab.ui, toplevel_widget='vpaned1')
        Dispatcher.connect('slave_discovered', self.discovered)
        
    def discovered(self, dispatcher, slave):
        pass
