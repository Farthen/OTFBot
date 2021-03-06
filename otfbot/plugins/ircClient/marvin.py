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
# (c) 2005, 2006 by Alexander Schier
#

from otfbot.lib import chatMod
from otfbot.lib import functions

import random


class Plugin(chatMod.chatMod):

    def __init__(self, bot):
        self.bot = bot

    def msg(self, user, channel, msg):
        #if channel == self.bot.nickname:
        #if msg[0]=="!" or msg[:len(self.bot.nickname)]==self.bot.nickname:
        if (msg[0] == "!" or self.bot.nickname in msg) and len(self.marvin):
            number = random.randint(0, 100)
            chance = int(self.bot.config.get("percent", "1", "marvin"))
            enc = self.bot.config.get("fileencoding", "iso-8859-15", "marvin")
            if number < chance:
                self.bot.sendmsg(channel, random.choice(self.marvin), enc)

    def start(self):
        fn = self.bot.config.getPath("file", datadir, "marvin.txt", "marvin")
        self.marvin = functions.loadList(fn)

    def reload(self):
        self.start()
