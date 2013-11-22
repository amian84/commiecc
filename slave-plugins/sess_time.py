# -*- coding: utf-8 -*-
# vim: ts=4 

import logging
import commands
import os
import time
import dbus
import gobject

from commiecc.slavelib.plugin_system import RPCPlugin, NotifierPlugin, ScreenLockerPlugin
from commiecc.slavelib import log

UPSTART_PATH = '/com/ubuntu/Upstart'
UPSTART_URI = 'com.ubuntu.Upstart'
UPGDM_PATH = UPSTART_PATH + '/jobs/lightdm/_'
UPGDM_IFACE_URI = 'com.ubuntu.Upstart0_6.Instance'

class SessionTime(RPCPlugin, NotifierPlugin, ScreenLockerPlugin):
    name = 'sess_time'
    description = 'Detach client from server'
    default_enabled = True
    capabilities = RPCPlugin.capabilities + NotifierPlugin.capabilities + ScreenLockerPlugin.capabilities

    idles = []
    session_time = 0
    bus = dbus.SystemBus()

    upgdm_controller = dbus.Interface(bus.get_object(UPSTART_URI,
            UPGDM_PATH), dbus_interface=UPGDM_IFACE_URI) 

    @log('Session time order received', logging.INFO)
    def rpc(self, sess_time):

        def notify_half():
            half_time = time.gmtime(self.session_time * 0.5)
            ht_string = '%.2i:%.2i:%.2i' % (half_time.tm_hour, half_time.tm_min, half_time.tm_sec)

            self.notify(title=_('Tiempo de Sesión:'), text='Ha alcanzado la mitad de la sesión. La sesión terminará en %s' % ht_string,
                    icon='commiecc', urgency=1)
            return False

        def notify_quarter():
            quarter_time = time.gmtime(self.session_time * 0.25)
            qt_string = '%.2i:%.2i:%.2i' % (quarter_time.tm_hour, quarter_time.tm_min, quarter_time.tm_sec)

            self.notify(title=_('Tiempo de Sesión:'), text='Resta un cuarto de la sesión establecida. La sesión terminará en %s' % qt_string,
                    icon='commiecc', urgency=1)
            return False

        def notify_two():
            self.notify(title=_('Tiempo de Sesión:'), text='ATENCIÓN: Quedan 2 minutos para el final de la sesión. Empiece a guardar todos sus documentos si no desea pérdidas de información debido al cierre automático de la sesión. Gracias.',
                    icon='commiecc', urgency=1)
            return False

        def notify_one():
            self.notify(title=_('Tiempo de Sesión:'), text='ATENCIÓN: En 1 minuto se procederá a cerrar la sesión. Guarde documentos, si no lo ha hecho ya, y cierre todas las aplicaciones para asegurar un correcto cierre de la sesión y evitar problemas en futuras sesiones. Gracias.',
                    icon='commiecc', urgency=1)
            return False

        def end_session():
            self.upgdm_controller.Restart(False)
            return False

        def remove_idles():
            for idle in self.idles:
                gobject.source_remove(idle)

            self.idles = []


        # process for apply session times begins
        self.session_time = self.time_to_secs(sess_time)

        # If new session time has been setted remove old idles
        if self.idles.__len__() != 0:
            remove_idles()

        if self.session_time == 0:
            return True


        self.unlock()

        self.HALF_TIME = (self.session_time * 0.5) * 1000
        self.QUARTER_TIME = (self.session_time * 0.75) * 1000
        self.TWO_MIN = (self.session_time - 120) * 1000
        self.ONE_MIN = (self.session_time - 60) * 1000
        self.END_TIME = self.session_time * 1000
        
        try:
            idle_half = gobject.timeout_add(int(self.HALF_TIME), notify_half)
            idle_quarter = gobject.timeout_add(int(self.QUARTER_TIME), notify_quarter)
            idle_two = gobject.timeout_add(int(self.TWO_MIN), notify_two)
            idle_one = gobject.timeout_add(int(self.ONE_MIN), notify_one)
            idle_end = gobject.timeout_add(self.END_TIME, end_session)

            self.notify(title=_('Tiempo de Sesión:'), text='Tiempo de session establecido a %s' % sess_time,
                    icon='commiecc', urgency=1)

            self.idles = [idle_half, idle_quarter, idle_two, idle_one, idle_end]

            return True

        except:
            return False

    def time_to_secs(self, time):
        session_time = (int(time.split(':')[0]) * 3600) + (int(time.split(':')[1]) * 60)
        return session_time


