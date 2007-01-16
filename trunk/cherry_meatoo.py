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

from meatoodb import *
import MeatooServer
import XMLServer


CONFIG = "./meatoo.conf"
CHERRYPY_CONFIG = "./cherrypy.conf"

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
    #cherrypy.tree._cp_config = {'environment': "production"}
    cherrypy.root.xmlrpc = XMLServer.MyServer(config,
                                              options.debug,
                                              options.verbose)
    #cherrypy.tree.mount(MeatooServer.MyServer(config, options.debug, options.verbose), config=CHERRYPY_CONFIG)
    #cherrypy.tree.mount(XMLServer.MyServer(config, options.debug, options.verbose))

    cherrypy.config.update(file = './cherrypy.conf')
    cherrypy.config.update({'/xmlrpc':{'xmlrpc_filter.on':True}})
    cherrypy.server.on_start_thread_list = [connect]
    cherrypy.server.start()

    #cherrypy.server.quickstart()
    #cherrypy.engine.start()

