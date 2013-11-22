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
import threading
import logging

LOG_MAIN = 'main_log'
LOG_FILE = '/var/log/commiecc-slave.log'
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%H:%M:%S'

def setup_main_logger():
    import logging.handlers

    main_logger = logging.getLogger(LOG_MAIN)
    main_logger.setLevel(LOG_LEVEL)
    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=300000, 
        backupCount=5)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    main_logger.addHandler(handler)

class log():
    def __init__(self, msg, level=logging.DEBUG):
        self.msg = msg
        self.level = level
        self.logger = logging.getLogger(LOG_MAIN)
        
    def __call__(self, f):
        def wrapped_f(*args):
            self.logger.log(self.level, self.msg)        
            return f(*args)
        return wrapped_f


import PAM
 
# Full-based on TcosMonitor TcosPAM.py module file by Mario Izquierdo
# http://wiki.tcosproject.org/Utils/TcosMonitor/
def pam_auth(user, password):
    class AuthConv:
        def __init__(self, password):
            self.password = password
 
        def __call__(self, auth, query_list, userData):
            resp = []
            for query, qt in query_list:
                if qt == PAM.PAM_PROMPT_ECHO_ON:
                    resp.append((self.password, 0))
                elif qt == PAM.PAM_PROMPT_ECHO_OFF:
                    resp.append((self.password, 0))
                elif qt == PAM.PAM_PROMPT_ERROR_MSG or type == PAM.PAM_PROMPT_TEXT_INFO:
                    print query
                    resp.append(('', 0))
                else:
                    return None
            return resp
 
 
    auth = PAM.pam()
    auth.start("passwd")
    auth.set_item(PAM.PAM_USER, user)
    auth.set_item(PAM.PAM_CONV, AuthConv(password))
    try:
        auth.authenticate()
        auth.acct_mgmt()
        return True
    except PAM.error, resp:
        return False

