
"""

herds.py - All you need to know about herds.

This sofware is Copyright 2005 released
under the terms of the GNU Public License Version 2

Original author and lead developer: Rob Cakebread
Contributor: Renat Lumpau

"""

from Cheetah.Template import Template

from commands import getstatusoutput


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

def get_dev_herds(dev):
    """Return all herds for Gentoo dev"""
    cmd = "herdstat -q -d %s" % dev
    status, output = getstatusoutput(cmd)
    if status:
        return
    return output.splitlines()


