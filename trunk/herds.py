
"""

herds.py - All you need to know about herds.

This sofware is Copyright 2005 released
under the terms of the GNU Public License Version 2

Original author and lead developer: Rob Cakebread
Contributor: Renat Lumpau

"""

from Cheetah.Template import Template

from commands import getstatusoutput

from meatoodb import *


def list_herds():
    """Output a list of existing herds"""
    herds = Herds.select()
    if herds.count():
        template = Template('''
        <p><a href="/meatoo/add_herd">Add</a> a herd</p>
        <table><th>Herd</th> <th>Trove id*</th></tr>
        #for herd in $herds
         <tr><td><a href="/meatoo/edit_herd/$herd.herd">$herd.herd</a></td>
          <td>$herd.trove</td>
        #end for
        </table>
        <p>* Comma-separated</p>
        ''', [locals(), globals()])
    else:
        template = Template('''
        <p><a href="/meatoo/add_herd">Add</a> a herd</p>
        <b>No herds found</b>''')
    yield template.respond()
    
def do_add(herd):
    """Actually add herd"""
    try:
        h = Herds(herd = herd, trove = "")
        template = Template ('''<b>Success!</b> <a href="/meatoo/edit_herd/$herd ">Edit</a> herd you just added''', [locals(), globals()])
    except:
        template = Template ('''<p>Error updating database.</p>''')
    return template.respond()
    
def do_edit(new_herd, new_trove, old_herd):
    """Actually edit herd"""
    try:
        if new_herd != old_herd:
            if Herds.select(Herds.q.herd == new_herd).count():
                yield "Herd with that name already exists"
                return
        H = Herds.select(Herds.q.herd == old_herd)
        H[0].set(herd = new_herd, trove = new_trove)
        template = Template ('''<b>Success!</b> <a href="/meatoo/edit_herd/$new_herd ">Edit</a> herd you just added''', [locals(), globals()])
    except:
        template = Template ('''<p>Error updating database.</p>''')
    yield template.respond()

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


