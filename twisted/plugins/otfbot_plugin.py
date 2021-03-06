#!/usr/bin/twistd -noy
# -*- coding: iso-8859-1 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# (c) 2005 - 2010 by Alexander Schier
# (c) 2006 - 2010 by Robert Weidlich
#

""" Twistd plugin to start the bot
"""

from twisted.application import internet, service
from twisted.application.service import IServiceMaker
from twisted.plugin import IPlugin
from twisted.python import log, usage
from twisted.python import versions as twversions
import twisted

from zope.interface import implements

import logging
import logging.handlers
from logging.handlers import RotatingFileHandler
import sys
import os

from otfbot.lib import version
from otfbot.services import config as configService

required_version = twversions.Version('twisted', 9, 0, 0)
if twisted._version.version < required_version:
    print "Get %s or newer to run OTFBot" % required_version
    os._exit(1)


class Options(usage.Options):
    optParameters = [["config", "c", "otfbot.yaml", "Location of configfile"]]


class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "otfbot"
    description = "OtfBot - The friendly Bot"
    options = Options

    def makeService(self, options):
        application = service.MultiService()
        application.version = version._version

        cfgS = configService.loadConfig(options['config'], "plugins/*/*.yaml")
        if not cfgS:
            print "Could not load configuration. Check the path or create" + \
                 " a new one by running 'twistd gen-otfbot-config'"
            os._exit(1)
        cfgS.setServiceParent(application)

        ######################################################################
        ## Begin of logging setup

        logging.getLogger('').setLevel(logging.DEBUG)
        root = logging.getLogger('')

        fmtPat = '%(asctime)s %(name)-10s %(module)-14s %(funcName)-20s'
        fmtPat += '%(levelname)-8s %(message)s'
        formatPattern = cfgS.get("format", fmtPat, "logging")
        formatter = logging.Formatter(formatPattern)

        logfile = cfgS.get("file", False, "logging")
        if logfile:
            filelogger = RotatingFileHandler(logfile, 'a', 1048576, 5)
            filelogger.setFormatter(formatter)
            root.addHandler(filelogger)
        errfile = cfgS.get("errfile", False, "logging")
        if errfile:
            errorlogger = RotatingFileHandler(errfile, 'a', 1048576, 5)
            errorlogger.setFormatter(formatter)
            errorlogger.setLevel(logging.ERROR)
            root.addHandler(errorlogger)
        memorylogger = logging.handlers.MemoryHandler(1000)
        memorylogger.setFormatter(formatter)
        root.addHandler(memorylogger)
        stdout = cfgS.get("logToConsole", True, "logging")
        if stdout:
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            root.addHandler(console)

        plo = log.PythonLoggingObserver()
        log.startLoggingWithObserver(plo.emit)

        corelogger = logging.getLogger('core')

        ## end of logging setup
        ######################################################################

        corelogger.info("  ___ _____ _____ ____        _   ")
        corelogger.info(" / _ \_   _|  ___| __ )  ___ | |_ ")
        corelogger.info("| | | || | | |_  |  _ \ / _ \| __|")
        corelogger.info("| |_| || | |  _| | |_) | (_) | |_ ")
        corelogger.info(" \___/ |_| |_|   |____/ \___/ \__|")
        _v = "version %s" % application.version.short()
        corelogger.info(" " * (34 - len(_v)) + _v)

        service_names = cfgS.get("services", [], "main")
        service_classes = []
        service_instances = []
        for service_name in service_names:
            #corelogger.info("starting Service %s" % service_name)
            pkg = "otfbot.services." + service_name
            service_classes.append(__import__(pkg, fromlist=['botService']))
            srv = service_classes[-1].botService(application, application)
            srv.setServiceParent(application)
            service_instances.append(srv)

        return application

serviceMaker = MyServiceMaker()
