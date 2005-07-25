#!/usr/bin/env python

"""

cherry_meatoo.py

This is the web app server and dynamic RSS feed generator.


This sofware is Copyright 2005 released
under the terms of the GNU Public License Version 2

Original author and lead developer: Rob Cakebread
Contributor: Renat Lumpau

"""

import ConfigParser
import optparse

import cherrypy

import MeatooServer
import XMLServer


CONFIG = "./meatoo.conf"

config = ConfigParser.ConfigParser()
config.read(CONFIG)


if __name__ == '__main__':
    optParser = optparse.OptionParser()
    optParser.add_option("-d", action="store_true",
                         dest="debug", default=False,
                         help="Set debug level.")
    optParser.add_option("-v", action="store_true",
                         dest="verbose", default=False,
                         help="Be more verboserer.")
    options, remainingArgs = optParser.parse_args()
    cherrypy.root = MeatooServer.MyServer(config,
                                          options.debug,
                                          options.verbose)
    cherrypy.root.xmlrpc = XMLServer.MyServer(config,
                                              options.debug,
                                              options.verbose)
    cherrypy.config.update(file = './cherrypy.conf')
    cherrypy.server.start()

