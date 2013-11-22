#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, platform
import glob
import subprocess

from distutils.core import setup
from distutils.command.build import build
from distutils.command.install_data import install_data
from distutils.log import warn, info, error, fatal
from distutils.dep_util import newer


# Get current Python version
python_version = platform.python_version_tuple()

# Setup the default install prefix
prefix = sys.prefix

# Check our python is version 2.6 or higher
if python_version[0] >= 2 and python_version[1] >= 6:
    ## Set file location prefix accordingly
    prefix = '/usr/local'

# Get the install prefix if one is specified from the command line
for arg in sys.argv:
    if arg.startswith('--prefix='):
        prefix = arg[9:]
        prefix = os.path.expandvars(prefix)

infile = open(os.path.join('commiecc', 'conf.py.in'))
data = infile.read().replace('@PREFIX@', prefix)
infile.close()

outfile = open(os.path.join('commiecc', 'conf.py'), 'w')
outfile.write(data)
outfile.close()

PO_DIR = 'po'
MO_DIR = os.path.join('build', 'mo')

class BuildData(build):
    def run (self):
        build.run (self)

        for po in glob.glob (os.path.join (PO_DIR, '*.po')):
            lang = os.path.basename(po[:-3])
            mo = os.path.join(MO_DIR, lang, 'commiecc.mo')

            directory = os.path.dirname(mo)
            if not os.path.exists(directory):
                info('creating %s' % directory)
                os.makedirs(directory)

            if newer(po, mo):
                info('compiling %s -> %s' % (po, mo))
                try:
                    rc = subprocess.call(['msgfmt', '-o', mo, po])
                    if rc != 0:
                        raise Warning, "msgfmt returned %d" % rc
                except Exception, e:
                    error("Building gettext files failed.  Try setup.py \
                        --without-gettext [build|install]")
                    error("Error: %s" % str(e))
                    sys.exit(1)

class InstallData(install_data):
    def run (self):
        self.data_files.extend (self._find_mo_files ())
        install_data.run (self)

    def _find_mo_files (self):
        data_files = []

        for mo in glob.glob (os.path.join (MO_DIR, '*', 'commiecc.mo')):
            lang = os.path.basename(os.path.dirname(mo))
            dest = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
            data_files.append((dest, [mo]))

        return data_files


setup(
    name='CommieCC',
    version='0.1alpha',
    description='Classroom controller',
    long_description='A plugin-able slave-master application for managing a computer classroom',
    author='J. Félix Ontañón',
    author_email='felixonta@gmail.com',
    url='https://launchpad.net/commiecc',

    classifiers=[
        'Development Status :: 0.1 - Alpha',
        'Environment :: Desktop Environment',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License (GPL)'
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Desktop Environment :: Gnome',
        'Topic :: Utilities'],
    
    keywords = ['classroom', 'control', 'master', 'slave', 'plugin'],
    requires = ['PyGTK', 'dbuspython'],

    packages = ['commiecc', 'commiecc.classcontrol', 'commiecc.masterlib',
                'commiecc.slavelib', 'commiecc.common'],
    package_dir = {'commiecc': 'commiecc'},
    
    scripts = ['commiecc-screen-locker', 'commiecc-slave', 
                'commie-class-control', 'commiecc-slave-desktop'],
    
    cmdclass={'build': BuildData, 'install_data': InstallData},

    data_files = [('share/commiecc/data/img', 
                        ['data/img/commiecc-artwork400x400.png', 
                        'data/img/commiecc-c-logo-bg64x64.png']),
                    ('share/pixmaps',
                        ['commie-class-control.png',
                        'commiecc-slave-desktop.png']),
                    ('share/commiecc/data', 
                        ['data/classcontrol.ui', 
                        'data/lock_screen.ui']),
                    ('share/commiecc/master-plugins',
                        ['master-plugins/mac_conf.py',
                        'master-plugins/mac_conf.ui',
                        'master-plugins/ldapmanager.py',
                        'master-plugins/examplemenu.py',
                        'master-plugins/messagemenu.ui',
                        'master-plugins/detachermenu.py',
                        'master-plugins/detachermenu.ui',
                        'master-plugins/detacher.png',
                        'master-plugins/session_time.py',
                        'master-plugins/session_time.ui']),
                    ('share/commiecc/slave-plugins',
                        ['slave-plugins/renewal.py',
                        'slave-plugins/example.py',
                        'slave-plugins/detach.py',
                        'slave-plugins/set_pass.py',
                        'slave-plugins/sess_time.py']),
                    ('share/gdm/autostart/LoginWindow/', 
                        ['commiecc-screen-locker.desktop']),
                    ('share/applications/',
                        ['commie-class-control.desktop']),
                    ('/etc/xdg/autostart/', 
                        ['commiecc-slave-desktop.desktop']),
                    ('share/applications/', 
                        ['commie-class-control.desktop']),
                    ('share/pixmaps/', 
                        ['commiecc.png']),
                    ('/etc/dbus-1/system.d', 
                        ['dbus/commiecc.conf'])]
)
