#!/usr/bin/env python

"""

me2dload.py

Downloads and parses freshmeat's RDF file then pickles
needed data in a dictionary.


This sofware is Copyright 2005 released
under the terms of the GNU Public License Version 2

Original author and lead developer: Rob Cakebread
Contributor: Renat Lumpau

"""

import optparse
import sys
import os
from commands import getstatusoutput
import cPickle
import urllib
import portage

from cElementTree import iterparse
import portage


RDF_FILE = "/var/tmp/meatoo/fm-projects.rdf"
RDF_REMOTE = "http://download.freshmeat.net/backend/fm-projects.rdf.bz2"
FM_DICT = "/var/tmp/meatoo/fmdb"
TREE_FILE = "/var/tmp/meatoo/porttree"


def cleanup():
    """Removes old temp files"""
    if os.path.exists(RDF_FILE):
        os.unlink(RDF_FILE)
    if os.path.exists(FM_DICT):
        os.unlink(FM_DICT)

def download_fm():
    """Download and uncompress RDF file from freshmeat.net"""
    cleanup()
    fm = urllib.urlopen(RDF_REMOTE)
    rdf_buff = fm.read()
    file_out = open("%s.bz2" % RDF_FILE, "w").write(rdf_buff)

    os.system("bunzip2 %s.bz2" % RDF_FILE)

def parse_rdf(filename):
    """Parse given fm rdf"""
    f = {}
    for event, elem in iterparse(open(filename, "r")):
        if elem.tag == "project_id":
            project_id = int(elem.text)
            elem.clear()
        elif elem.tag == "projectname_short":
            projectname_short = "%s" % elem.text
            elem.clear()
        elif elem.tag == "desc_short":
            desc_short = "%s" % elem.text
            elem.clear()
        elif elem.tag == "latest_release_version":
            latest_release_version = "%s" % elem.text
            elem.clear()
        elif elem.tag == "url_homepage":
            url_homepage = "%s" % elem.text
            elem.clear()
        elif elem.tag == "url_changelog":
            url_changelog = "%s" % elem.text
            elem.clear()
        elif elem.tag == "latest_release_date":
            latest_release_date = "%s" % elem.text[0:10]
            if elem.text[0:4] == "2005" or elem.text[0:4] == "2004":
                f[projectname_short] = {'id': project_id,
                                'descShort': desc_short,
                                'fmName': projectname_short,
                                'latestReleaseVersion': latest_release_version,
                                'urlHomepage': url_homepage,
                                'urlChangelog': url_changelog,
                                'latestReleaseDate': latest_release_date
                                }
            elem.clear()
    file = open(FM_DICT, 'w')
    cPickle.dump(f, file)

def pickle_tree():
    """Pickles entire Portage tree, including overlays."""
    # is there an easy way to avoid returning overlays?
    if os.path.exists(TREE_FILE):
        os.unlink(TREE_FILE)
    file = open(TREE_FILE, 'w')
    cPickle.dump(portage.portdb.cp_all(), file)

if __name__ == '__main__':

    optParser = optparse.OptionParser()
    optParser.add_option( "-d", action="store_true", dest="dload", default=False,
                            help="Download freshmeat RDF file.")
    optParser.add_option( "-p", action="store_true", dest="parse", default=False,
                            help="Parse and pickle freshmeat RDF file.")
    optParser.add_option( "-t", action="store_true", dest="tree", default=False,
                            help="Pickle portage tree.")
    options, remainingArgs = optParser.parse_args()
    if len(sys.argv) == 1:
        optParser.print_help()
        sys.exit()

    if options.dload:
        download_fm()

    if options.parse:
        parse_rdf(RDF_FILE)
    
    if options.tree:
        pickle_tree()
