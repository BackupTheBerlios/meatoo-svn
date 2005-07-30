#!/usr/bin/env python

"""

me2sql.py

This updates the sql database and writes static RSS file.
Make sure you use both options (-u, -r) for normal updates.


This sofware is Copyright 2005 Rob Cakebread released
under the terms of the GNU Public License Version 2


"""


import sys
from commands import getstatusoutput
import cPickle
import datetime
import optparse

import PyRSS2Gen
import portage

from meatoodb import *
import herds
import utils


FM_DICT = "/var/tmp/meatoo/fmdb"
TROVES_DICT = "/var/tmp/meatoo/trdb"
XML_FILE = "/var/www/localhost/htdocs/static/meatoo.xml"
TREE_FILE = "/var/tmp/meatoo/porttree"

class RSS_Generator:

    """Generates static RSS file"""

    def __init__(self):
        self.items = []

    def new_item(self, cat, pn, pv, rel, desc, fm_desc, date):
        """Generate dynamic RSS feed"""
        self.items.append(PyRSS2Gen.RSSItem(
                title = "%s/%s-%s [%s]" % \
                (cat, pn, pv, rel),
                link = "http://freshmeat.net/projects/%s/" % pn,
                description = "Freshmeat release date: %s<br><br><b>Portage desc:</b><br> %s<br><br><b>Freshmeat desc:</b><br> %s<br>http://freshmeat.net/projects/%s/" % (date, desc, fm_desc, pn),
                pubDate = datetime.datetime.now()
                ))

    def write_rss(self):
        """Write file to disk"""
        rss = PyRSS2Gen.RSS2(
            title = "Meatoo - Gentoo vs. Freshmeat Releases",
            link = "http://www.gentooexperimental.org/meatoo",
            description = "The latest Freshmeat releases with matching Gentoo versions.",
            lastBuildDate = datetime.datetime.now(),
            items = self.items)
        rss.write_xml(open(XML_FILE, "w"))

my_rss =  RSS_Generator()

def get_maints(cpn):
    """Return maintainers for CPN"""
    cmd = "herdstat -q -n -m %s" % cpn
    status, output = getstatusoutput(cmd)
    m = output.splitlines()
    if status or m[1].strip() == "No metadata.xml":
        return "NoMetadata"
    
    maints = m[1]
    herds = m[2]
    if maints.strip() == "none":
        maints = ""
    if herds.strip() == "none":
        herds = ""
    if not herds and not maints:
        return "NoMetadata"
    return "%s %s" % (maints, herds)

def split_package_name(name):
    """Returns a list on the form [category, name, version, revision]. Revision will
    be 'r0' if none can be inferred. Category and version will be empty, if none can
    be inferred."""
    r = portage.catpkgsplit(name)
    if not r:
        r=name.split("/")
        if len(r) == 1:
            return ["",name,"","r0"]
        else:
            return r + ["","r0"]
    if r[0] == 'null':
        r[0] = ''
    return r

def get_gentoo_pkgs():
    """Return list of every Gentoo package"""
    return cPickle.load(open(TREE_FILE, 'r'))

def get_versions(pn):
    """Return True if package has unique name"""
    try:
       pkgs = portage.portdb.xmatch("match-all", pn)
    except ValueError, msg:
        return
    if not len(pkgs):
        return 
    return pkgs

def get_highest(pn, pkgs):
    """Return highest available version from a list of packages"""
    try:
        return portage.portdb.xmatch("bestmatch-list", pn, mylist = pkgs)
    except:
        pass

def crossref_gentoo(fm):
    """Insert each gentoo package in db, add freshmeat id"""
    #rss items:
    items = []
    #Get all gentoo pkgs, installed, uninstalled and overlay.
    pkgs = get_gentoo_pkgs()
    #print len(pkgs)
    for cpn in pkgs:
        #pkg element is in cat/packagname format
        cpn = cpn.strip()
        cat, pn = cpn.split("/")
        pn = pn.lower()

        if fm.has_key(pn):
            vers = get_versions(pn)
            if vers:
                highest = get_highest(pn, vers)
                pv = split_package_name(get_highest(pn, vers))[2]
                fm_ver = fm[pn]['latestReleaseVersion']
                try:
                    res = portage.pkgcmp([pn, pv, "r0"], [pn, fm_ver, "r0"]) 
                    # -1 if fm is higher
                except:
                    #This means its a fm version that won't compare with Gentoo's
                    #version. We accept it as being higher. e.g. pkgfoo_BeTa.12
                    res = -1
                desc = portage.portdb.aux_get(highest, ["DESCRIPTION"])[0]
                maints = get_maints(cpn)
                if res == -1:
                    #freshmeat version is higher than portage's
                    #OR freshmeat's version is so screwy we assume its higher
                    update_sql(desc, fm[pn], cat, pn, pv, maints, 1)
                else:
                    #freshmeat version is equal or lower that portage's
                    update_sql(desc, fm[pn], cat, pn, pv, maints, 0)
            del fm[pn]

def delete_ignores():
    """Go through Ignores table and delete all matches"""
    ignores = Ignores.select()
    print "Removing ignored pkgs from db..."
    for i in ignores:
        pn = i.packageName
        ver = i.latestReleaseVersion
        print "Deleting %s-%s" % (pn, ver)
        try:
            pkg = Packages.select(AND(Packages.q.packageName == pn,
                                      Packages.q.latestReleaseVersion == ver))
            pkg[0].destroySelf()
        except:
            #Doesn't exist anymore so remove from Ignores table:
            ignore = Ignores.select(Ignores.q.id == i.id)
            ignore[0].destroySelf()

def query_sql(fm_id):
    """Fetch package by fm id"""
    return Packages.select(Packages.q.id == fm_id)

def check_known_good(fmName):
    """Check if pkg fmName exists in KnownGood db. Returns 0 if no match found, and cat/pn if found"""
    match = KnownGood.select(KnownGood.q.fmName == fmName)
    if match.count():
        # have a known good package
        return match[0].portageCategory, match[0].packageName
    else:
        # no known good
        return 0

def update_sql(desc, my_fm, cat, pn, pv, maints, higher):
    """Add or update pkg (if exists)"""
    pkg_good = check_known_good(my_fm['fmName'])
    if pkg_good:
        true_cat, true_pn = pkg_good
    else:
        true_cat, true_pn = cat, pn
        
    res = query_sql(my_fm['id'])
    if res.count():
        #Record exists, update it
        res[0].set(packageName = true_pn,
                   portageCategory = true_cat,
                   portageDesc = desc,
                   portageVersion = pv,
                   maintainerName = maints,
                   fmName = my_fm['fmName'],
                   descShort = my_fm['descShort'],
                   latestReleaseVersion = my_fm['latestReleaseVersion'],
                   urlHomepage = my_fm['urlHomepage'],
                   urlChangelog = my_fm['urlChangelog'],
                   latestReleaseDate = my_fm['latestReleaseDate'],
                   fmNewer = higher
                  ) 
    else:
        #Add new package
        p = Packages(id = int(my_fm['id']),
                     portageCategory = true_cat,
                     packageName = true_pn,
                     portageDesc = desc,
                     portageVersion = pv,
                     maintainerName = maints,
                     fmName = my_fm['fmName'],
                     descShort = my_fm['descShort'],
                     latestReleaseVersion = my_fm['latestReleaseVersion'],
                     urlHomepage = my_fm['urlHomepage'],
                     urlChangelog = my_fm['urlChangelog'],
                     latestReleaseDate = my_fm['latestReleaseDate'],
                     fmNewer = higher
                    )

    #These packages will be added to RSS feeds and sent in email subscriptions:
    if higher and not query_ignore(true_pn, my_fm['latestReleaseVersion']):
        if my_fm['latestReleaseDate'] == utils.get_today(1): 
            print "SUBSCRIPTION", true_pn, my_fm['latestReleaseDate'], 
                    pv, my_fm['latestReleaseVersion']
            my_rss.new_item(true_cat,
                            true_pn,
                            pv,
                            my_fm['latestReleaseVersion'],
                            desc,
                            my_fm['descShort'],
                            my_fm['latestReleaseDate']
                            )
                

def query_ignore(pn, fm_ver):
    """Return True if ignored"""
    ignore = Ignores.select(AND(Ignores.q.packageName == pn,
                                Ignores.q.latestReleaseVersion == fm_ver))
    if ignore.count():
        return True

def get_latest_fm(fm):
    """Store 1 week's worth of all FM releases in a table"""

    week = utils.get_days()
    
    pkgs = get_gentoo_pkgs()
    pnames = []
    for gp in pkgs:
        pnames.append(gp.split('/')[1])
                
    for pkg in fm.keys():
        if fm[pkg]['latestReleaseDate'] in week:
            if fm[pkg]['fmName'].lower() in pnames:
                port = True
            else:
                port = False
                
            Allfm(fmName = fm[pkg]['fmName'],
                         descShort = fm[pkg]['descShort'],
                         latestReleaseVersion = fm[pkg]['latestReleaseVersion'],
                         urlHomepage = fm[pkg]['urlHomepage'],
                         urlChangelog = fm[pkg]['urlChangelog'],
                         latestReleaseDate = fm[pkg]['latestReleaseDate'],
                         troveId = fm[pkg]['troveId'],
                         inPortage = port
                        )
            #print "NEW_ALL", fm[pkg]['fmName'], fm[pkg]['latestReleaseDate'], fm[pkg]['latestReleaseVersion'], fm[pkg]['troveId'], port

def store_herds():
    """Store herds of each registered dev in the db"""
    for dev in Users.select():
        dev.set(herdsAuto = " ".join(herds.get_dev_herds(dev.user)))

def store_troves(tr):
    """Store FM troves in the db"""
    for t in tr.keys():
        Troves(fId = tr[t]['id'], name = tr[t]['name'] )

if __name__ == '__main__':

    optParser = optparse.OptionParser()
    optParser.add_option( "-u", action="store_true", dest="update", default=False,
                            help="Update database of packages.")
    optParser.add_option( "-r", action="store_true", dest="rss", default=False,
                            help="Write static RSS file.")
    optParser.add_option( "-d", action="store_true", dest="herds", default=False,
                            help="Update database of herds.")
    optParser.add_option( "-l", action="store_true", dest="latest", default=False,
                            help="Update database of all latest FM releases.")
    optParser.add_option( "-t", action="store_true", dest="troves", default=False,
                            help="Update database of FM troves.")
    options, remainingArgs = optParser.parse_args()
    if len(sys.argv) == 1:
        optParser.print_help()
        sys.exit()

    if options.rss and not options.update:
        print "You must update (-u) in order to write an RSS file (-r)"
        sys.exit(1)
    if options.update:
        fm = cPickle.load(open(FM_DICT, 'r'))
        crossref_gentoo(fm)
        delete_ignores()
    if options.rss:
        my_rss.write_rss()
        #print len(fm.keys())
    if options.herds:
        store_herds()
    if options.latest:
        fm = cPickle.load(open(FM_DICT, 'r'))
        get_latest_fm(fm)
    if options.troves:
        fm = cPickle.load(open(TROVES_DICT, 'r'))
        store_troves(fm)
