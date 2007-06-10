# This file is part of OtfBot.
#
# Otfbot is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Otfbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OtfBot; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
# (c) 2005, 2006 by Alexander Schier
#

import string, re
import chatMod, functions

def default_settings():
	settings={};
	settings['commandsMod.fileencoding']='iso-8859-15'
	settings['commandsMod.file']='commands.txt'
	settings['commandsmod.commandChar']='!'
	return settings
		
class chatMod(chatMod.chatMod):
	def __init__(self, bot):
		self.bot = bot
		self.commandChar={}
		self.channels=[]

	def connectionMade(self):
		self.reload()
		
	def joined(self, channel):
		self.commands[channel]=functions.loadProperties(self.bot.getConfig("file", "commands.txt", "commandsMod", self.bot.network, channel))
		self.commandChar[channel]=self.bot.getConfig("commandChar", "!", "commandsMod", self.bot.network, channel)
	
	def msg(self, user, channel, msg):
		user = user.split("!")[0] #only nick
		if self.commandChar.has_key(channel):
			try:
				char=msg[0].decode('UTF-8').encode('UTF-8')
			except UnicodeDecodeError:
				char=msg[0].decode('iso-8859-15').encode('UTF-8')
			if char == self.commandChar[channel]:
				#if msg == "!reload-commands": #TODO: global methodChar
				#	self.logger.info("reloading")
				#	self.reload()
				#	return
				answer = self.respond(channel, user, msg)
				if answer != "":
					if answer[0] == ":":
						self.bot.sendmsg(channel, answer[1:], self.bot.getConfig("commandsMod.fileencoding", "iso-8859-15"))
					else:
						self.bot.sendme(channel, answer, self.bot.getConfig("commandsMod.fileencoding", "iso-8859-15"))
			
	def start(self):
		self.commands={}
		self.commandChar={}
		self.commands["general"]=functions.loadProperties(self.bot.getConfig("file","commands.txt","commandsMod"))
		self.commands["network"]=functions.loadProperties(self.bot.getConfig("file","commands.txt","commandsMod", self.bot.network))

	def reload(self):
		self.start()
	
	def getCommand(self, channel, cmd):
		if not self.commands.has_key(channel):
			self.commands[channel]={}
		if self.commands[channel].has_key(cmd):
			return self.commands[channel][cmd]
		elif self.commands["network"].has_key(cmd):
			return self.commands["network"][cmd]
		elif self.commands["general"].has_key(cmd):
			return self.commands["general"][cmd]
		else:
			return ""

	def respond(self, channel, user, command):
		answer = ""
		if command[0] == self.commandChar[channel]:
			tmp=command[1:].split(" ", 1)
			cmd=string.lower(tmp[0])
			if len(tmp) >1:
				param=tmp[1]
				answer=self.getCommand(channel, cmd+"_")
				answer = re.sub("OTHER", param, answer)
			else:
				answer=self.getCommand(channel, cmd)
			answer = re.sub("USER", user, answer)
				
		if len(answer)>0 and answer[-1] == "\n":
			return answer[0:-1]
		else:
			return answer