
'''

accounts.py - Functions for accessing user accounts db


'''


import pgen

from meatoodb import *


def get_user_passwd(username):
    """Return password for given username"""
    user = Users.select(Users.q.user==username)
    if user.count():
        return user[0].password
    else:
        return None

def add_user(username, passwd):
    """Add new user to db"""
    new_user = Users( user = username, password = passwd)

def get_password():
    """Return random password"""
    return pgen.Pgenerate().password


