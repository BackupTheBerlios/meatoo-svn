
import datetime
from time import *
import tempfile
import ConfigParser

import cherrypy
from cherrypy.lib import cptools
from cherrypy.lib import httptools
from Cheetah.Template import Template

import accounts
from sections import *
from meatoodb import *
from auth import *


 
class MyServer(cptools.PositionalParametersAware):
    """Server class for meatoo"""


    def __init__(self, config):
        cptools.PositionalParametersAware.__init__(self)
        self.config = config

    def get_days(self):
        """Get date strings for last five days"""
        week = []
        i = 0
        while i < 5:
            now = gmtime(mktime(gmtime()) - 86400 * i)
            week.append("%s-%02d-%02d" % (now[0], now[1], now[2]))
            i += 1
        return week

    def body(self, verbose, login):
        """Yields body html"""
        print cherrypy.request.headerMap
        week = self.get_days()
        packages = Packages.select(OR(Packages.q.latestReleaseDate == week[0],
                                    Packages.q.latestReleaseDate == week[1],
                                    Packages.q.latestReleaseDate == week[2],
                                    Packages.q.latestReleaseDate == week[3],
                                    Packages.q.latestReleaseDate == week[4]
                                    ))
        packages = packages.orderBy('latestReleaseDate').reversed()
        template = Template('''
<table><tr><td width="65%"><table><br><b>Latest:</b>
#for $pkg in $packages
    #if $pkg.latestReleaseDate == $week[0] or $pkg.latestReleaseDate == $week[1]
        <tr class="alt">
        <td>

        #if $verbose
            ($pkg.id)
        #end if    

        <b><a href="http://packages.gentoo.org/search/?sstring=%5E$pkg.packageName%24">
        $pkg.portageCategory/$pkg.packageName-$pkg.portageVersion</a> [
        <a class="nav" href="http://freshmeat.net/projects/$pkg.packageName/" title="Freshmeat Latest Release">$pkg.latestReleaseVersion</a> ]</b>
        $pkg.latestReleaseDate 

        <a class="nav" href="/meatoo/ignore/$pkg.id" title="Ignore this version of this package.">
        <img border=0 src="/meatoo/static/edit.png" alt="Ignore"></a>
        <a class="nav" href="/meatoo/add_known/$pkg.fmName" title="Edit Portage name">
        <img border=0 src="/meatoo/static/edit.gif"></a>
        <a class="nav" href="$pkg.urlHomepage" title="Project Homepage">
        <img border=0 src="/meatoo/static/home.png"></a>

        <a class="nav" href="http://freshmeat.net/redir/$pkg.packageName/$pkg.urlChangelog/url_changelog/" title="View ChangeLog">
        <img border=0 src="/meatoo/static/changelog.gif" alt="changelog"></a>

        </td></tr><tr><td><br>
        $pkg.portageDesc
        <br><br>
        <b>Freshmeat description:</b><br>
        $pkg.descShort<br><br>
        <b>Maintainers:</b> $pkg.maintainerName<br><br></td></tr>
    #end if
#end for
</table>
</td>
<td>
<table>
    #set $i = 0
    #while $i < 5
        <tr class="alt"><td><b>$week[$i]</b></tr>
        #for $pkg in $packages
            #if $pkg.latestReleaseDate == $week[$i]
                <tr><td>
                <a href="http://packages.gentoo.org/search/?sstring=%5E$pkg.packageName%24">
                $pkg.portageCategory/$pkg.packageName-$pkg.portageVersion</a> [
                <a class="nav" href="http://freshmeat.net/projects/$pkg.packageName/" title="Freshmeat Latest Release">$pkg.latestReleaseVersion</a> ]
        <a class="nav" href="/meatoo/ignore/$pkg.id" title="Ignore this version of this package.">
        <img border=0 src="/meatoo/static/edit.png" alt="Ignore"></a>
        <a class="nav" href="/meatoo/add_known/$pkg.fmName" title="Edit Portage name">
        <img border=0 src="/meatoo/static/edit.gif"></a>
        <a class="nav" href="$pkg.urlHomepage" title="Project Homepage">
        <img border=0 src="/meatoo/static/home.png"></a>

        <a class="nav" href="http://freshmeat.net/redir/$pkg.packageName/$pkg.urlChangelog/url_changelog/" title="View ChangeLog">
        <img border=0 src="/meatoo/static/changelog.gif" alt="changelog"></a>
                </td></tr>
            #end if
        #end for
        #set $i += 1 
    #end while
</table></td></tr></table>
        ''', [locals(), globals()])
        return template.respond()

    def ignore_action(self, pn, ver):
        """Process ignore form"""
        try:
            pkg = Packages.select(AND(Packages.q.packageName == pn, \
                                  Packages.q.latestReleaseVersion == ver))
            pkg[0].destroySelf()
            print "Deleted match:", pn
        except:
            pass
        ignore = Ignores(packageName = pn, latestReleaseVersion = ver)
        yield pn + "-" +  ver + " ignored.<br><br>"
        yield "Go <a href='/meatoo'>back</a>"
        yield footer()
    ignore_action.exposed = True

    @cherrypy.expose
    @needsLogin
    def ignore(self, id, *args, **kwargs):
        """Ignore particular version of pkg"""
        yield header()
        yield self.ignore_form(id)
        yield footer()

    def ignore_form(self, id):
        """Form for ignoreing pkgs"""
        pkg = Packages.get(id)
        template = Template('''
            <form method="get" action="/meatoo/ignore_action/">
            <div>
            <h3>Ignore $pkg.packageName</h3>
            <br>This will ignore this particular freshmeat release version, not the entire pacakge.</b><br><br>
            Freshmeat Release Date: $pkg.latestReleaseDate<br><br>
            <a href="http://packages.gentoo.org/search/?sstring=%5E$pkg.packageName%24">
            $pkg.portageCategory/$pkg.packageName-$pkg.portageVersion</a> [
            <a class="nav" href="http://freshmeat.net/projects/$pkg.packageName/" title="Freshmeat Latest Release">$pkg.latestReleaseVersion</a> ]
            </div><div><br />
            <input type="submit" value="Ignore" />
            <input type='hidden' name='pn' value='$pkg.packageName'>
            <input type='hidden' name='ver' value='$pkg.latestReleaseVersion'>
            </div>
            </form>
        ''', [locals(), globals()])
        return template.respond()

    def signup(self):
        """Return search results"""
        yield header()
        yield self.signup_section()
        yield footer()
    signup.exposed = True

    def signup_section(self):
        return '''
             <form method="get" action="/meatoo/signup_send/">
             <div>
              <h3>Meatoo Signup</h3>
              Currently only Gentoo developers can signup to edit Meatoo entries.<br><br>
              <div>
               <label for="email">Email:</label>
               <input type="text" id="email" name="email" class="textwidget" size="30"
                      value="" />
              </div></div><div><br />
               <input type="submit" value="Register" />
              </div>
             </form>
        '''

    def signup_send(self, email):
        if "@" not in email:
            return "Invalid email address."
        if email.split("@")[1] != "gentoo.org":
            return "Only official Gentoo developers may register."

        username = email.split("@")[0] 
        password = self.get_password()
        if accounts.get_user_passwd(username):
            return "You already have an account."
        mail = '''Date: %s\n''' % datetime.datetime.now()
        mail += '''To: <%s>\n''' % email
        mail += '''From: "Meatoo Registration" <gentooexp@gmail.com>\n'''
        mail += '''Subject: Meatoo is ready for you.\n\n'''
        mail += '''You can now login to Meatoo and add, delete or modify entries.\n\n'''
        mail += '''Your password is: %s\n''' % password
        tfname = tempfile.mktemp()
        tempFile = open(tfname, "w")
        tempFile.write(mail)
        tempFile.close()
        accounts.add_user(username, password)
        os.system('/usr/bin/nbsmtp < %s &' % tfname)
        return """Your password has been emailed."""
    signup_send.exposed = True

    def search(self,srch = "", type = ""):
        """Return search results"""
        yield header()
        yield self.search_results(srch, type)
        yield footer()

    def search_results(self, srch, type):
        """Return search results page"""
        if self.config.get("web", "showall") == "False":
            if type == 'herd':
                packages = Packages.select( AND ( LIKE(Packages.q.maintainerName, '%' +  srch + '%'), Packages.q.fmNewer==1 ) )
            elif type == 'pn':
                packages = Packages.select( AND ( LIKE(Packages.q.packageName, '%' + srch + '%'), Packages.q.fmNewer==1) )
            elif type == "cat":
                packages = Packages.select( AND ( LIKE(Packages.q.portageCategory, '%' + srch + '%'), Packages.q.fmNewer==1) )
            else:
                return "<b>Nothing found for:</b> %s" % srch
        else: # showall = True
            if type == 'herd':
                packages = Packages.select(LIKE(Packages.q.maintainerName, '%' +  srch + '%') )
            elif type == 'pn':
                packages = Packages.select(LIKE(Packages.q.packageName, '%' + srch + '%'))
            elif type == "cat":
                packages = Packages.select(LIKE(Packages.q.portageCategory, '%' + srch + '%'))
            else:
                return "<b>Nothing found for:</b> %s" % srch


        packages = packages.orderBy('latestReleaseDate').reversed()

        template = Template('''
            <b>Search results for:</b> $srch
            <table>
            <tr> <th>Portage Name</th> <th>Portage Version</th> <th>Freshmeat Version</th> <th>Freshmeat Release Date</th> <th>Maintainers</th></tr>

            #for $pkg in $packages
                <tr class="alt">
                <td><a href="http://packages.gentoo.org/search/?sstring=%5E$pkg.packageName%24">
                $pkg.portageCategory/$pkg.packageName</a>
                <a class="nav" href="/meatoo/ignore/$pkg.id" title="Ignore this version of this package.">
                <img border=0 src="/meatoo/static/edit.png" alt="Ignore"></a>

                <a class="nav" href="/meatoo/add_known/$pkg.fmName" title="Edit Portage name">
                <img border=0 src="/meatoo/static/edit.gif"></a>
                <a class="nav" href="$pkg.urlHomepage" title="Project Homepage">
                <img border=0 src="/meatoo/static/home.png"></a></td>
                #if pkg.portageVersion < $pkg.latestReleaseVersion
                    <td class="hilite">$pkg.portageVersion</td>
                #else
                    <td>$pkg.portageVersion</td>
                #end if
                <td><a href="http://freshmeat.net/projects/$pkg.packageName/">$pkg.latestReleaseVersion</a>
                <a class="nav" href="http://freshmeat.net/redir/$pkg.packageName/$pkg.urlChangelog/url_changelog/" title="changelog">
                <img border=0 src="/meatoo/static/changelog.gif"></a>
                </td><td>$pkg.latestReleaseDate</td>
                <td>$pkg.maintainerName</td>
                </tr>
            #end for
            </table>
            ''', [locals(), globals()])
        return template.respond()
    search.exposed = True

    def add_known_form(self, pn):
        """Generate form for adding known-goods"""
        packages = KnownGood.select(KnownGood.q.fmName == pn )
        if packages.count():
            fullName = packages[0].portageCategory + "/" + packages[0].packageName
        else:
            fullName = "No matches found!"

        template = Template('''
            <b>Edit Portage name for:</b> $pn
            <table>
            <tr> <th>Existing match</th> <th>New package category</th> <th>New package name</tr>

            <tr class="alt">
            <td>$fullName </td>
            <td>
            <form name='add_known' action="/meatoo/known_submit" method=post>
            <input type='input' name='new_cat' value=""></td>
            <td><input type='input' name='new_pn' value=""></td>
            <input type='hidden' name='fmpn' value="$pn">
            </tr>
            </table>
            <center><input type='submit' value="Submit"></center>
            </form>
            ''', [locals(), globals()])
        return template.respond()
    
    @cherrypy.expose
    @needsLogin
    def add_known(self, pn, *args, **kwargs):
        """Show form for editing known matches"""
        yield header()
        yield self.add_known_form(pn)
        yield footer()

		
    def known_submit(self, new_cat="", new_pn="", fmpn=""):
        """Add submitted known match to db"""
        if not new_pn or not new_cat:
            # FIXME - these should really be a standard error form
            yield "No package specified!"
            return
        good = KnownGood.select(KnownGood.q.fmName == fmpn )
        if good.count():
            # found existing good
            try:
                good[0].set(packageName = new_pn,
                    portageCategory = new_cat)
            except:
                yield "Failed to update database!"
                return
        else:
            # add new known-good 
           try:
                g=KnownGood(packageName = new_pn,
                    portageCategory = new_cat,
                    fmName = fmpn)
           except:
               yield "Failed to update database!"
               return

        packages = Packages.select(Packages.q.fmName == fmpn )
        try:
            packages[0].set(packageName = new_pn,
                    portageCategory = new_cat)
        except:
                yield "Failed to update database!"
                return

        yield header()
        yield """<b>Success!</b> Go <a href="/meatoo">home</a>"""
        yield footer()
        
    known_submit.exposed = True

    @cherrypy.expose
    @needsLogin
    def login(self, *args, **kwargs):
        """Show form for editing known matches"""
        #print "DEBUG", cherrypy.request.headerMap.get('Referer','/')
        #FIXME: We should send them back to the page they were:
        httptools.redirect("/")

    def logout(self):
        yield header()
        try:
            del cherrypy.session['userid']
            yield "<br><b>You are logged out.</b><br>"
        except:
            yield "<br><b>You are not logged out. This is a known bug.</b><br>"
        yield footer()

    def index(self, verbose = None, login = None):
        """Main index.html page"""
        yield header()
        yield self.body(verbose, login)
        yield footer()
    index.exposed = True

    def rss(self, herd = ""):
        """Generate dynamic RSS feed"""
        if not herd:
            return """No herd specified."""
        packages = Packages.select(LIKE(Packages.q.maintainerName, '%' +  herd + '%') )
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

    rss.exposed = True

