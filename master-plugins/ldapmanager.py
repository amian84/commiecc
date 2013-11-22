# -*- coding: utf-8 -*-
#
# Authors : Adrian Belmonte  <abelmonte@emergya.es>
#
# Copyright (c) 2008, Emergya Consultoria
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import os
import ldap
import re
import string


CONFFILE = '/etc/ldap/ldap.conf'
HOST= '172.26.1.1'
BASE= 'o=guadalinex,c=es'

#
#       Devuelve un diccionario de parejas nombre:MAC pasado una lista de busqueda ldap 
# 
#       IN: Lista de busqueda ldap
#       OUT: Dict parejas nombre:Mac
#


def get_hwdict (list_ldap):
    """
    get_hwdict(IN:list): Get hardware address dictionary: Returns a dicta [Client_name: MAC_Address] from a given ldap search list result
    OUT: dict (Client_name:MAC_addr)

    """      
    dic_ret={}
    #print "List_ldap"
    #print list_ldap

    # En un primer lugar, tenemos que sacar el valor que nos interesa
    n= len(list_ldap)
        
    if n != 0:
        for i in range (0,n):   
            tup=list_ldap[i]
            dic=tup[1]
            #print "Diccionario "
            #print dic
            if dic.has_key('dhcpHWAddress'):
                list_cn=dic['cn']
                list_dhcp=dic['dhcpHWAddress']
                # La lista es del tipo: cn : ['puesto1'] dhcpHWAddress: ['ethernet 00:0c:29:e9:2d:c8']

                div_cn=split_list(list_cn)
                div_dhcp=split_list(list_dhcp)

                # Nos quedara algo como [ ["puesto1"] y [("ethernet", "00:0c:29:e9:2d:c8"]]

                name=div_cn[0];
                #print name 
                #print div_dhcp[1]
                dic_ret[name]=div_dhcp[1]

    return dic_ret

def get_hwlist(list_ldap):
    list_ret=[]
    n=len(list_ldap)
#    print list_ldap
    if(n!= 0):
        for i in range (0,n):
            tup=list_ldap[i]
            dic=tup[1]
            if dic.has_key('dhcpHWAddress'):
                list_dhcp=dic['dhcpHWAddress']      
#                print list_dhcp
                div_dhcp=split_list(list_dhcp)
                list_ret.append(div_dhcp[1])
                print list_ret

    return list_ret         
                

#
#       Divide una lista de cadenas en una lista de cadenas sin espacios 
#       
#       IN: Lista[str]
#       OUT: Lista de cadenas
#
#


def split_list(list_div):
    """
    split_list(IN:list): Split a given list 
    OUT:list 
    
    """

    space = re.compile("\s*")

    for str in list_div:
        l_div= space.split(str)
    return l_div


#
#       Modifica el cliente seleccionado realizando las operaciones en el ldap
#
#       IN:     cliente_name: Nombre del cliente
#               cliente_hwmac: Mac del cliente
#       
#   Out:    ret -  Booleano, devuelve True si la operacion fue correcta, False en CC
#

def update_hwmac_ldap (cliente_name,cliente_hwmac):
    """
    update_ldap (IN:str, str): Modifies selected client in ldap whit the specified MAC address
    OUT: True if correct, Exception if Error
    """
    #En clase se puede usar l como variable de clase, no hace falta hacer bind de nuevo
    cliente_id= "cn=%s,cn=Puestos,cn=base,ou=dhcp,ou=servicios,o=guadalinex,c=es" % cliente_name
    l = ldap.open(HOST)
    try:
        l.protocol_version = ldap.VERSION3
        username =  "cn=admin,o=guadalinex,c=es"
        password  = "wadA15"
        l.simple_bind(username, password)
        cadena= "ethernet %s" %cliente_hwmac
        l.modify_s(cliente_id, [(ldap.MOD_REPLACE,'dhcpHWAddress', cadena)])
        print "Modificacion en LDAP realizada correctamente"
        l.unbind()
        return True
    except ldap.LDAPError, error:
        l.unbind()
        print "Error al modificar en el LDAP",error


def check_correct_mac(hwmac):
    """
    check_correct_mac(IN:str): Check if a MAC is in a correct Format [XX:XX:XX:XX:XX:XX]
    OUT: Boolean
    """
    x='^[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}$'
    #x = '([a-fA-F0-9]{2}[:]?){6}' # regex para direccion MAC
    #c = re.compile(x).finditer(hwmac)
    prog=re.compile(x)
    c= prog.match(hwmac)
    if c:
        print "La MAC suministrada es correcta"
        return True
    else:
        print "La MAC suministrada es incorrecta"
        return False


#
#       Dado un cliente y una Mac, se comprobara si existe dicho cliente y se modificara en consecuencia
#
#       IN:     cliente - String
#               hwmac- String 
#               
#       OUT:    ret- Boolean
#                        
#                       -
#

def modify_client_hwmac (client,hwmac):
    """
    modify_client(IN:string, string):  Modify the mac for a given client name
    OUT:  Boolean
    """  

    ret=False
    ret=check_correct_mac(hwmac)  #TODO: lanzamiento de excepciones 
    dict=get_clients_registered()
    if ret:
        if (dict.has_key(client)):
            update_hwmac_ldap (client,hwmac)
            print "Actualiza realizado correctamente"
            #dict[cliente]=hwmac     #Actualizamos la lista  
            ret=True;
        else:
            print "El cliente no existe"
    return ret

#
#   Devuelve verdadero si la MAC existe en un diccionario determinado
#   IN: hwmac: Dirreccion MAC
#       
#
#   OUT: Booleano: True si lo encuentra False en CC
#
#

def hwmacadd_exists(hwmac):
    
    # Se podria llamar a get_hwdict para obtener una lista actualizada, q se pase como parametro
    # o bien si usamos una clase, llamarla como parametro de la clase, vamos a implementar el mas 
    # general
    """
    hwmacadd_exists(IN: MAC_add (str)) Check if a MAC address exists in ldap
    OUT: Boolean
    """

    dict=get_clients_registered()
    for k in dict.itervalues():
        if (k == hwmac):
#            print "Valor existe en la lista"
            return True
    print "El valor de hwmac no existe en la lista"
    return False

#
#   Comprueba si un cliente existe en el LDAP
#
#


def client_exists(client_name):
    """
    client_exists(IN: client_name(str)) Check if a Client name exists in ldap
    OUT: Boolean
    """
    dict=get_clients_registered()
    if dict.has_key(client_name):   
        return True
    else:
        return False


#
#   Devuelve el cliente de un hwmac 
#
#   IN: hwmac : Direccion MAC a buscar
#       dict: Diccionario que contiene pares direccion:nombre cliente
#
#   OUT: client_name: Nombre del cliente al que se corresponde o cero en caso de que no encuentre el valor 
#           
#

    
def get_client_name(hwmac):
    """
    get_client_name(IN: MAC_addres(str)) returns client name for a given MAC Address
    OUT: client_name (str)
    """
    dict=get_clients_registered()
    if hwmacadd_exists(hwmac):
        for k,v in dict.iteritems():
            if (v==hwmac): 
                return k
    else:
        return False

#
#   Devuelve un nombre nuevo para un nombre de cliente para el caso de que se encuentre ocupado
#   el nombre nuevo sera el nombre del cliente con el numero mas a,b,c...
#   Si llega hasta la 'z' devolvera un mensaje de error
#   
#   IN: cliente_numero (str) : Nombre a cambiar
#   
#   OUT: nuevo nombre no ocupado o cadena "Error"
#



def get_new_client_name(cliente_numero):
    """
    get_new_client_name(IN: client_name (str): Change client name for a new one 
    OUT: new client_name 
    """
    #Es necesario implementar que si el parametro que le llega acaba en a-z 
    #lo elimine y haga lo suyo
    if re.match("(.+)[a-z]$",cliente_numero):
        cliente_numero=cliente_numero[:-1] 
    
    for c in string.lowercase:
        cliente_numero_letra=cliente_numero+c
        if client_exists(cliente_numero_letra)== False:                 
            print "Nuevo valor valido: " +cliente_numero_letra
            return cliente_numero_letra
    return "Error"


#
#   Anade cliente al LDAP
#   IN:     cliente (str):Nombre del cliente a anadir  
#       hwmac (str):  MAC a anadir
#   OUT:    True si es correcto, excepcion en cc
#

# Anade un cliente al ldap: dentro de la funcion te pedira el nombre que quieres asignarle al cliente host
# el resto de la inforacion: MAC (la suministrada) y hostname,que vendra dado por el nombre del cliente
# Es necesario para asignarlo que se compruebe que el nombre del cliente exista y en ese caso se le anadira a,b,c,d...
# hasta que haya un clientex que no exista


def ldap_add_client(cliente,hwmac):
    """
    ldap_add_client(IN: str,str): Addd a client with the MAC address given
    OUT: true if correct, exception if not 
    """
    config_dic=get_config_info()
    l=ldap.open(HOST)

    try:
        # Establecemos la version LDAP 
        l.protocol_version = ldap.VERSION3
        l.simple_bind ("cn=admin,o=guadalinex,c=es","wadA15")
        
        #base= config_dic['base']
        base=BASE
    except:
        print "Error al acceder al LDAP"
        l.unbind()
        return False

    path= "cn=Puestos, cn=base, ou=dhcp, ou=servicios, o=guadalinex,c=es"

    client_info= {
        'dhcpHWAddress':' ',
        'objectClass': ('top','dhcpHost'),
        'dhcpStatements':' ',
        'cn': ' ',
        }
    client_info['dhcpHWAddress']= 'ethernet '+hwmac
    client_info['cn']= cliente;
    
    if re.match("(.+)[a-z]$",cliente):
        clienteb=cliente[:-1]
        client_info['dhcpStatements']='fixed-address ' + clienteb 
    else:
        client_info['dhcpStatements']='fixed-address ' + cliente

    id='cn=' +cliente +', ' +path
    attributes=[ (k,v) for k,v in client_info.items() ]
    try:
        l.add_s(id,attributes)
        l.unbind() 
        return True
    except ldap.LDAPError, error:
        print 'problem with ldap',error
        l.unbind()


#
#   Borra un cliente del LDAP
#
#   IN: Nombre del cliente
#
#   OUT: Excepcion si falla, 0 en caso de que funcione
#
#




def ldap_delete_client (client_name):
    """
    ldap_delete_client (IN: str): delete a ldap entry given by its client name
    OUT: True if ok, exception if fails
    """

    path="cn=Puestos, cn=base, ou=dhcp, ou=servicios, o=guadalinex,c=es"
    config_dic=get_config_info()
    l=ldap.open(HOST)

    try: 
        # Establecemos la version LDAP 
        l.protocol_version = ldap.VERSION3
        l.simple_bind ("cn=admin,o=guadalinex,c=es","wadA15")
    except:
        print "Error al acceder al LDAP"
        l.unbind()
        return False

    # base= config_dic['base']
    base=BASE
    path= "cn=Puestos, cn=base, ou=dhcp, ou=servicios, o=guadalinex,c=es"
    
    delete_cn= 'cn='+client_name+', '+path
    try:
        l.delete_s(delete_cn)
        return 0
    except ldap.LDAPError, error:
        print 'problem with ldap',error
    
    l.unbind()
    
#   Lee el archivo de configuracion. Devuelve una diccionario con el valor leido 
#   
#   IN: NONE
#   
#   OUT: diccionario con dos entradas URI y BASE leidas desde el archivo de config.
#
#



def get_config_info():
    """
    get_config_info: reads config file
    OUT: dict with base and uri entries
    """
    dic= {}
    dic['base'] = ""
    dic ['uri'] = ""
    space = re.compile("\s*")
    args = open(CONFFILE).readlines()
    for line in map(str.strip, args):
        var  = space.split(line)
        n= len(var)
        if n==2:
            if var[0].upper() == "BASE":
                dic['base']= var[1]
                #print dic['base']
                
            if var[0].upper() =="URI":
                dic['uri']=var[1]
                #print dic['uri']
    return dic




# 
#   Lista clientes e impresoras registradas en el ldap, busca las cadenas cliente * e impresora* 
#   si se introdujera un valor habria de ser modificada la busqueda 
#
#   IN: NONE
#   OUT: dict con todos los clientes: Nombre:MAC
#
#

def get_clients_registered():
    """
    get_clients_registered: get clients and printers from ldap
    OUT: dict [name:hwmac]
    """
    dict_ret={}
    config_dic=get_config_info()
    l=ldap.open(HOST)
#    print config_dic
    try:
        # Establecemos la version LDAP 

        l.protocol_version = ldap.VERSION3
        l.simple_bind ("cn=admin,o=guadalinex,c=es","wadA15")

        # Ejemplo de la busqueda, todos los apellidos que empiecen por "a"
        # l.search_s(path,ldap.SCOPE_SUBTREE,'sn='+'a*')
        # aqui vamos a busar todos los puestos
    
        #   base= config_dic['base']
        base=BASE

        #list_puestos=l.search_s(base,ldap.SCOPE_SUBTREE,'cn='+ 'puesto*')
        list_puestos=l.search_s(base,ldap.SCOPE_SUBTREE,'cn='+ 'cliente*')
        list_impresoras= l.search_s(base,ldap.SCOPE_SUBTREE,'cn='+ 'impresora*')
        l.unbind()
    except: 
        print "Error al acceder al LDAP"
        l.unbind()
        return dict_ret

    dic_puestos = get_hwdict(list_puestos)
    dic_impresoras = get_hwdict(list_impresoras)

    dic_total=dic_puestos
    
    for k,v in dic_impresoras.iteritems():
        dic_total[k]=v

    return dic_total

#Devuelve un diccionario  [cliente:lista de macs asociadas a cliente en ldap]
#para ello hay que realizar la busqueda cliente2* (o impresora2*) e ir anadiendo
# las macs a la lista

def get_client_mac_list_registered(client_name):
    
    config_dic=get_config_info()
    l=[]
    l=ldap.open(HOST)
    try: 
        # Establecemos la version LDAP 
        l.protocol_version = ldap.VERSION3
        l.simple_bind ("cn=admin,o=guadalinex,c=es","wadA15")
    except:
        print "Error al acceder al LDAP"
        l.unbind()
        return l 
    # Ejemplo de la busqueda, todos los apellidos que empiecen por "a"
    # l.search_s(path,ldap.SCOPE_SUBTREE,'sn='+'a*')
    # aqui vamos a busar todos los puestos
    
    # base= config_dic['base']
    base=BASE
    s=str(client_name)  
    list_puestos=[]
    search_pattern='cn=' + s 
    ls1=l.search_s(base,ldap.SCOPE_SUBTREE,search_pattern)
    if len(ls1)>0:
        for item1 in ls1:
            list_puestos.append(item1)

    for char in string.lowercase:
        search_pattern='cn=' + s + char
        ls=l.search_s(base,ldap.SCOPE_SUBTREE,search_pattern)
        if len(ls) > 0:
            for item in ls:
                list_puestos.append(item)

    l.unbind()

# Metodo antiguo
#    search_pattern='cn=' + s + '*' 
    
    
    #list_puestos=l.search_s(base,ldap.SCOPE_SUBTREE,'cn='+ 'puesto*')
#    list_puestos=l.search_s(base,ldap.SCOPE_SUBTREE,search_pattern)


    # Tenemos la consulta al ldap con el patron del cliente, veremos que 
    # Pasamos a guardar en una lista todas las direcciones mac   
    

    list=get_hwlist(list_puestos)
    return list

def update_client_name_ldap(old_name,new_name):
    if client_exists(new_name):
        print "El nombre destino ya existe. Elija otro"
        return False
    elif client_exists(old_name)==False:
        print "El cliente no existe"
        return False
    else:
        l = ldap.open(HOST)
        try:        
            l.protocol_version = ldap.VERSION3
            username =  "cn=admin,o=guadalinex,c=es"
            password  = "wadA15"
            base=BASE
            l.simple_bind(username, password)
            s=str(old_name)
            search_pattern= 'cn='+old_name + '*'
    
            list_puestos=l.search_s(base,ldap.SCOPE_SUBTREE,search_pattern)
            id_old= "cn=%s,cn=Puestos,cn=base,ou=dhcp,ou=servicios,o=guadalinex,c=es" % old_name
            n=len(list_puestos)
            if n==1:
                #Si n es igual a 1, no es necesario entrar en el bucle
                #simplemente cambiamos un valor por otro
                # Hacemos la disticion por comodidad y por eficacia
            
                id_new= "cn=%s,cn=Puestos,cn=base,ou=dhcp,ou=servicios,o=guadalinex,c=es" % new_name
                cn_new="cn=%s" % new_name
                #LDAPObject.modrdn_s(dn, newrdn [, delold=1)
                try:
                    #l.modrdn_s(id_old,id_new)
                    l.modrdn_s(id_old,cn_new)
                    #Actualizamos la entrada al cn correspondiente
                    l.modify_s(id_new, [(ldap.MOD_REPLACE,'cn', new_name)])
                    #Actualizamos el dhcpStatements
                    new_statement= "fixed-address "+ new_name
                    l.modify_s(id_new, [(ldap.MOD_REPLACE,'dhcpStatements', new_statement)])

                except ldap.LDAPError,error:
                    print "Error",error
            else:
                for i in range (1,n):
                    name= get_new_client_name(new_name)
                    new_path= "cn=%s,cn=Puestos,cn=base,ou=dhcp,ou=servicios,o=guadalinex,c=es" % name
                    cn_new_path="cn=%s"%name
                    l.modrdn_s(id_old,cn_new_path)         
                    #Actualizamos la entrada al cn correspondiente
                    l.modify_s(new_path, [(ldap.MOD_REPLACE,'cn', name)])
                    #Actualizamos el dhcpStatements
                    new_statement2= "fixed-address "+ name
                    l.modify_s(new_path, [(ldap.MOD_REPLACE,'dhcpStatements', new_statement2)])
                    return True
            l.unbind()                
        except ldap.LDAPError, error:
            print "Error al modificar en el LDAP",error
            l.unbind()

#
# Comprueba si dada una lista de clientes, alguno de ellos se encuentra registrado
# esa lista, es la que envia un equipo al conectarse con todas sus macs
#
#


def check_list_onldap(list_mac):

    dict={}
    list_registered=[]
    list_unregistered=[]

    for mac in list_mac:
        if hwmacadd_exists(mac):
            #TODO: Pdodia pasar que distintas macs tuvieran distinto nombre de cliente
            #se tendrian que comprobar coherencias y conflictos  en el ldap
            list_registered.append(mac)
        else:
            list_unregistered.append(mac)
    dict['registered']=list_registered
    dict['unregistered']=list_unregistered
    return dict
            
# Comprueba si para una mac recibida el cliente concuerda con la version actual del ldap
# puede ser que cuando se reciba un dato puede tener la mac correcta, pero un cliente diferente
# podemos dejarlo en stand-by de moment0
#
#def check_mac_client_coherence(client,mac)
#   if check_correct_mac(mac) == False:
#       print " Formato incorrecto de MAC"
#       return False
#   if client_exists(client) == False:
#       print "Cliente No existe"
#       return False    
#   mac_ldap=
#


"""
    numero= raw_input(" Numero de cliente para asignar la direccion MAC?: ")
    cliente_numero= "puesto"+numero
    if (client_exists(cliente_numero)):
        print "Cliente ya registrado. Buscando nuevo numero"
        nuevo_cliente= get_new_client_name(cliente_numero)
        if nuevo_cliente != "Error":
            print "Se intentara anadir el cliente " + nuevo_cliente
            add_client(nuevo_cliente,mac)

"""



"""

## Caso practico, recibimos un par Cliente,mac, por ejemplo 
#Sacado de un diccionario {Cliente:[Lista de MACS]}


######## Una MAC registrada otra no #######
#avahi_client="guadalinfoclientv6-345"
#mac_list=["00:11:22:33:44:55","22:33:44:55:66:77"]
#########

####### Ninguna MAC registrada ########
avahi_client="guadalinfoclientv6-345"
mac_list=["99:88:21:33:44:51","22:31:44:55:66:77"]
########

###### Ambas MAC registradas #########
#avahi_client="guadalinfoclientv6-345"
#mac_list=["00:11:22:33:44:55","00:0c:29:ea:2d:c8"]
######


# Ordenamos las listas en registrados y no registrados

dict_ldap_mac=check_list_onldap(mac_list) 

# tenemos 3 posibilidades: Que todos las macs esten registradas (lista unregistered vacia)
# que ninguna mac se encuentre registrada (lista registered vacia) 
# o que haya de ambos

list_registered = dict_ldap_mac['registered']
list_unregistered = dict_ldap_mac['unregistered']

if len(list_registered) == 0:
    # No existe ningua MAC registrada en ese equipo
    print "Todas las macs para ese equipo se encunentran sin registrar"
    # Llamamos a la funcion mostrar_en_no_registrados(list_unregistered,avahi_client,"NONE")
    # 'NONE' se rellenara con el nombre de cliente si existe alguna mac en la lista registrada
    print "No registrados"
    print list_unregistered
    
    client_n=raw_input(" Numero de cliente para asignar a los nuevos equipos:  ")
    cliente_numero= "cliente-"+client_n
    if client_exists(cliente_numero)==True:
        print "El cliente existe " 
    else:
        for mac in list_unregistered:
            if client_exists(cliente_numero)==True:
                new_client_num=cliente_numero
                while client_exists(new_client_num) == True:
                    new_client_num=get_new_client_name(cliente_numero)
                ldap_add_client(new_client_num,mac)
            else:
                ldap_add_client(cliente_numero,mac)

elif len(list_unregistered) == 0:
    print "Todas las macs para este equipo se encuentran registradas"
    # Sacamos el nombre del cliente al que pertenecen, deben pertenecer todos al mismo 
    
    # TODO: COMPROBAR COHERENCIA DEL LDAP haciendo una funcion que compruebe que todos los 
    #Elementos de la lista pertenezcan al mismo cliente

    mac=list_registered[0]
    client_name= get_client_name(mac)
    print "Se llama a la funcion para mostrar en registrados"
    # Llamar a mostrar_en_registrados(list_registered,client_name)
    print "Registrados"
    print list_registered
else:  
    mac=list_registered[0]
    client_name= get_client_name(mac)
    print "Se mostraran en 'registrados' los registrados: "
    print list_registered
    # Llamada a la funcion mostrar_en registrados(list_registered,client_name)
    print "Los no registrados se mostraran en 'no registrados: "
    print list_unregistered
    resp= raw_input(" Desea registrar  los no registrados?: ")
    if resp=='s':
        for mac in list_unregistered:
            if client_exists(client_name)==True:
                new_client_num=client_name
                while client_exists(new_client_num) == True:
                    new_client_num=get_new_client_name(client_name)
                ldap_add_client(new_client_num,mac)
            else:
                ldap_add_client(cliente_numero,mac)


        
    #llamada a la funcion mostrar_en_no_registrados(list_unregistered,avahi_client,client_name)
    # Esta vez podemos incluir un nombre de cliente por defecto
 
#Probar con ninguna mac registrada (OK) (arriba)
#Probar con todas los macs registrados (OK) (arriba)

    
## Prueba de anadir cliente: 
## anadir cliente con una mac(OK)
#ldap_delete_client("cliente10001")
#ldap_delete_client("cliente10002")
#ldap_delete_client("cliente10003")

#ldap_delete_client("cliente8833a")
#ldap_delete_client("cliente33a")
#ldap_delete_client("cliente10001")

#ldap_add_client("cliente10001","00:01:20:22:33:66")

## anadir cliente ya registrado, es decir varias macs asociados: Deberia aádir con cliente1a, cliente1b... 




#Borrar cliente (OK)
#ldap_delete_client("cliente10001")



##Prueba de update_cliet_name simple (OK)

#update_client_name_ldap("cliente50","cliente55")


## Prueba cliente subsecuentes: deberia cambiar los subsecuentes

"""
