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

# From http://wiki.python.org/moin/PythonDecoratorLibrary#CreatingWell-BehavedDecorators.2BAC8.22Decoratordecorator.22
def simple_decorator(decorator):
    """This decorator can be used to turn simple functions into well-behaved 
    decorators, so long as the decorators are fairly simple. If a decorator 
    expects a function and returns a function (no descriptors), and if it 
    doesn't modify function attributes or docstring, then it is eligible to use
    this. Simply apply @simple_decorator to your decorator and it will 
    automatically preserve the docstring and function attributes of functions 
    to which it is applied."""
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    # Now a few lines needed to make simple_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator
    
import threading

@simple_decorator
def threaded(f):
    def wrapper(*args):
        t = threading.Thread(target=f, args=args)
        t.setDaemon(True)
        t.start()
    return wrapper
