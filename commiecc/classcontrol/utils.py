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

import threading

class SlaveUIState:
    ST_ALIVE, ST_DEAD = range(2)
    
    def __init__(self):
        self.alive_evt = threading.Event()
        self.status = SlaveUIState.ST_ALIVE
        self.locked = None

import logging

TEXTBUFFER_LOGGER = 'log_buffer'

class TextBufferHandler(logging.StreamHandler):
    def __init__(self, textbuffer):
        logging.StreamHandler.__init__(self)
        self.textbuffer = textbuffer
        
    def emit(self, record):
        logging.StreamHandler.emit(self, record)
        self.textbuffer.insert_at_cursor(self.formatter.format(record)+'\n')

import commiecc.masterlib.timeout_xmlrpclib as xmlrpclib
from commiecc.common import threaded

RPC_TIMEOUT = 5

@threaded
def do_work(method, address, port, args=None, rpc_timeout=RPC_TIMEOUT, cb=None):
    server = xmlrpclib.ServerProxy("http://%s:%s" % (address, port), 
        timeout=rpc_timeout)

    try:
        if args:
            result = eval('server.%s(*args)' % method)
        else:
            result = eval('server.%s()' % method)
           
        if cb:
            cb(result)
    except Exception, err:
        logger = logging.getLogger(TEXTBUFFER_LOGGER)
        logger.error('Method %s failed %s: %s' % (method, address, str(err)))
