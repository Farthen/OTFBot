# This file is part of OtfBot.
#
# OtfBot is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# OtfBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OtfBot; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
# (c) 2009 Robert Weidlich
# (c) 2008 by Alexander Schier
#

from twisted.application import service
from twisted.internet import reactor

class botService(service.MultiService):
    name="scheduler"
    def __init__(self, root, parent):
        self.root=root
        self.parent=parent
        service.MultiService.__init__(self)
    """Wrapper class for the scheduling functions of twisted.internet.reactor.ReactorTime"""
    def callLater(self,time,function,*args,**kwargs):
        """ executes C{function} after C{time} seconds with arguments C{*args} and keyword arguments C{**kwargs}
            @param time: seconds to wait before executing C{function}
            @type time: int
            @param function: the function to call
            @type function: callable
            @param *args: arguments for the function
            @type *args: tuple
            @param **kwargs: keyworded arguments for the function
            @type **kwargs: dict
        """
        return reactor.callLater(time,function,*args,**kwargs)
    def cancelCallLater(self, callID):
        """ cancel a delayed call
            @param callID: the call to cancel (id returned in callLater)
        """
        return reactor.cancelCallLater(callID)

    def callPeriodic(self,delay,function,kwargs={}):
        """ executes C{function} every C{delay} seconds with keyword arguments C{**kwargs}
            @param delay: the delay between two runs of the C{function}
            @type delay: int
            @param function: the function to be called
            @type function: callable
            @param kwargs: the keyworded arguments for the function
            @type kwargs: dict
            @note: add the possibility to give a *args-tuple (need to know how to merge two tuples)
        """
        def func(delay,function,**kwargs):
            args=(delay,function)
            if function and function(**kwargs):
                reactor.callLater(delay,func,*args,**kwargs)
        args=(delay,function)
        reactor.callLater(delay,func,*args,**kwargs)
