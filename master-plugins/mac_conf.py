# -*- coding: utf-8 -*-
# vim: ts=4 

import gtk
import logging
import gobject
from commiecc.masterlib.service_discover import ServiceDiscover

from commands import getoutput

from commiecc.conf import MASTER_DEFAULT_PLUGINS
from commiecc.classcontrol import do_work, TEXTBUFFER_LOGGER
from commiecc.classcontrol.plugin_system import TabPlugin
from commiecc.masterlib import Dispatcher
from commiecc.classcontrol.plugin_system import NotifierPlugin
from ldapmanager import *

SUBNET = '172.26.1.'
ICON_COL, NAME_COL, IP_COL, MACS_COL, ALLMACS_COL = range(5)

theme = gtk.icon_theme_get_default()
wired_icon = theme.load_icon('network-wired', 24, 0)
offline_icon = theme.load_icon('network-offline', 24, 0)
printer_icon = theme.load_icon('printer', 24, 0)

#ldap = {'cliente-1':'00:AA:BB:CC:DD:EE', 'cliente-2':'00:BB:CC:DD:EE:FF, 00:CC:DD:EE:FF:GG', 'impresora-laser1':'00:11:22:33:44:55',}# 'orion.local':'00:VV:SS:AA:DD:CC'}
#available_computers= ['cliente-1', 'cliente-2', 'cliente-3', 'cliente-4', 'cliente-5']
available_computers= ['cliente-1', 'cliente-2', 'cliente-3', 'cliente-4', 'cliente-5', 'cliente-6', 'cliente-7', 'cliente-8', 'cliente-9', 'cliente-10', 'cliente-11', 'cliente-12', 'cliente-13', 'cliente-14', 'cliente-15', 'cliente-16', 'cliente-17', 'cliente-18', 'cliente-19', 'cliente-20', 'cliente-21', 'cliente-22', 'cliente-23', 'cliente-24', 'cliente-25', 'cliente-26', 'cliente-27', 'cliente-28', 'cliente-29', 'cliente-30', 'cliente-31', 'cliente-32', 'cliente-33', 'cliente-34', 'cliente-35', 'cliente-36', 'cliente-37', 'cliente-38', 'cliente-39', 'cliente-40', 'cliente-41', 'cliente-42', 'cliente-43', 'cliente-44','cliente-45']

available_printers= ['impresora-laser1', 'impresora-laser2']

def get_ip_by_hostname(hostname):
    try:
        if hostname.startswith('impresora'):
            number = hostname.split('-')[1]
            number = number[-1]
            return SUBNET + str(200 + int(number[-1]))
        else:
            number = hostname.split('-')[1]
            number2=int(number)
            number=number2-1
            return SUBNET + str(10 + int(number))
    except:
        return SUBNET + '?'

class PrinterDiscover(gobject.GObject):
    STYPE = '_pdl-datastream._tcp'

    SIGNAL = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                (gobject.TYPE_PYOBJECT,))

    __gsignals__ = {
        'printer_discovered' : SIGNAL,
        'printer_losed' : SIGNAL,
    }

    def __init__(self):
        gobject.GObject.__init__(self)

        self.printers = {}
	self.discoverer = ServiceDiscover()

        self.discoverer.connect_service(PrinterDiscover.STYPE, self.discovered, self.losed)

    def get_printers(self):
        return self.printers.values()

    def discovered(self, *args):
	print args
        try:
            address, port, name, host, txt = self.discoverer.resolve(*args)
            mac = getoutput('arping -f -w 10 '+address+'|grep reply|awk \'{print $5}\'').strip('[[,]]')
        except Exception, err:
            print "Cant discover: ", err
            return
        printer = {'address': address, 'port': port, 'name': name, 'host': host, 'txt': txt, 'mac': mac}
        self.printers[args[:-1]] = printer
        self.emit('printer_discovered', printer)

    def losed (self, *args):
        printer = self.printers[args[:-1]]
        self.emit('printer_losed', printer)
        del self.printers[args[:-1]]

class ComputersTab(TabPlugin, NotifierPlugin):
    ui = MASTER_DEFAULT_PLUGINS + 'mac_conf.ui'
    name = 'Registro'
    description = 'Manage the computers'
    default_enabled = True
    capabilities = TabPlugin.capabilities + NotifierPlugin.capabilities
    dict_avahi={}    

    def __init__(self):
        TabPlugin.__init__(self, ComputersTab.ui, toplevel_widget='vpaned1',
            extra_objects=['reg_liststore', 'unreg_liststore', 
                'reg_menu', 'edit_dialog', 'printer_dialog', 'available_store'])

        self.reg_store = self.builder.get_object('reg_liststore')
        self.reg_tv = self.builder.get_object('reg_tv')
        self.unreg_store = self.builder.get_object('unreg_liststore')
        self.unreg_iv = self.builder.get_object('unreg_iv')
        self.reg_menu = self.builder.get_object('reg_menu')

        self.edit_dialog = self.builder.get_object('edit_dialog')
        self.available_store = self.builder.get_object('available_store')
        self.name_box = self.builder.get_object('name_box')
        self.name_lbl = self.builder.get_object('name_lbl')
        self.ip_lbl = self.builder.get_object('ip_lbl')

        self.printer_dialog = self.builder.get_object('printer_dialog')
        self.printer_name_box = self.builder.get_object('printer_name_box')
        self.printer_mac_entry = self.builder.get_object('printer_mac_entry')

        self.populate()
        self.logger = logging.getLogger(TEXTBUFFER_LOGGER)

        self.printer_discover = PrinterDiscover() 
        self.printer_discover.connect('printer_discovered', self.printer_discovered)
        self.printer_discover.connect('printer_losed', self.printer_losed)

        Dispatcher.connect('slave_discovered', self.discovered)
        Dispatcher.connect('slave_alive', self.discovered)        
        Dispatcher.connect('slave_losed', self.losed)
        Dispatcher.connect('slave_dead', self.losed)
                
    def populate(self):
        self.reg_store.clear()
        dict_mac={}
        l1=[]
        for name, macs in get_clients_registered().items(): 
            icon = offline_icon
            if name.startswith('impresora'):
		    icon = printer_icon
                    dict_mac[name] = macs
            elif name.startswith("cliente"):
               icon = offline_icon
               if name[-1].isalpha():
                   name2=name.strip(name[-1])                  
               elif name[-1].isdigit():
                   name2=name
               if dict_mac.has_key(name2) == False:
                   l=[]
                   dict_mac[name2]=l
               l1=dict_mac[name2]
               l1.append(macs)             
               dict_mac[name2]=l1 
            l1=[]
        for final_name,list_mac in dict_mac.items() :  
            if final_name.startswith("cliente"):
                icon=wired_icon           
                self.reg_store.append([icon, final_name, get_ip_by_hostname(final_name), list_mac])
            if final_name.startswith("impresora"):
                icon=printer_icon           
                self.reg_store.append([icon, final_name, get_ip_by_hostname(final_name), list_mac])
            #self.reg_store.append([icon, name, get_ip_by_hostname(name), l])
            #self.reg_store.append([icon, name, get_ip_by_hostname(name), macs])
                
    def register_computer(self, name, macs):
        # Hay que registrar todas las macs de la lista
        if name.startswith("impresora"):
            if ldap_add_client(name, macs):
               self.populate()
               return True
        else:
            for m in macs:
	        if client_exists(name):
                    new_client_num=name
                    while client_exists(new_client_num) == True:
                        new_client_num=get_new_client_name(name)
                    ldap_add_client(new_client_num, m)
                else:
                    ldap_add_client(name, m)
            self.logger.info('New computer registered %s' % name)
            self.populate()

    def delete_computer(self, name):
        l=get_client_mac_list_registered(name) # Devuelve las MACS registrdas con el nombre
        for mac in l:
            if hwmacadd_exists(mac):
                name_hwmac=get_client_name(mac)               
                ldap_delete_client(name_hwmac)
                self.logger.info('Deleted computer %s' % name_hwmac)
        self.populate()

    def update_name(self, old_name, new_name):
        update_client_name_ldap(old_name, new_name)
        self.logger.info('Renamed computer %s to %s' % (old_name, new_name))
        self.populate()

    def reg_tv_button_press_event_cb(self, reg_tv, event):
        if event.button == 3:
            self.reg_menu.popup(None, None, None, event.button, event.time)

    def unreg_iv_button_release_event_cb(self, reg_tv, event):
        selection = self.unreg_iv.get_item_at_pos(int(event.x), int(event.y))
        print "DEBUG Selection: ",selection
        if selection:
            selected = self.unreg_store[selection[0]]	
            print "DEBUG SELECTED ",selected 
            print "selected[ICON_COL] ", selected[ICON_COL] 
            print "selected[NAME_COL] ", selected[NAME_COL]
            print "selected[IP_COL] " ,selected[IP_COL] 
            print "selected[ALLMACS_COL]" ,selected[ALLMACS_COL]  
            # Add printer
            if selected[ICON_COL] == printer_icon:
                themac = getoutput('arping -f -w 10 '+selected[IP_COL]+'|grep reply|awk \'{print $5}\'').strip('[[,]]')
                self.printer_mac_entry.set_text(themac)
                self.printer_mac_entry.set_sensitive(False)
                self.available_store.clear()
                for item in [x for x in available_printers if not x in get_clients_registered().keys()]:
                    self.available_store.append([item])
                if not hwmacadd_exists(themac):
                    response = self.printer_dialog.run()
                    if response == gtk.RESPONSE_OK and self.printer_name_box.get_active_text():
                        if self.register_computer(self.printer_name_box.get_active_text(), self.printer_mac_entry.get_text()):
                            self.notify(title=_('Control de Puestos'),text='La impresora se ha registrado, apague y enciandala para que los cambios surtan efecto', icon='commiecc', urgency=1) 
                    self.printer_dialog.hide()
                    return
                else:
                    dialog_just_printer_added = gtk.MessageDialog(parent = None,
                        flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        type = gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_OK,
                        message_format = 'Registro de impresoras')
                    dialog_just_printer_added.format_secondary_text('Parece que esta impresora está ya añadida, apáguela y vuélvala a encender')
                    if dialog_just_printer_added.run() == gtk.RESPONSE_OK:
                        dialog_just_printer_added.destroy()
                        return

            # Add computer         
            self.name_lbl.set_text(selected[NAME_COL])
            self.ip_lbl.set_text(selected[IP_COL])

            self.available_store.clear()
            for item in [x for x in available_computers if not x in get_clients_registered().keys()]:
                self.available_store.append([item])
        
            response = self.edit_dialog.run()
            if response == gtk.RESPONSE_OK:
                #TODO: Check if computer still alive before continue
                if self.name_box.get_active_text():
                    try:
                        print selected
                        print type(selected[NAME_COL])
                        cadena_macs= selected[ALLMACS_COL]
	                print "DEBUG CADENA MACS",cadena_macs
                        list_macs=cadena_macs.split(";")
                        for mac in list_macs:
                            if hwmacadd_exists(mac):
                                print "Operacion de duplicacion no permitida"
                            else:
                                self.register_computer(self.name_box.get_active_text(),
                            list_macs) #ADRIAN:Aqui se debe pasar una lista de mac             
                 
                            def cb(result):
                                if not result:
                                    self.logger.error('Cant request renewal to %s' \
                                        % row[NAME_COL])                       
                            do_work('renewal', selected[NAME_COL], 8000, [], 5, cb)
                    except:
                        print "Excepcion"
                try:
                    self.notify(title=_('Control de Puestos'),text='El equipo se ha registrado, deberá reiniciarlo para que el registro se complete en el equipo.', icon='commiecc', urgency=1)
                except:
                    print "Notify Exception"

            self.edit_dialog.hide()
       
    def edit_menuitem_activate_cb(self, menuitem, data=None):
        selection = self.reg_tv.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:

            #TODO: Add printer editing
            if selected[ICON_COL] == printer_icon:
                return

            row = model[selected]
            self.name_lbl.set_text(row[NAME_COL])
            self.ip_lbl.set_text(row[IP_COL])

            self.available_store.clear()
            for item in [x for x in available_computers if not x in get_clients_registered().keys()]:
                self.available_store.append([item])
        
            response = self.edit_dialog.run()
            if response == gtk.RESPONSE_OK:
                #TODO: Check if computer still alive before continue
                if self.name_box.get_active_text():
                    if row[ICON_COL] == wired_icon:
                        def cb(result):
                            if not result:
                                self.logger.error('Cant request renewal to %s' \
                                    % row[NAME_COL])
                        do_work('renewal', row[NAME_COL], 8000, [], 5, cb)
                            
                    self.update_name(row[NAME_COL], 
                        self.name_box.get_active_text())

            self.edit_dialog.hide()

    def remove_menuitem_activate_cb(self, menuitem, data=None):
        selection = self.reg_tv.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:
            row = model[selected]

            #Aqui tenemos que republicar
            def cb(result):
                if not result:
                    self.logger.error('Cant request renewal to %s' % row[NAME_COL])
            client_name = row[NAME_COL]
            do_work('renewal', row[NAME_COL], 8000, [], 5, cb)
            self.delete_computer(client_name)

    def name_box_changed_cb(self, combobox, data=None):
        active = combobox.get_active_text()
        if active:
            self.name_lbl.set_text(active)
            self.ip_lbl.set_text(get_ip_by_hostname(active))    
    
    def discovered(self, dispatcher, slave):
        try:
    
            print 'Nuevo Equpo Descubierto. Direccion MAC ACTIVA:  %s ' %slave.hwaddr
            print 'Nombre del equipo descubierto %s' %slave.host
            print 'IP del nombre descubierto %s' %slave.address
            print 'Lista de MACS del equipo',slave.macs
    
    #        self.notify(title=_('Control de Puestos'), text='Se ha descubierto un equipo NO REGISTRADO con mac: %s' % slave.macs, icon='commiecc', urgency=1)
    
            # Tenemos que ir guardando los clientes avahi en una lista e ir comprobando que si estan registrados 
            # Si hay incongruencias se debe reiniciar 
            
            if slave.host.startswith("sin-registrar"):
                print "EL EQUIPO COMIENZA CON SIN-REGISTRAR"
                self.logger.info(" El equipo comienza con sin-registrar, se manda a reiniciar %s " % slave.host)
                do_work('reboot', slave.host, slave.port)
            
            list_macs=slave.macs.split(";")
            #print list_macs
            bol=False
            for mac in list_macs:
                self.dict_avahi[mac]=slave.host
                if hwmacadd_exists(mac):
                    bol=True
                else:
                    bol=False
            #Si bol= True quiere decir que todas las MACS del equipo registrado se encuentran registradas
            if bol == True: 
                ldap_slave_name=get_client_name(slave.hwaddr)
                print 'Nombre extraido del LDAP para la MAC: %s ' % ldap_slave_name
                print 'Nombre pasado en el descubrimiento: %s' % slave.host
                # Si estan registradas hay que ver si concierdan, para si no, reiniciar.
                for mac_avahi,client_avahi in self.dict_avahi.items():
                    if hwmacadd_exists(mac_avahi): 
                        name_ldap=get_client_name(mac_avahi)
                        if client_avahi.startswith("cliente") == False:
                            if client_avahi.startswith("impresora")==False:
                                #print "El cliente tampoco comienza como impresora"
                                print "Debug REINICIAR"  
                                self.logger.info(' Deberia mandarse a reiniciar el cliente %s:' % slave.host)
                                self.logger.info(' REBOOT-DEBUG %s: La mac está registrada pero el hostname no es ni del tipo cliente-x ni impresora-x' % (slave.host))
                                #do_work('reboot', client_avahi, slave.port)
                            else:
                               print "El cliente es una impresora"
                               #TODO repasar el tema de impresoras
                        elif client_avahi.startswith("cliente")==True: 
                            p=client_avahi.split(".")
                            client_avahi=p[0]
                            #Se supone que la informacion en le ldap estara correcta   
                            #pasamos a quitar el ultimo digito 
                            if client_avahi[-1].isalpha()== True:
                                client_avahi=client_avahi.strip(client_avahi[-1])
                            if name_ldap[-1].isalpha()== True:
                                name_ldap=name_ldap.strip(name_ldap[-1])
                            if client_avahi != name_ldap:                        
                                print "Comparacion entre " ,client_avahi ," y " + name_ldap 
                                print "DEBUG REINICIAR"
                             #   print "DEBUG: Nombre cliente avahi ", client_avahi
                                self.logger.info(' Deberia mandarse a reiniciar el cliente %s:' % slave.host)
                                self.logger.info(' REBOOT-DEBUG %s: La mac está registrada pero el avahi hostname %s no coincide con el del LDAP: %s' % (slave.host, client_avahi, name_ldap))
                                #do_work('reboot', client_avahi, slave.port)
                      
            elif bol==False:                  
                print "Alguna de las MACS no se encuentran registradas"
            #    self.notify(title=_('Control de Puestos'), text='Se ha descubierto un equipo NO REGISTRADO con mac: %s' % slave.macs, icon='commiecc', urgency=1)
                # Aqui se mandaria el mensaje de "Tiene equipos sin registrar"
    #            try:
    #                self.notify(title=_('Control de Puestos'),text='Existen equipos sin registrar', icon='commiecc', urgency=1)
    #            except e:
    #                print "Excepcion en el notify",e
                self.unreg_store.append([wired_icon, slave.host, slave.address,slave.hwaddr,slave.macs])
                self.logger.info(" Element added ");
                if slave.host.startswith("cliente") and not slave.host.startswith("cliente-live"):
                    print ("NO registrado y empiza como cliente, reiniciar!")
                    self.logger.info(' Deberia mandar a reiniciar el cliente %s:' % slave.host)
                    self.logger.info(' REBOOT-DEBUG %s: La mac no está registrada pero sin embargo su hostname es %s ' % (slave.host, slave.host))
#                    do_work('reboot', slave.host, slave.port)

            for item in self.reg_store:
                print 'Equipo registrado, nombre: %s ' %item[NAME_COL]
                print 'Equipo registrado, MAC: %s ' %item[MACS_COL]
            for item in self.unreg_store:
                print 'Equipo NO registrado, nombre %s ' %item[NAME_COL]
                print 'Equipo NO registrado, MAC %s ' %item[MACS_COL]
        except Exception, e:
            print e

    def losed(self, dispatcher, slave):
        for item in self.reg_store:
            if item[NAME_COL] == slave.host:
                item[ICON_COL] = offline_icon
                return
        
        for item in self.unreg_store:
            if item[NAME_COL] == slave.host:
                self.unreg_store.remove(item.iter)

    def printer_discovered(self, discoverer, printer):
        print 'Nueva IMPRESORA descubierta. Direccion MAC ACTIVA:  %s ' % printer['mac']
        print 'Nombre de la impresora %s' % printer['host']
        print 'IP de la impresora %s' % printer['address']

        for item in self.reg_store:
            if item[NAME_COL] == printer['host']:
                return

        for item in self.unreg_store:
            if item[NAME_COL] == printer['host']:
                return

        if not hwmacadd_exists(printer['mac']):
            self.unreg_store.append([printer_icon, printer['host'], printer['address'], '',''])

    def printer_losed(self, discoverer, printer):
        for item in self.unreg_store:
            if item[NAME_COL] == printer['host']:
                self.unreg_store.remove(item.iter)


