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
from sqlobject.sqlite.sqliteconnection import SQLiteConnection


CONFIG = "./meatoo.conf"
config = ConfigParser.ConfigParser()
config.read(CONFIG)

FILENAME = config.get("sqlobject", "filename")
DB_NAME = config.get("sqlobject", "dbname")
DATABASE = config.get("sqlobject", "database")
HOST = config.get("sqlobject", "host")
USERNAME = config.get("sqlobject", "username")
PASSWORD = config.get("sqlobject", "password")

conn = dbconnection.ConnectionHub()

def connect(threadIndex):
    if DATABASE == "sqlite":
        conn.threadConnection = connectionForURI("sqlite:///%s" % FILENAME)
    else:
        conn.threadConnection = connectionForURI("mysql://%s:%s@%s/%s" % \
                                (USERNAME, PASSWORD, HOST, DB_NAME))

class Packages(SQLObject):

    """Record containing freshmeat releases"""

    _connection = conn

    portageCategory = StringCol(length=64, notNull=1)
    packageName = StringCol(length=128, notNull=1)
    portageDesc = StringCol(length=254, notNull=1)
    portageVersion = StringCol(length=64, notNull=1)
    fmName = StringCol(length=128, notNull=1)
    maintainerName = StringCol(length=128, notNull=1)
    descShort = StringCol(length=254, notNull=1)
    latestReleaseVersion = StringCol(length=64, notNull=1)
    latestReleaseDate = StringCol(length=128, notNull=1)
    urlHomepage = StringCol(length=128, notNull=1)
    urlChangelog = StringCol(length=128, notNull=0)
    fmNewer = BoolCol(notNull=1)
               
    
class Ignores(SQLObject):

    """Contains packages with freshmeat versions that should be ignored
     This could be changed later with a regex for fixing versions i.e.
     games-strategy/lgeneral-1.2_beta2    1.2beta-2
     games-strategy/widelands-0.0.9      build-9"""

    _connection = conn

    packageName = StringCol(length=64, notNull=1)
    latestReleaseVersion = StringCol(length=64, notNull=1)

class KnownGood(SQLObject):

    """Contains user-submitted mappings of fm names to Gentoo package names"""

    _connection = conn
    portageCategory = StringCol(length=64, notNull=1)
    packageName = StringCol(length=128, notNull=1)
    fmName = StringCol(length=254, notNull=1)

class Users(SQLObject):

    """Contains usernames and passwords"""

    _connection = conn
    user = StringCol(length=32, notNull=1)
    password = StringCol(length=32, notNull=1)
    herdsAuto = StringCol(length=254, notNull=1)
    herdsUser = StringCol(length=254, notNull=0)
    troves = StringCol(length=254, notNull=0)
    
class Stats(SQLObject):

    """Contains misc statstics:
        fm_rdf_size      - Filesize in bytes of last fm download
        pkgs_ttl         - Total number of pkgs in database
        matches_ttl      - Total gentoo->fm pkg matches
        need_bump_ttl    - Number of pkgs needing a bump
        weekly_bumped    - Number of pkgs bumped this week
        weekly_need_bump - Number of pkgs needing a bump this week"""

    _connection = conn
    fm_rdf_size = IntCol(notNull=0)
    pkgs_ttl = IntCol(notNull=0)
    matches_ttl = IntCol(notNull=0)
    need_bump_ttl = IntCol(notNull=0)
    weekly_bumped = IntCol(notNull=0)
    weekly_need_bumps = IntCol(notNull=0)

class Allfm(SQLObject):
    """Contains all FM releases for the past week"""
    _connection = conn

    fmName = StringCol(length=128, notNull=1)
    descShort = StringCol(length=254, notNull=1)
    latestReleaseVersion = StringCol(length=64, notNull=1)
    latestReleaseDate = StringCol(length=128, notNull=1)
    urlHomepage = StringCol(length=128, notNull=1)
    urlChangelog = StringCol(length=128, notNull=1)
    troveId = StringCol(length=128, notNull=1)
    inPortage = BoolCol(notNull=1)

class Troves(SQLObject):
    """Contains all FM troves"""
    _connection = conn

    fId = StringCol(length=32, notNull=1)
    name = StringCol(length=254, notNull=1)

if __name__ == "__main__":
    #Initialize database tables if necessary
    connection_thread = connect(0)
    Packages.createTable(ifNotExists = True)
    Ignores.createTable(ifNotExists = True)
    KnownGood.createTable(ifNotExists = True)
    Users.createTable(ifNotExists = True)
    Stats.createTable(ifNotExists = True)
    Allfm.createTable(ifNotExists = True)
    Troves.createTable(ifNotExists = True)

