
"""

auth.py - All the authorization code.

This sofware is Copyright 2005 released
under the terms of the GNU Public License Version 2

Original author and lead developer: Rob Cakebread
Contributor: Renat Lumpau

"""

import cherrypy

import accounts
import sections


def needsLogin(fn):
    '''Login decorator: if the user is not logged in, send up a login
    rather than the page content.  Point the login form back to the
    same page to avoid a redirect when the user logs in correctly.
    '''
    def _wrapper(*args, **kwargs):
        if cherrypy.session.get('userid', None):
            # User is logged in; allow access
            return fn(*args, **kwargs)
        else:
            # User isn't logged in yet.
            
            # See if the user just tried to log in
            try:
                submit = kwargs['login']
                username = kwargs['userName']
                password = kwargs['loginPassword']
            except KeyError:
                # No, this wasn't a login attempt.  Send the user to
                # the login "page".
                return loginPage(cherrypy.request.path)

            # Now look up the user id by the username and password
            userid = getUserId(username, password)
            if userid is None:
                # Bad login attempt
                return loginPage(cherrypy.request.path, 'Invalid username or password.')
            # User is now logged in, so retain the userid and show the content
            cherrypy.session['userid'] = userid
            return fn(*args, **kwargs)
    return _wrapper


def getUserId(username, password):
    '''Return True if good password'''
    
    try:
        db_pswd = accounts.get_user_passwd(username)
    except:
        return None
    if db_pswd == password:
        return username
    else:
        return None

def loginPage(targetPage, message=None):
    '''Return login form page '''
    result = []
    result.append(sections.header_top())
    result.append('<table class="admin"><tr><td>')
    result.append('<h1 class="admin">Login</h1>')
    if message is not None:
        result.append('<p>%s</p>' % message)
    result.append('<form action=/meatoo%s method=post>' % targetPage)
    result.append('<p>Username: <input type=text name="userName"></p>')
    result.append('<p>Password: <input type=password name="loginPassword"></p>')
    result.append('<p><input type="submit" name="login" value="Log In"></p>')
    result.append('</form>')
    result.append('<br><a href="/meatoo/signup">New account</a><br><br>')
    result.append("<a href='/meatoo/lost_passwd'>Lost your password?</a>")
    result.append('</td></tr></table>')
    result.append(sections.footer())
    return '\n'.join(result)

