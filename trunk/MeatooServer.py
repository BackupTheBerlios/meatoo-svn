
import datetime
from time import *
import tempfile
import ConfigParser
import types

import cherrypy
from cherrypy.lib import cptools
from cherrypy.lib import httptools
from Cheetah.Template import Template

import accounts
import utils
import templates
from sections import *
from meatoodb import *
from auth import *
from herds import *

class exposed(type):
   def __init__(cls, name, bases, dict):
      super(exposed, cls).__init__(name, bases, dict)
      for name, value in dict.iteritems():
        if type(value)==types.FunctionType and not name.startswith('_'):
           value.exposed = True

class MyServer(cptools.PositionalParametersAware):

    """Server class for meatoo"""

    __metaclass__ = exposed
    def __init__(self, config):
        cptools.PositionalParametersAware.__init__(self)
        self.config = config
        self._body_tmpl = templates.body()
        self._search_tmpl = templates.search()

    def index(self, verbose = None):
        """Main index.html page"""
        #verbose=1 will show you sql id's for debugging
        #For debugging, seeing cookies etc:
        print cherrypy.request.headerMap
        week = utils.get_days()
        packages = Packages.select(OR(Packages.q.latestReleaseDate == week[0],
                                    Packages.q.latestReleaseDate == week[1],
                                    Packages.q.latestReleaseDate == week[2],
                                    Packages.q.latestReleaseDate == week[3],
                                    Packages.q.latestReleaseDate == week[4]
                                    ))
        packages = packages.orderBy('latestReleaseDate').reversed()
        herds = Herds.select()
        try:
            my_herds = cherrypy.session['herds'].split(" ")
        except:
            my_herds = None
        self._body_tmpl.herds = herds
        self._body_tmpl.week = week
        self._body_tmpl.my_herds = my_herds
        self._body_tmpl.packages = packages
        self._body_tmpl.verbose = verbose
        yield header()
        yield self._body_tmpl.respond()
        yield footer()

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
        yield header_top()
        yield "<table class='admin'><tr><td>"
        yield pn + "-" +  ver + " ignored.<br><br>"
        yield "Go <a href='/meatoo'>back</a>"
        yield "</td></tr></table>"
        yield footer()

    @needsLogin
    def ignore(self, id, *args, **kwargs):
        """Ignore particular version of pkg"""
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
        yield header_top()
        yield template.respond()
        yield footer()

    def signup(self):
        """Return search results"""
        yield header_top()
        yield '''
             <form method="get" action="/meatoo/signup_send/">
             <div>
              <h1 class="admin">Meatoo Signup</h1>
              <table class="admin"><tr><td>
              Currently only Gentoo developers can signup to edit Meatoo entries.<br><br>
              <div>
               <label for="email">Email:</label>
               <input type="text" id="email" name="email" class="textwidget" size="30"
                      value="" />
              </div></div><div><br />
               <input type="submit" value="Register" />
              </div>
             </form>
             </td></tr></table>
        '''
        yield footer()


    def error_form(self, msg, *args, **kwargs):
        """Standard error message form"""
        #TODO: Add optional 'go back' url link
        yield header_top()
        yield "<table class='admin'><tr><td><h1 class='admin'>Error:</h1></td></tr>"
        yield "<tr><td><b>"
        yield msg
        yield "</b></td></tr></table>"
        yield footer()

    def signup_send(self, email, *args, **kwargs):
        if "@" not in email:
            yield self.error_form("Invalid email address.")
            return
        if email.split("@")[1] != "gentoo.org":
            yield self.error_form("Only official Gentoo developers may register.")
            return

        yield header()
        username = email.split("@")[0] 
        password = accounts.get_password()
        if accounts.get_user_passwd(username):
            yield "You already have an account."
            yield footer()
            return
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
        yield """Your password has been emailed."""
        yield footer()

    def search(self, length = "short", srch = "", type = ""):
        """Return search results page. length refers to verbosity. 
        'short' means show only new packages, 'long' means show all"""
        yield header()
        if length == "short":
            if type == 'herd':
                packages = Packages.select(AND \
                            (LIKE(Packages.q.maintainerName, \
                             '%' +  srch + '%'), \
                             Packages.q.fmNewer==1))
            elif type == 'pn':
                packages = Packages.select(AND \
                            (LIKE(Packages.q.packageName, \
                             '%' + srch + '%'), \
                             Packages.q.fmNewer==1))
            elif type == "cat":
                packages = Packages.select(AND \
                            (LIKE(Packages.q.portageCategory, \
                             '%' + srch + '%'), \
                             Packages.q.fmNewer==1))
            else:
                yield "<b>Nothing found for:</b> %s" % srch
        elif length == "long":
            if type == 'herd':
                packages = Packages.select(LIKE \
                            (Packages.q.maintainerName, '%' +  srch + '%') )
            elif type == 'pn':
                packages = Packages.select(LIKE \
                            (Packages.q.packageName, '%' + srch + '%'))
            elif type == "cat":
                packages = Packages.select(LIKE \
                            (Packages.q.portageCategory, '%' + srch + '%'))
            else:
                yield "<b>Nothing found for:</b> %s" % srch
        else: # something weird
            yield "Wrong search type"
            return

        packages = packages.orderBy('latestReleaseDate').reversed()
        self._search_tmpl.srch = srch
        self._search_tmpl.type = type
        self._search_tmpl.packages = packages
        yield self._search_tmpl.respond()
        yield footer()

    @needsLogin
    def add_known(self, pn, *args, **kwargs):
        """Show form for editing known matches"""
        yield header_top()
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
        </form>''', [locals(), globals()])
        yield template.respond()
        yield footer()

    @needsLogin
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
        
    def show_herds(self, *args, **kwargs):
        """Show form for adding and editing herds and troves"""
        yield header()
        yield list_herds()
        yield footer()
        
    @needsLogin
    def add_herd(self, *args, **kwargs):
        """Add a herd"""
        yield header_top()
        template = Template ('''
            <table class="admin"><tr><td>
             <form method="post" action="/meatoo/process_herd/add">
             <div>
              <h1 class="admin">Add a herd</h1>
              Currently only Gentoo developers can modify herd info.<br /><br />
              <div>
               <label for="herd" size="10">Herd name:</label>
               <input type="text" id="herd" name="herd" class="textwidget" size="30"
                      value="" />
              </div></div><div><br />
               <input type="submit" value="Add" />
              </div>
             </form></td></tr></table>''')
        yield template.respond()
        yield footer()

    @needsLogin
    def edit_herd(self, herd, *args, **kwargs):
        """Edit a herd"""
        try:
            h = Herds.select(Herds.q.herd == herd)
        except:
            yield "Failed to connect to db"
            return
        yield header()
        
        template = Template ('''
             <form method="post" action="/meatoo/process_herd/edit">
             <div>
              <h3>Edit a herd</h3>
              Currently only Gentoo developers can modify herd info.<br /><br />
              <div>
               <table><th>Herd Name:</th> <th>Troves:</th>
               #for $herds in $h 
                <tr><td><input type="text" id="herd" name="herd" class="textwidget" size="30" value="$herds.herd" /></td>
               <td><input type="text" id="trove" name="trove" class="textwidget" size="30" value="$herds.trove" />
               <input type="hidden" id="old_herd" name="old_herd" value="$herd" /></td></tr>
               #end for
               </table>
              </div></div><div><br />
               <input type="submit" value="Add" />
              </div>
             </form>
            ''', [locals(), globals()])
        yield template.respond()
        yield footer()
        
    @needsLogin
    def process_herd(self, action, herd, trove="", old_herd="", *args, **kwargs):
        """Process add/edit herd request. Action is add or edit"""
        yield header()
        if action == "add":
            h = Herds.select(Herds.q.herd == herd)
            if h.count():
                yield "Herd with that name already exists"
            else:
                yield do_add(herd)
        elif action == "edit":
            h = Herds.select(Herds.q.herd == old_herd)
            if not h.count():
                yield "No such herd"
            else:
                yield do_edit(herd, trove, old_herd)
        else:
            yield "Wrong action"
        yield footer()

    @needsLogin
    def options(self, *args, **kwargs):
        yield header_top()
        yield "<table class='admin'><tr><td><h1 class='admin'>Options</h1>"
        yield "<a href='/meatoo/change_passwd'>Change password<br></a>"
        yield "<a href='/meatoo/lost_passwd'>Lost your password?<br></a>"
        yield "</td></tr></table>"
        yield footer()

    @needsLogin
    def login(self, *args, **kwargs):
        """Go to front page if login succeeds."""
        utils.set_herd_session()
        httptools.redirect("/")

    def logout(self):
        """Logout and goto / """
        cherrypy.session['userid'] = None
        cherrypy.session['herds'] = None
        httptools.redirect("/")
    
    def rss(self, herd = ""):
        """Generate dynamic RSS feed"""
        if not herd:
            return """No herd specified."""
        packages = Packages.select(LIKE(Packages.q.maintainerName, '%' +  herd + '%') )
        utils.generate_rss(packages)

