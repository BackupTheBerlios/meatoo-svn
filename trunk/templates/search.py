#!/usr/bin/env python


"""
Autogenerated by CHEETAH: The Python-Powered Template Engine
 CHEETAH VERSION: 0.9.17
 Generation time: Sat Jul 23 00:02:19 2005
   Source file: templates/search.tmpl
   Source file last modified: Fri Jul 22 23:59:50 2005
"""

__CHEETAH_genTime__ = 'Sat Jul 23 00:02:19 2005'
__CHEETAH_src__ = 'templates/search.tmpl'
__CHEETAH_version__ = '0.9.17'

##################################################
## DEPENDENCIES

import sys
import os
import os.path
from os.path import getmtime, exists
import time
import types
import __builtin__
from Cheetah.Template import Template
from Cheetah.DummyTransaction import DummyTransaction
from Cheetah.NameMapper import NotFound, valueForName, valueFromFrameOrSearchList
import Cheetah.Filters as Filters
import Cheetah.ErrorCatchers as ErrorCatchers

##################################################
## MODULE CONSTANTS

try:
    True, False
except NameError:
    True, False = (1==1), (1==0)
VFFSL=valueFromFrameOrSearchList
VFN=valueForName
currentTime=time.time

##################################################
## CLASSES

class search(Template):
    """
    
    Autogenerated by CHEETAH: The Python-Powered Template Engine
    """

    ##################################################
    ## GENERATED METHODS


    def __init__(self, *args, **KWs):
        """
        
        """

        Template.__init__(self, *args, **KWs)

    def respond(self,
            trans=None,
            dummyTrans=False,
            VFFSL=valueFromFrameOrSearchList,
            VFN=valueForName,
            getmtime=getmtime,
            currentTime=time.time):


        """
        This is the main method generated by Cheetah
        """

        if not trans:
            trans = DummyTransaction()
            dummyTrans = True
        write = trans.response().write
        SL = self._searchList
        filter = self._currentFilter
        globalSetVars = self._globalSetVars
        
        ########################################
        ## START - generated method body
        
        write('\n<b>Search results for:</b> ')
        write(filter(VFFSL(SL,"srch",True), rawExpr='$srch')) # from line 2, col 28.
        write('\n<p>Show <a href="/meatoo/search/short/')
        write(filter(VFFSL(SL,"srch",True), rawExpr='$srch')) # from line 3, col 39.
        write('/')
        write(filter(VFFSL(SL,"type",True), rawExpr='$type')) # from line 3, col 45.
        write('">recent</a>\nor <a href="/meatoo/search/long/')
        write(filter(VFFSL(SL,"srch",True), rawExpr='$srch')) # from line 4, col 33.
        write('/')
        write(filter(VFFSL(SL,"type",True), rawExpr='$type')) # from line 4, col 39.
        write('''">all</a> releases</p>
<table>
<tr> <th>Portage Name</th> <th>Portage Version</th>
<th>Freshmeat Version</th> <th>Freshmeat Release Date</th> 
<th>Maintainers</th></tr>

''')
        for pkg in VFFSL(SL,"packages",True):
            write('    <tr class="alt">\n    <td><a href="http://packages.gentoo.org/search/?sstring=%5E')
            write(filter(VFFSL(SL,"pkg.packageName",True), rawExpr='$pkg.packageName')) # from line 12, col 64.
            write('%24">\n    ')
            write(filter(VFFSL(SL,"pkg.portageCategory",True), rawExpr='$pkg.portageCategory')) # from line 13, col 5.
            write('/')
            write(filter(VFFSL(SL,"pkg.packageName",True), rawExpr='$pkg.packageName')) # from line 13, col 26.
            write('</a>\n    <a class="nav" href="/meatoo/ignore/')
            write(filter(VFFSL(SL,"pkg.id",True), rawExpr='$pkg.id')) # from line 14, col 41.
            write('''" title="Ignore this version of this package.">
    <img border=0 src="/meatoo/static/edit.png" alt="Ignore"></a>

    <a class="nav" href="/meatoo/add_known/''')
            write(filter(VFFSL(SL,"pkg.fmName",True), rawExpr='$pkg.fmName')) # from line 17, col 44.
            write('" title="Edit Portage name">\n    <img border=0 src="/meatoo/static/edit.gif"></a>\n    <a class="nav" href="')
            write(filter(VFFSL(SL,"pkg.urlHomepage",True), rawExpr='$pkg.urlHomepage')) # from line 19, col 26.
            write('" title="Project Homepage">\n    <img border=0 src="/meatoo/static/home.png"></a></td>\n')
            if pkg.fmNewer:
                write('        <td class="hilite">')
                write(filter(VFFSL(SL,"pkg.portageVersion",True), rawExpr='$pkg.portageVersion')) # from line 22, col 28.
                write('</td>\n')
            else:
                write('        <td>')
                write(filter(VFFSL(SL,"pkg.portageVersion",True), rawExpr='$pkg.portageVersion')) # from line 24, col 13.
                write('</td>\n')
            write('    <td><a href="http://freshmeat.net/projects/')
            write(filter(VFFSL(SL,"pkg.packageName",True), rawExpr='$pkg.packageName')) # from line 26, col 48.
            write('/">')
            write(filter(VFFSL(SL,"pkg.latestReleaseVersion",True), rawExpr='$pkg.latestReleaseVersion')) # from line 26, col 67.
            write('</a>\n    <a class="nav" href="http://freshmeat.net/redir/')
            write(filter(VFFSL(SL,"pkg.packageName",True), rawExpr='$pkg.packageName')) # from line 27, col 53.
            write('/')
            write(filter(VFFSL(SL,"pkg.urlChangelog",True), rawExpr='$pkg.urlChangelog')) # from line 27, col 70.
            write('/url_changelog/" title="changelog">\n    <img border=0 src="/meatoo/static/changelog.gif"></a>\n    </td><td>')
            write(filter(VFFSL(SL,"pkg.latestReleaseDate",True), rawExpr='$pkg.latestReleaseDate')) # from line 29, col 14.
            write('</td>\n    <td>')
            write(filter(VFFSL(SL,"pkg.maintainerName",True), rawExpr='$pkg.maintainerName')) # from line 30, col 9.
            write('</td>\n    </tr>\n')
        write('</table>\n\n')
        
        ########################################
        ## END - generated method body
        
        if dummyTrans:
            return trans.response().getvalue()
        else:
            return ""
        
    ##################################################
    ## GENERATED ATTRIBUTES


    __str__ = respond

    _mainCheetahMethod_for_search= 'respond'


# CHEETAH was developed by Tavis Rudd, Mike Orr, Ian Bicking and Chuck Esterbrook;
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org

##################################################
## if run from command line:
if __name__ == '__main__':
    search().runAsMainProgram()

