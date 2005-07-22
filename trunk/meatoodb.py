#!/usr/bin/python

"""

meatoodb.py - sqlobject database code


This sofware is Copyright 2005 released
under the terms of the GNU Public License Version 2

Original author and lead developer: Rob Cakebread
Contributor: Renat Lumpau

"""


import os
import ConfigParser

from sqlobject import *


CONFIG = "./meatoo.conf"

config = ConfigParser.ConfigParser()
config.read(CONFIG)

FILENAME = config.get("sqlobject", "filename")
DB_NAME = config.get("sqlobject", "dbname")
DATABASE = config.get("sqlobject", "database")
HOST = config.get("sqlobject", "host")
USERNAME = config.get("sqlobject", "username")
PASSWORD = config.get("sqlobject", "password")

if DATABASE == "sqlite":
    conn = connectionForURI("sqlite:///%s" % FILENAME)
else:
    conn = connectionForURI("mysql://%s:%s@%s/%s" % \
                                (USERNAME, PASSWORD, HOST, DB_NAME)
                            )



class Packages(SQLObject):

    """Record containing freshmeat releases"""

    _connection = conn

    _columns = [StringCol('portageCategory', length=64, notNull=1),
                StringCol('packageName', length=128, notNull=1),
                StringCol('portageDesc', length=254, notNull=1),
                StringCol('portageVersion', length=64, notNull=1),
                StringCol('fmName', length=128, notNull=1),
                StringCol('maintainerName', length=128, notNull=1),
                StringCol('descShort', length=254, notNull=1),
                StringCol('latestReleaseVersion', length=64, notNull=1),
                StringCol('latestReleaseDate', length=128, notNull=1),
                StringCol('urlHomepage', length=128, notNull=1),
                StringCol('urlChangelog', length=128, notNull=0),
                BoolCol('fmNewer',notNull=1)
               ]
    

class Ignores(SQLObject):

    """Contains packages with freshmeat versions that should be ignored
     This could be changed later with a regex for fixing versions i.e.
     games-strategy/lgeneral-1.2_beta2    1.2beta-2
     games-strategy/widelands-0.0.9      build-9"""

    _connection = conn

    _columns = [StringCol('packageName', length=64, notNull=1),
                StringCol('latestReleaseVersion', length=64, notNull=1)
               ]

class KnownGood(SQLObject):
    """Contains user-submitted mappings of fm names to Gentoo package names"""

    _connection = conn
    _columns = [StringCol('portageCategory', length=64, notNull=1),
                StringCol('packageName', length=128, notNull=1),
                StringCol('fmName', length=254, notNull=1)
               ]

class Users(SQLObject):
    """Contains usernames and passwords"""

    _connection = conn
    _columns = [StringCol('user', length=32, notNull=1),
                StringCol('password', length=32, notNull=1)
               ]
    
class Herds(SQLObject):
    """Contains herds and associated trove ids"""

    _connection = conn
    _columns = [StringCol('herd', length=32, notNull=1),
                StringCol('trove', length=32, notNull=1)
               ]


Packages.createTable(ifNotExists = True)
Ignores.createTable(ifNotExists = True)
KnownGood.createTable(ifNotExists = True)
Users.createTable(ifNotExists = True)
Herds.createTable(ifNotExists = True)
