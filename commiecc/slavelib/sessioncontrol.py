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

import dbus
import logging

import commands
import syslog

from utils import log

CK_URI = 'org.freedesktop.ConsoleKit'
CK_PATH = '/org/freedesktop/ConsoleKit'
CK_MANAGER_URI = CK_URI + '.Manager'
CK_MANAGER_PATH = CK_PATH + '/Manager'

UPSTART_PATH = '/com/ubuntu/Upstart'
UPSTART_URI = 'com.ubuntu.Upstart'
UPGDM_PATH = UPSTART_PATH + '/jobs/lightdm/_'
UPGDM_IFACE_URI = 'com.ubuntu.Upstart0_6.Instance'

class SessionControl():
    def __init__(self):
        self.bus = dbus.SystemBus()
        
        self.__ck_manager = dbus.Interface(self.bus.get_object(CK_URI, 
            CK_MANAGER_PATH), dbus_interface=CK_MANAGER_URI)

        self.__upgdm = dbus.Interface(self.bus.get_object(UPSTART_URI, 
            UPGDM_PATH), dbus_interface=UPGDM_IFACE_URI)

    @log('Logout order received', logging.INFO)
    def logout(self, user):
        if not user == 'lightdm': self.log_activity(user)
        self.__upgdm.Restart(False)
        return True
        
    @log('Reboot order received', logging.INFO)
    def reboot(self, user):
        if not user == 'lightdm': self.log_activity(user)
        self.__upgdm.Restart(False)
        self.__ck_manager.Restart()
        return True

    @log('Shutdown order received', logging.INFO)
    def shutdown(self, user):
        if not user == 'lightdm': self.log_activity(user)
        self.__ck_manager.Stop()
        return True

    def log_activity(self, username):
        gdmPid = self._pidof_gdm()
        syslog.openlog('gdm-session-worker[' + gdmPid + ']',0,syslog.LOG_AUTH)
        syslog.syslog(syslog.LOG_AUTH, 'pam_unix(gdm:session): session closed for user ' + username)

    def _pidof_gdm(self):
        gdm_str = '/usr/lib/gdm/gdm-session-worker'
        return commands.getoutput('pidof %s' % gdm_str)


if __name__ == '__main__':
    import gobject
    from dbus.mainloop.glib import DBusGMainLoop
 
    DBusGMainLoop(set_as_default=True)
 
    sc = SessionControl()
    gobject.MainLoop().run()
