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

from time import localtime
import optparse
import sys
import os
import cPickle
import urllib

from cElementTree import iterparse
import portage


RDF_FILE = "/var/tmp/meatoo/fm-projects.rdf"
TROVES_FILE = "/var/tmp/meatoo/fm-trove.rdf"
RDF_REMOTE = "http://download.freshmeat.net/backend/fm-projects.rdf.bz2"
TROVES_REMOTE = "http://download.freshmeat.net/backend/fm-trove.rdf"
FM_DICT = "/var/tmp/meatoo/fmdb"
TROVES_DICT = "/var/tmp/meatoo/trdb"
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

def download_troves():
    """Download troves file from freshmeat.net"""
    if os.path.exists(TROVES_DICT):
        os.unlink(TROVES_DICT)
    fm = urllib.urlopen(TROVES_REMOTE)
    rdf_buff = fm.read()
    file_out = open(TROVES_FILE, "w").write(rdf_buff)

def get_last_four_years():
    """Returns tuple of the last four years"""
    current_year = localtime()[0]
    return (current_year, current_year - 1, current_year -2, current_year -3)

def parse_rdf(filename):
    """Parse given fm rdf"""
    f = {}
    trove = ""
    #Number of years to check back in time.
    years = get_last_four_years()
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
            elem.clear()
        elif elem.tag == "descriminators":
            t = ""
            for trove in elem[:]:
                t = "%s %s" % (t, trove.text)
            #If it hasn't been updated in four years, screw it.
            if  latest_release_date[0:4] in years:
                    f[projectname_short] = {'id': project_id,
                                'descShort': desc_short,
                                'fmName': projectname_short,
                                'latestReleaseVersion': latest_release_version,
                                'urlHomepage': url_homepage,
                                'urlChangelog': url_changelog,
                                'latestReleaseDate': latest_release_date,
                                'troveId': t
                                }
            elem.clear()
    file = open(FM_DICT, 'w')
    cPickle.dump(f, file)

def parse_troves(filename):
    """Parse given fm troves"""
    f = {}
    for event, elem in iterparse(open(filename, "r")):
        if elem.tag == "id":
            id = int(elem.text)
            elem.clear()
        elif elem.tag == "name":
            name = "%s" % elem.text
            elem.clear()
            f[id] = {'id': id,
                        'name': name
                        }
            elem.clear()
    file = open(TROVES_DICT, 'w')
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
    optParser.add_option( "-D", action="store_true", dest="trdload", default=False,
                            help="Download freshmeat troves file.")
    optParser.add_option( "-P", action="store_true", dest="trparse", default=False,
                            help="Parse and pickle freshmeat troves file.")
    optParser.add_option( "-A", action="store_true", dest="all", default=False,
                            help="Download freshmeat RDF file.")
    options, remainingArgs = optParser.parse_args()
    if len(sys.argv) == 1:
        optParser.print_help()
        sys.exit()

    if options.all:
        options.dload = True
        options.parse = True
        options.tree = True
        options.trdload = True
        options.trparse = True
    if options.dload:
        download_fm()

    if options.parse:
        parse_rdf(RDF_FILE)
    
    if options.tree:
        pickle_tree()
    
    if options.trdload:
        download_troves()

    if options.trparse:
        parse_troves(TROVES_FILE)
