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
# (c) 2009 by Alexander Schier
#

"""
search on youtube with !youtube search phrase
"""

from otfbot.lib import chatMod, urlutils
import logging
import urllib


class Plugin(chatMod.chatMod):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger("youtube")
        self.feedparser=self.bot.depends_on_module("feedparser")
    def command(self, user, channel, command, options):
        if command=="youtube" and options:
            parsed=self.feedparser.parse("http://gdata.youtube.com/feeds/base/videos?q=%s&client=ytapi-youtube-search&alt=rss&v=2"%urllib.quote(options))
            if len(parsed.entries):
                self.bot.sendmsg(channel, "%s - %s"%(parsed.entries[0]['link'].encode("UTF-8"), parsed.entries[0]['title'].encode("UTF-8")))
            else:
                self.bot.sendmsg(channel, "Error: Nothing found")
