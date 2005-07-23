
'''

accounts.py - Functions for accessing user accounts db


'''


import pgen
import cherrypy

from meatoodb import *


def get_user_passwd(username):
    """Return password for given username"""
    user = Users.select(Users.q.user==username)
    if user.count():
        return user[0].password

def add_user(username, passwd):
    """Add new user to db"""
    new_user = Users( user = username, password = passwd)

def get_password():
    """Return random password"""
    return pgen.Pgenerate().password

def get_logged_username():
    """If user is logged in return username"""
    try:
        return cherrypy.session['userid'] 
    except:
        pass # Not logged in

