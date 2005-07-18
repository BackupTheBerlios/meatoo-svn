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

import cherrypy

import MeatooServer
import XMLServer


CONFIG = "./meatoo.conf"

config = ConfigParser.ConfigParser()
config.read(CONFIG)

    
cherrypy.root = MeatooServer.MyServer(config)
cherrypy.root.xmlrpc = XMLServer.MyServer(config)
cherrypy.config.update(file = './cherrypy.conf')
cherrypy.server.start()

