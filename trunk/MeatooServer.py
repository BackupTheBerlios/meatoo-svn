
import datetime
from time import *
import tempfile
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

class exposed(type):

   """Metaclass for exposing all methods. Only put methods
      in MeatooServer you want exposed. All else go in utils.py
      or other specific places such as herds.py etc."""

   def __init__(cls, name, bases, dict):
      super(exposed, cls).__init__(name, bases, dict)
      for name, value in dict.iteritems():
        if type(value)==types.FunctionType and not name.startswith('_'):
           value.exposed = True

class MyServer(cptools.PositionalParametersAware):

    """Server class for meatoo"""

    __metaclass__ = exposed

    def __init__(self, config, debug, verbose):
        cptools.PositionalParametersAware.__init__(self)
        self.config = config
        self.debug = debug
        self.verbose = verbose
        self._body_tmpl = templates.body()
        self._search_tmpl = templates.search()
        self._showtrove_tmpl = templates.showtrove()
        self._change_passwd_tmpl = templates.change_passwd()

    #FIXME: Its tricky turning this on based on a config
    #or optparser option. Any ideas?
    #def _cpOnError():
    #    """Enter pdb on tracebacks"""
    #    import pdb
    #    pdb.set_trace()
    #    cherrypy._cputil._cpOnError()
    #_cpOnError = staticmethod(_cpOnError)

    def plain_page(self, content):
        """Generic page with plain header/footer"""
        #FIXME: Use CSS and make this look nice
        #Use compiled Cheetah template?
        #Add header arg for titlebar etc.
        yield header_top()
        yield "<table class='admin'><tr><td>"
        yield content
        yield "</td></tr></table>"
        yield footer()

    def error_form(self, msg, *args, **kwargs):
        """Standard error message form"""
        #TODO: Add optional 'go back' url link
        content = "<tr><td><h1 class='admin'>Error:</h1></td></tr>"
        content += "<tr><td>"
        content += msg
        content += "</td></tr></table>"
        yield self.plain_page(content)

    def index(self, verbose = None):
        """Main index.html page"""
        #verbose=1 will show you sql id's for debugging
        #For debugging, seeing cookies etc:
        if self.verbose:
            print cherrypy.request.headerMap
        week = utils.get_days()
        
        #FIXME: Show either pkgs needing bump or all fm pkgs
        packages = Packages.select(AND(OR(Packages.q.latestReleaseDate == week[0],
                                    Packages.q.latestReleaseDate == week[1],
                                    Packages.q.latestReleaseDate == week[2],
                                    Packages.q.latestReleaseDate == week[3],
                                    Packages.q.latestReleaseDate == week[4]
                                    ), Packages.q.fmNewer==1))

        #packages = Packages.select(OR(Packages.q.latestReleaseDate == week[0],
        #                            Packages.q.latestReleaseDate == week[1],
        #                            Packages.q.latestReleaseDate == week[2],
        #                            Packages.q.latestReleaseDate == week[3],
        #                            Packages.q.latestReleaseDate == week[4]
        #                            ))
        packages = packages.orderBy('latestReleaseDate').reversed()
        try:
            my_herds = cherrypy.session['herds'].split(" ")
        except:
            my_herds = None
        
        try:
            troves = cherrypy.session['troves'].split(" ")
        except:
            troves = None

        tr = {}
        if troves:
            for t in troves:
                a = Troves.select(Troves.q.fId == t)
                tr[t] = a[0].name

        self._body_tmpl.troves = tr 
        self._body_tmpl.username = accounts.get_logged_username()
        self._body_tmpl.week = week
        self._body_tmpl.my_herds = my_herds
        self._body_tmpl.packages = packages
        self._body_tmpl.verbose = verbose
        yield header()
        yield self._body_tmpl.respond()
        yield footer()

    @needsLogin
    def ignore(self, id, *args, **kwargs):
        """Ignore particular version of pkg"""
        pkg = Packages.get(id)
        template = Template('''
            <form method="get" action="/meatoo/ignore_action/">
            <div>
            <b>Ignore version $pkg.latestReleaseVersion of $pkg.packageName</b>
            <br>
            <br>This will ignore this particular freshmeat release version,
            <b>not</b> the entire pacakge.</b><br><br>
            Freshmeat Release Date: $pkg.latestReleaseDate<br><br>
            <a href="http://packages.gentoo.org/search/?sstring=%5E$pkg.packageName%24">
            $pkg.portageCategory/$pkg.packageName-$pkg.portageVersion</a> [
            <a class="nav" href="http://freshmeat.net/projects/$pkg.packageName/"
            title="Freshmeat Latest Release">$pkg.latestReleaseVersion</a> ]
            </div><div><br />
            <input type="submit" value="Ignore" />
            <input type='hidden' name='pn' value='$pkg.packageName'>
            <input type='hidden' name='ver' value='$pkg.latestReleaseVersion'>
            </div>
            </form>
        ''', [locals(), globals()])
        content = template.respond()
        yield self.plain_page(content)

    @needsLogin
    def ignore_action(self, pn, ver):
        """Process ignore form"""
        try:
            pkg = Packages.select(AND(Packages.q.packageName == pn,
                                  Packages.q.latestReleaseVersion == ver))
            pkg[0].destroySelf()
            if self.verbose:
                print "Deleted match:", pn
        except:
            pass
        ignore = Ignores(packageName = pn, latestReleaseVersion = ver)
        username = accounts.get_logged_username()
        timestamp = asctime(gmtime())
        msg = "%s %s IGNORE %s-%s" % (timestamp, username, pn, ver)
        utils.admin_log_msg(msg)
        template = Template('''Freshmeat version $ver of $pn ignored.
                                <br><br>Go <a href='/meatoo'>back</a>''',
                                [locals(), globals()])
        content = template.respond()
        yield self.plain_page(content)

    def signup(self):
        """New account signup form"""
        content = '''
             <form method="get" action="/meatoo/signup_send/">
             <div>
              <h1 class="admin">New Account</h1>
              <table class="admin"><tr><td>
              Currently only Gentoo developers can signup to edit Meatoo
              entries.<br><br>
              <div>
               <label for="email">Email:</label>
               <input type="text" id="address" name="address" 
                    class="textwidget" size="30" value="" />
              </div></div><div><br />
               <input type="submit" value="Register" />
              </div>
             </form>
             </td></tr></table>'''
        yield self.plain_page(content)

    def signup_send(self, address, *args, **kwargs):
        """Send generated password for new account to user"""
        yield self.plain_page(utils.send_new_passwd(address))

    @needsLogin
    def show_trove(self, trove):
        """Return search results by trove"""
        yield header()
        yield '''<h3> This is a list of Freshmeat releases  in the past week that belong to one of the Freshmeat troves you specified</h3><br />'''
        packages = Allfm.select(LIKE(Allfm.q.troveId, '%' + trove + '%'))
        packages = packages.orderBy('latestReleaseDate').reversed()
        
        a = Troves.select(Troves.q.fId == trove)
        self._showtrove_tmpl.trove = trove
        self._showtrove_tmpl.descr = a[0].name
        self._showtrove_tmpl.packages = packages
        yield self._showtrove_tmpl.respond()
        yield footer()
        
    @needsLogin
    def show_all_troves(self):
        """Return search results for all user troves"""
        
        troves = cherrypy.session['troves']
        yield header() 
        yield '''<h3> This is a list of Freshmeat releases  in the past week that belong to one of the Freshmeat troves you specified</h3><br />'''
        for t in troves.split():
            packages = Allfm.select(LIKE(Allfm.q.troveId, '%' + t + '%'))
            packages = packages.orderBy('latestReleaseDate').reversed()
            a = Troves.select(Troves.q.fId == t)

            self._showtrove_tmpl.descr = a[0].name
            self._showtrove_tmpl.trove = t
            self._showtrove_tmpl.packages = packages
            yield self._showtrove_tmpl.respond()
        yield footer()
        
    def search(self, length = "short", srch = "", type = ""):
        """Return search results page. length refers to verbosity. 
        'short' means show only new packages, 'long' means show all"""
        yield header()
        if length == "short":
            if type == 'herd':
                packages = Packages.select(AND(LIKE(Packages.q.maintainerName,
                             '%' +  srch + '%'),
                             Packages.q.fmNewer==1))
            elif type == 'pn':
                packages = Packages.select(AND(LIKE(Packages.q.packageName,
                             '%' + srch + '%'),
                             Packages.q.fmNewer==1))
            elif type == "cat":
                packages = Packages.select(AND(LIKE(Packages.q.portageCategory,
                             '%' + srch + '%'),
                             Packages.q.fmNewer==1))
            else:
                yield "<b>Nothing found for:</b> %s" % srch
        elif length == "long":
            if type == 'herd':
                packages = Packages.select(LIKE(Packages.q.maintainerName,
                            '%' +  srch + '%') )
            elif type == 'pn':
                packages = Packages.select(LIKE(Packages.q.packageName,
                            '%' + srch + '%'))
            elif type == "cat":
                packages = Packages.select(LIKE(Packages.q.portageCategory,
                            '%' + srch + '%'))
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
        packages = KnownGood.select(KnownGood.q.fmName == pn )
        if packages.count():
            fullName = "%s/%s" % (packages[0].portageCategory,
                                  packages[0].packageName)
        else:
            fullName = "No matches found!"
        template = Template('''
            <b>Edit Portage name for:</b> $pn
            <br><br>
            If a Freshmeat package name does not match,
            you can re-map it to a new Gentoo category and package name.
            <br><br>
            <table>
            <tr> <th>Existing match</th> 
            <th>New package category</th> <th>New package name</tr>
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
        yield self.plain_page(template.respond())

    @needsLogin
    def known_submit(self, new_cat="", new_pn="", fmpn=""):
        """Add submitted known match to db"""
        username = accounts.get_logged_username()
        timestamp = asctime(gmtime())
        msg = "%s %s CHANGE " % (timestamp, username)
        if not new_pn or not new_cat:
            yield self.error_form("No package specified!")
            return
        good = KnownGood.select(KnownGood.q.fmName == fmpn )
        if good.count():
            # found existing good
            try:
                good[0].set(packageName = new_pn,
                    portageCategory = new_cat)
                msg += "%s-%s NEW_PN NEW_CAT\n" % (new_pn, new_cat)
            except:
                yield self.error_form("Failed to update database!")
                return
        else:
            # add new known-good 
           try:
                g=KnownGood(packageName = new_pn,
                    portageCategory = new_cat,
                    fmName = fmpn)
                msg += "%s-%s %s NEW_PN NEW_CAT FMNM\n" % (new_pn, new_cat, fmpn)
           except:
               yield self.error_form("Failed to update database!")
               return

        packages = Packages.select(Packages.q.fmName == fmpn )
        try:
            packages[0].set(packageName = new_pn,
                    portageCategory = new_cat)
            msg += "%s-%s NEW_PN NEW_CAT\n" % (new_pn, new_cat)
        except:
            yield self.error_form("Failed to update database!")
            return

        utils.admin_log_msg(msg)
        content = "<b>Success!</b><br><br>Go <a href='/meatoo'>home</a>"
        yield self.plain_page(content)
        
    @needsLogin
    def add_user_herd(self, *args, **kwargs):
        """Add user's herd"""
        content = '''
             <form method="post" action="/meatoo/process_user_herd">
             <div>
              <h1 class="admin">Add a herd</h1>
              <div>
               <label for="herd" size="10">Herd name:</label>
               <input type="text" id="herd" name="herd" class="textwidget"
                size="30" value="" />
              </div></div><div><br />
               <input type="submit" value="Add" />
              </div>'''
        yield self.plain_page(content)

    @needsLogin
    def del_user_herd(self, herd):
        """Delete user's herd"""
        username = accounts.get_logged_username()
        u = Users.select(Users.q.user == username)
        if herd in u[0].herdsAuto:
            yield self.error_form('''You are a member of that herd,
                                     which means you cannot delete it from your
                                     Meatoo preferences. Sorry.''')
            return
        elif herd in u[0].herdsUser:
            s = u[0].herdsUser.split()
            s.remove(herd)
            if s:
                u[0].set(herdsUser = " ".join(s))
            else:
                u[0].set(herdsUser = "")
        else: #weird
            yield self.error_form("Couldn't find that herd in your list.")
            return

        utils.set_herd_session()
        content = "<b>Success!</b><br><br>Go <a href='/meatoo'>home</a>"
        yield self.plain_page(content)

    @needsLogin
    def process_user_herd(self, herd, *args, **kwargs):
        """Process add user herd request."""
        
        username = accounts.get_logged_username()
        h = Users.select(Users.q.user == username)
        if h[0]:
            h[0].set(herdsUser = h[0].herdsUser + " " + herd)
        else:
            h[0].set(herdsUser = herd)
        utils.set_herd_session()

        content = "<b>Success!</b><br><br>Go <a href='/meatoo'>home</a>"
        yield self.plain_page(content)
   
    @needsLogin
    def add_user_trove(self, *args, **kwargs):
        """Add user's trove"""
        content = '''
            <table class="admin"><tr><td>
             <form method="post" action="/meatoo/process_user_trove">
             <div><h1 class="admin">Add a trove</h1>
              <br /><p>
              Consult the Freshmeat 
              <a href="http://freshmeat.net/browse/18/">list</a>
              of sub-categories. The number at the end of the URL is the
              trove number.</p>
              <div>
               <label for="trove" size="10">Trove number:</label>
               <input type="text" id="trove" name="trove"
                 class="textwidget" size="30" value="" />
              </div></div><div><br />
               <input type="submit" value="Add" />
              </div>'''
        yield self.plain_page(content)

    @needsLogin
    def del_user_trove(self, trove):
        """Delete user's trove"""
        
        username = accounts.get_logged_username()
        u = Users.select(Users.q.user == username)
        if trove in u[0].troves:
            s = u[0].troves.split()
            s.remove(trove)
            if s:
                u[0].set(troves = " ".join(s))
            else:
                u[0].set(troves = "")
        else: #weird
            yield self.error_form ("Couldn't find that trove in your list.")
            return

        utils.set_troves_session()
        content = "<b>Success!</b><br><br>Go <a href='/meatoo'>home</a>"
        yield self.plain_page(content)

    @needsLogin
    def process_user_trove(self, trove, *args, **kwargs):
        """Process add user trove request."""
        
        username = accounts.get_logged_username()
        h = Users.select(Users.q.user == username)
        if h[0].troves:
            h[0].set(troves = h[0].troves + " " + trove)
        else:
            h[0].set(troves = trove)
        utils.set_troves_session()

        content = "<b>Success!</b><br><br>Go <a href='/meatoo'>home</a>"
        yield self.plain_page(content)

    @needsLogin
    def options(self, *args, **kwargs):
        content = """<h1 class='admin'>Options</h1>
                     <a href='/meatoo/change_passwd'>Change password<br></a>
                     """
        yield self.plain_page(content)

    @needsLogin
    def login(self, *args, **kwargs):
        """Go to front page if login succeeds."""
        utils.set_herd_session()
        utils.set_troves_session()
        httptools.redirect("/")

    def logout(self):
        """Logout and goto / """
        cherrypy.session['userid'] = None
        cherrypy.session['herds'] = None
        cherrypy.session['troves'] = None
        httptools.redirect("/")
    
    def lost_passwd(self):
        """Form for mailing lost passwd"""
        content = """
            <b>Lost password?</b>
            <form method="get" action="/meatoo/lost_passwd_action/">
            <div>
            <br>Enter your Gentoo developer username: 
            <input type='input' name='username' value=""></td>
            <input type="submit" value="Send" />
            </div>
            </form>"""
        yield self.plain_page(content)

    def lost_passwd_action(self, username):
        """Mail lost passwd"""
        utils.mail_lost_passwd(username)
        content = """Password mailed.<br><br>Go <a href='/meatoo'>home.</a>"""
        yield self.plain_page(content)

    @needsLogin
    def change_passwd(self, *args, **kwargs):
        """Change password form"""
        yield self.plain_page(self._change_passwd_tmpl.respond())

    @needsLogin
    def change_passwd_action(self, old_passwd, new_passwd, confirm_passwd, *args, **kwargs):
        username = accounts.get_logged_username()
        password = accounts.get_user_passwd(username)
        if password != old_passwd:
            yield self.error_form('''Old password is incorrect.<br><br>
                                     <a href='/meatoo/change_passwd'>
                                     Try again.</a>''')
            return
        if new_passwd != confirm_passwd:
            yield self.error_form('''New passwords don't match.<br><br>
                                     <a href='/meatoo/change_passwd'>
                                     Try again.</a>''')
            return
        if accounts.change_passwd(username, new_passwd):
            yield self.plain_page("<b>Password changed.</b>")
        else:
            yield self.error_form("Error: Failed to change passwd.")

    def rss(self, herd = ""):
        """Generate dynamic RSS feed"""
        if not herd:
            return """No herd specified."""
        packages = Packages.select(LIKE(Packages.q.maintainerName,
                    '%' +  herd + '%') )
        utils.generate_rss(packages, herd)

