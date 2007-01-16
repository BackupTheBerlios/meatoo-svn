
''' 

utils.py - Miscellaneous helper functions


'''

import urllib
from time import *
import datetime
import os
import tempfile
import ConfigParser

import PyRSS2Gen
import cherrypy

from meatoodb import *
import accounts
import herds

CONFIG = "./meatoo.conf"
config = ConfigParser.ConfigParser()
config.read(CONFIG)

ADMIN_LOG = config.get("log", "admin_log")


def send_email(body):
    """Send email. Return -1 if fail"""
    tfname = tempfile.mktemp()
    tempFile = open(tfname, "w")
    tempFile.write(body)
    tempFile.close()
    os.system('/usr/bin/nbsmtp -V < %s' % tfname)
    try:
        os.unlink(tfname)
    except:
        print "WARNING - tmpfile not deleted - ", tfname
        return -1

def send_new_passwd(address):
    """Create new account and email passwd"""
    if "@" not in address:
        return "Invalid email address."
    if address.split("@")[1] != "gentoo.org":
        return "Only official Gentoo developers may register."

    username = address.split("@")[0] 
    password = accounts.get_password()
    if accounts.get_user_passwd(username):
        return "You already have an account."

    body = '''Date: <%s>\n''' % ctime(time())
    body += '''To: <%s>\n''' % address
    body += '''From: "Meatoo Registration" <gentooexp@gmail.com>\n'''
    body += '''Subject: Meatoo Registration Confirmation.\n\n'''
    body += '''You can now login to Meatoo and add, delete or modify entries.\n\n'''
    body += '''Your password is: %s\n''' % password
    if send_email(body) == -1:
        return "There was an error sending email."
    else:
        accounts.add_user(username, password)
        return "Your password has been emailed."

def mail_lost_passwd(username):
    """Email existing password to user"""
    password = accounts.get_user_passwd(username)
    body = '''Date: <%s>\n''' % ctime(time())
    body += '''To: <%s>\n''' % "%s@gentoo.org" % username
    body += '''From: "Meatoo Admin" <gentooexp@gmail.com>\n'''
    body += '''Subject: Your lost Meatoo password.\n\n'''
    body += '''Tsk tsk!\n\n'''
    body += '''Your password is: %s\n''' % password
    send_email(body)

def get_dload_size(url):
    """Returns int size in bytes of file for given url"""
    file = urllib.FancyURLopener().open(url)
    return int(file.headers['content-length'])

def get_today(offset = 0):
    """Return todays format like 2005-01-28"""
    #offset is number of days past. 1 = yesterday
    now = gmtime(mktime(gmtime()) - (86400 * offset) )
    return "%s-%02d-%02d" % (now[0], now[1], now[2])

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
        user = Users.select(Users.q.user == username)
        if user[0].herdsUser:
            herds = user[0].herdsAuto + " " + user[0].herdsUser
            herds = " ".join(herds.split())
        else:
            herds = user[0].herdsAuto
        cherrypy.session['herds'] = herds
    else:
        cherrypy.session['herds'] = None

def set_troves_session():
    """Set session var with troves user is interested in"""
    username = accounts.get_logged_username()
    if username:
        user = Users.select(Users.q.user == username)
        troves = user[0].troves
        if troves:
            cherrypy.session['troves'] = troves
        else:
            cherrypy.session['troves'] = None
    else:
        cherrypy.session['troves'] = None
            
def generate_rss(packages, herd):
    """Return dynamic RSS feed for given packages"""
    if not packages.count():
        return """<?xml version="1.0" encoding="iso-8859-1"?><rss version="2.0"><channel><title>Meatoo - Gentoo vs. Freshmeat Releases</title><link>http://meatoo.gentooexperimental.org/</link><description>The latest Freshmeat releases with matching Gentoo versions.</description><lastBuildDate>%s</lastBuildDate><generator>PyRSS2Gen-0.1.1</generator><docs>http://blogs.law.harvard.edu/tech/rss</docs><item><title>Herd %s has no entries.</title><link>http://meatoo.gentooexperimental.org/</link><description>There are no entries for %s</description><pubDate>%s</pubDate></item></channel></rss>""" % (datetime.datetime.utcnow(), herd, herd, datetime.datetime.utcnow())
    items = []
    for pkg in packages:
        items.append(PyRSS2Gen.RSSItem(
            title = "%s/%s-%s [%s]" % \
                (pkg.portageCategory, pkg.packageName, pkg.portageVersion, \
                 pkg.latestReleaseVersion),
            description = "Freshmeat Release Date: %s<br><br><b>Portage desc:</b><br> %s<br><br><b>Freshmeat desc:</b><br> %s<br>http://freshmeat.net/projects/%s/" % (pkg.latestReleaseDate, pkg.portageDesc, pkg.descShort, pkg.packageName),
            link = "http://meatoo.gentooexperimental.org/",
            pubDate = datetime.datetime.utcnow()
            ))

    rss = PyRSS2Gen.RSS2(
        title = "Meatoo - Gentoo vs. Freshmeat Releases",
        link = "http://meatoo.gentooexperimental.org/",
        description = "The latest Freshmeat releases with matching Gentoo versions.",
        lastBuildDate = datetime.datetime.utcnow(),
        items = items)
    return rss.to_xml()

def get_cookie(name):
    """Reads the value of a cookie"""
    try:
        return cherrypy.request.simpleCookie[name].value
    except Exception:
        return None

def set_cookie(name, value, path='/', age=60, version=1):
    """Sets a cookie, age in seconds"""
    cherrypy.response.simpleCookie[name] = value
    cherrypy.response.simpleCookie[name]['path']    = path
    cherrypy.response.simpleCookie[name]['max-age'] = age
    cherrypy.response.simpleCookie[name]['version'] = version

def del_cookie(name):
    """Deletes a cookie"""
    cherrypy.response.simpleCookie[name]['expires']  = 0

def admin_log_msg(msg):
    """Adds line to log file"""
    f = open(ADMIN_LOG, "a")
    f.write("%s\n" % msg)
    f.close()

