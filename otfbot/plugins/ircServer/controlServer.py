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
# (c) 2008 by Alexander Schier
#

from twisted.internet import reactor

from otfbot.lib import chatMod

import time

#from lib import controlInterface


class Plugin(chatMod.chatMod):
    def __init__(self, server):
        self.server=server
        self.first=True
        #self.control=controlInterface.controlInterface(self.server.root.getServiceNamed("control"))
    def irc_NICK(self, prefix, params):
        if self.first:
            self.server.join(self.server.getHostmask(), "#control")
            self.server.privmsg(self.server.getHostmask(), "#control", "Welcome to the OTFBot control channel. Type \"help\" for help ;).")
            self.server.names(self.server.name, "#control", ['OtfBot', self.server.name])
    def irc_PRIVMSG(self, prefix, params):
        channel=params[0]
        if channel=="#control":
            msg=params[1]
            self.server.privmsg(self.server.getHostmask(), "#control", self.server.root.getServiceNamed("control").handle_command(msg))