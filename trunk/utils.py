
''' 

utils.py - Miscellaneous helper functions


'''

import urllib
from time import *
import datetime

import PyRSS2Gen
import accounts
import herds
import cherrypy


def get_dload_size(url):
    """Returns int size in bytes of file for given url"""
    file = urllib.FancyURLopener().open(url)
    return int(file.headers['content-length'])

def get_days():
    """Return date strings for last five days"""
    week = []
    i = 0
    while i < 5:
        now = gmtime(mktime(gmtime()) - 86400 * i)
        week.append("%s-%02d-%02d" % (now[0], now[1], now[2]))
        i += 1
    return week

def set_herd_session():
    """Set session var with herds user belongs to"""
    username = accounts.get_logged_username()
    if username:
        my_herds = " ".join(herds.get_dev_herds(username))
        cherrypy.session['herds'] = my_herds
    else:
        cherrypy.session['herds'] = None

def generate_rss(packages, herd):
    """Return dynamic RSS feed for given packages"""
    if not packages.count():
        return """<?xml version="1.0" encoding="iso-8859-1"?><rss version="2.0"><channel><title>Meatoo - Gentoo vs. Freshmeat Releases</title><link>http://www.gentooexperimental.org/meatoo</link><description>The latest Freshmeat releases with matching Gentoo versions.</description><lastBuildDate>%s</lastBuildDate><generator>PyRSS2Gen-0.1.1</generator><docs>http://blogs.law.harvard.edu/tech/rss</docs><item><title>Herd %s has no entries.</title><link>http://gentooexperimental.org/meatoo/</link><description>There are no entries for %s</description><pubDate>%s</pubDate></item></channel></rss>""" % (datetime.datetime.utcnow(), herd, herd, datetime.datetime.utcnow())
    items = []
    for pkg in packages:
        items.append(PyRSS2Gen.RSSItem(
            title = "%s/%s-%s [%s]" % \
                (pkg.portageCategory, pkg.packageName, pkg.portageVersion, \
                 pkg.latestReleaseVersion),
            description = "Freshmeat Release Date: %s<br><br><b>Portage desc:</b><br> %s<br><br><b>Freshmeat desc:</b><br> %s<br>http://freshmeat.net/projects/%s/" % (pkg.latestReleaseDate, pkg.portageDesc, pkg.descShort, pkg.packageName),
            link = "http://gentooexperimental.org/meatoo/",
            pubDate = datetime.datetime.utcnow()
            ))

    rss = PyRSS2Gen.RSS2(
        title = "Meatoo - Gentoo vs. Freshmeat Releases",
        link = "http://www.gentooexperimental.org/meatoo",
        description = "The latest Freshmeat releases with matching Gentoo versions.",
        lastBuildDate = datetime.datetime.utcnow(),
        items = items)
    return rss.to_xml()

