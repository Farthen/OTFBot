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
# (c) 2006 by Robert Weidlich
#

"""
    Log channel conversations to files.
"""

from otfbot.lib import chatMod

import time
import string
import locale
import os
from string import Template


class Plugin(chatMod.chatMod):

    def __init__(self, bot):
        self.bot = bot
        self.channels = {}
        self.files = {}
        self.path = {}

        os.umask(0022)
        #this has no usable defaultconfig string, because datadir is only known at runtime
        self.datadir = bot.config.getPath("logdir", datadir, ".", "log")
        default = "$n-$c/$y-$m-$d.log"
        self.logpath = self.datadir + "/" + bot.config.get("path", default, "log")
        #TODO: blocking
        if not os.path.isdir(self.datadir):
            os.makedirs(self.datadir)
        try:
            locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
        except:
            locale.setlocale(locale.LC_ALL, "")
        # saves the hour, to detect daychanges
        self.day = self.ts("%d")
        self.setNetwork()

    def timemap(self):
        return {'y': self.ts("%Y"), 'm': self.ts("%m"), 'd': self.ts("%d")}

    def ts(self, format="[%H:%M]"):
        """timestamp"""
        return time.strftime(format, time.localtime(time.time()))

    def secsUntilDayChange(self):
        """calculate the Seconds to midnight"""
        tmp = time.localtime(time.time())
        wait = (24 - tmp[3] - 1) * 60 * 60
        wait += (60 - tmp[4] - 1) * 60
        wait += 60 - tmp[5]
        return wait

    def dayChange(self):
        self.day = self.ts("%d")
        self.stop()
        for channel in self.channels:
            self.joined(channel)
            #self.log(channel, "--- Day changed "+self.ts("%a %b %d %Y"))

    def log(self, channel, string, timestamp=True):
        if self.day != self.ts("%d"):
            self.dayChange()
        if channel in self.channels:
            logmsg = string + "\n"
            if timestamp:
                logmsg = self.ts() + " " + logmsg
            #TODO: blocking
            self.files[channel].write(logmsg)
            self.files[channel].flush()

    def logPrivate(self, user, mystring):
        #dic = self.timemap()
        #dic['c'] = string.lower(user)
        #filename = Template(self.logpath).safe_substitute(dic)
        ##TODO: blocking
        #if not os.path.exists(os.path.dirname(filename)):
        #    os.makedirs(os.path.dirname(filename))
        #file = open(filename, "a")
        #file.write(self.ts() + " " + mystring + "\n")
        #file.close()
        pass

    def joined(self, channel):
        self.channels[string.lower(channel)] = 1
        #self.files[string.lower(channel)]=open(string.lower(channel)+".log", "a")
        self.path[channel] = Template(self.logpath).safe_substitute({'c': channel.replace("/", "_").replace(":", "")}) #replace to handle psyc:// channels
        file = Template(self.path[channel]).safe_substitute(self.timemap())
        #TODO: blocking
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))
        self.files[string.lower(channel)] = open(file, "a")
        self.log(channel, "--- Log opened " + self.ts("%a %b %d %H:%M:%S %Y"), False)
        #self.log(channel, "*** " + self.bot.nickname + " [" + self.bot.nickname + "@hostmask] has joined " + channel) #TODO: real Hostmask
        self.channels[string.lower(channel)] = 1

    def left(self, channel):
        self.log(channel, "*** " + self.bot.nickname + "[" + self.bot.nickname + "@hostmask] has left " + channel)
        del self.channels[string.lower(channel)]
        self.files[string.lower(channel)].close()

    def msg(self, user, channel, msg):
	#self.logger.debug(user+" "+channel+" "+msg)
        user = user.split("!")[0]
        modesign = "" #self.bot.users[channel][user]['modchar']
        if string.lower(channel) == string.lower(self.bot.nickname):
            self.logPrivate(user, "<" + modesign + user + "> " + msg)
        elif len(channel) > 0 and channel[0] == "#":
            #modesign=self.bot.users[channel][user]['modchar']
            self.log(channel, "<" + modesign + user + "> " + msg)

    def query(self, user, channel, msg):
        user = user.split("!")[0]
        if user == self.bot.nickname:
            self.logPrivate(channel, "<" + user + "> " + msg)
        else:
            self.logPrivate(user, "<" + user + "> " + msg)

    def noticed(self, user, channel, msg):
        if user != "":
            #self.logger.info(str(user+" : "+channel+" : "+msg))
            self.logPrivate(user.split("!")[0], "< " + user.split("!")[0] + "> " + msg)

    def action(self, user, channel, msg):
        #self.logger.debug(user+channel+msg)
        user = user.split("!")[0]
        self.log(channel, "* " + user + " " + msg)

    def modeChanged(self, user, channel, set, modes, args):
        user = user.split("!")[0]
        sign = "+"
        if not set:
            sign = "-"
        self.log(channel, "*** mode/" + channel + " [" + sign + modes + " " + string.join(args, " ") + "] by " + user)

    def userKicked(self, kickee, channel, kicker, message):
        self.log(channel, "*** " + kickee + " was kicked from " + channel + " by " + kicker + " [" + message + "]")

    def userJoined(self, user, channel):
        self.log(channel, "*** " + user.split("!")[0] + " has joined " + channel)

    def userLeft(self, user, channel):
        self.log(channel, "*** " + user.split("!")[0] + " has left " + channel)

    def userQuit(self, user, quitMessage):
        user = user.split("!")[0]
        userdict = self.bot.getChannelUserDict()
        for channel in userdict:
            for chanuser in userdict[channel]:
                if chanuser.nick == user:
                    self.log(channel, "*** " + user + " has quit IRC (" + quitMessage + ")")

    def topicUpdated(self, user, channel, newTopic):
        #TODO: first invoced on join. This should not be logged
        self.log(channel, "*** " + user + " changed the topic of " + channel + " to: " + newTopic)

    def userRenamed(self, oldname, newname):
        #TODO: This can not handle different channels right
        userdict = self.bot.getChannelUserDict()
        for channel in userdict:
            for chanuser in userdict[channel]:
                if chanuser.nick == oldname:
                    self.log(channel, "*** " + oldname + " is now known as " + newname)
                    chanuser.nick = newname

    def stop(self):
        for channel in self.channels:
            self.log(channel, "--- Log closed " + self.ts("%a %b %d %H:%M:%S %Y"), False)
            self.files[channel].close()

    def connectionMade(self):
        self.setNetwork()

    def setNetwork(self):
        if len(self.bot.network.split(".")) < 3:
            net = self.bot.network
        else:
            net = self.bot.network.split(".")[-2]
        self.logpath = Template(self.logpath).safe_substitute({'n': net})
