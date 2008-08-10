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
# (c) 2007 by Robert Weidlich
#

import chatMod, string
from twisted.internet import protocol, reactor
from twisted.words.protocols import irc
from twisted.words import service
from twisted.protocols import basic

class ServerProtocol(basic.LineOnlyReceiver):
	def sendMessage(self, command, *parameter_list, **prefix):
		"""
		From http://twistedmatrix.com/trac/browser/trunk/twisted/words/protocols/irc.py
		Send a line formatted as an IRC message.

		First argument is the command, all subsequent arguments
		are parameters to that command.  If a prefix is desired,
		it may be specified with the keyword argument 'prefix'.
		"""

		if not command:
			raise ValueError, "IRC message requires a command."
		#if ' ' in command or 
		if command[0] == ':':
			# Not the ONLY way to screw up, but provides a little
			# sanity checking to catch likely dumb mistakes.
			raise ValueError, "Somebody screwed up, 'cuz this doesn't" \
							" look like a command to me: %s" % command
		line = string.join([command] + list(parameter_list))
		if prefix.has_key('prefix'):
			line = ":%s %s" % (prefix['prefix'], line)
		self.sendLine(line)

		if len(parameter_list) > 15:
			self.logger.warn("Message has %d parameters (RFC allows 15):\n%s" %
				(len(parameter_list), line))

	def parsemsg(self, s):
		"""Breaks a message from an IRC server into its prefix, command, and arguments.
		"""
		prefix = ''
		trailing = []
		if not s:
		    raise IRCBadMessage("Empty line.")
		if s[0] == ':':
			prefix, s = s[1:].split(' ', 1)
		if s.find(' :') != -1:
			s, trailing = s.split(' :', 1)
			args = s.split()
			args.append(trailing)
		else:
			args = s.split()
		command = args.pop(0)
		return prefix, command.upper(), args

	def connectionLost(self, reason):
		self.mod.connected=False
	
	def lineReceived(self, line):
		(prefix,command, args) = self.parsemsg(line)
		# TODO: add a upper() or lower()
		if command == "USER" and len(args) == 4:
			self.hostmask=self.nickname+"!"+args[0]+"@"+self.transport.client[0];
			self.sendMessage(irc.RPL_WELCOME+" "+self.nickname,":connected to Twisted IRC",prefix="localhost")
			self.sendMessage(irc.RPL_YOURHOST+" "+self.nickname,":Your host is %(serviceName)s, running version %(serviceVersion)s" % {"serviceName": self.transport.server.getHost(),"serviceVersion": self.mod.bot.versionNum},prefix="localhost")
			#self.sendMessage(irc.RPL_CREATED+" "+self.nickname,":This server was created on %(creationDate)s",prefix="localhost")
			self.mod.bot.sendLine("VERSION")
			self.sendMessage("NICK",":"+self.mod.bot.nickname,prefix=self.hostmask)
			self.hostmask=self.mod.bot.nickname+"!"+args[0]+"@"+self.transport.client[0];
			
			for c in self.mod.bot.channels:
				self.sendMessage("JOIN",":"+c,prefix=self.mod.bot.nickname)
				self.mod.bot.sendLine("NAMES "+c)
			self.loggedin=True
		elif command == "NICK":
			self.nickname=args[0]

		elif command == "PASS":
			#check for password
			pass
		elif command == "BOT":
			#some controlfunctions
			pass
		elif command == "QUIT":
			self.mod.connected=False
			self.transport.loseConnection()
		else:
			self.mod.bot.sendLine(line)

class ServerProtocolFactory(protocol.ServerFactory):
	protocol=ServerProtocol
	proto=None
	def __init__(self,mod):
		self.mod=mod
	def buildProtocol(self,addr):
		proto=protocol.ServerFactory.buildProtocol(self,addr)
		self.proto=proto
		proto.mod=self.mod
		proto.loggedin=False
		if not self.mod.connected:
			self.mod.connected=True
			return proto

class chatMod(chatMod.chatMod):
	connected=False
	def __init__(self, bot):
		self.bot=bot
		self.enabled=self.bot.getBoolConfig("active", "False", "humanMod")
		if not self.enabled:
			return
		self.f=ServerProtocolFactory(self)
		
	def start(self):
		if not self.enabled:
			return
		self.bot.getReactor().listenTCP(6667, self.f)
	
	def lineReceived(self, line):
		if self.connected and self.f.proto.loggedin:
			self.f.proto.sendLine(line)
	def msg(self, user, channel, msg):
		if not (self.connected and self.f.proto.loggedin):
			return
		if string.lower(user) == string.lower(self.bot.nickname):
			self.f.proto.sendMessage("PRIVMSG", channel, ":"+msg, prefix=self.f.proto.hostmask)
	def query(self, user, channel, msg):
		if not (self.connected and self.f.proto.loggedin):
			return
		if string.lower(user) == string.lower(self.bot.nickname) and self.f.proto:
			#TODO FIXME: this is a workaround. the external irc client does not recognize own messages from queries (xchat)
			#or are just the parameters wrong? so it will show the foreign nick, but prefix the message with <botnick>
			self.f.proto.sendMessage("PRIVMSG", channel, ":<"+self.bot.nickname+"> "+msg, prefix=channel)