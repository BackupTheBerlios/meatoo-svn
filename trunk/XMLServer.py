
from time import *

import PyRSS2Gen

import meatoodb


class MyServer:
    """XML-RPC methods"""

    def __init__(self, config):
        self.config = config

    def _parsePackages(self, pkgs):
        """Parse Packages into a list of lists"""
        if not pkgs.count():
            return [["", "", "", "", "", "", "", "", "", ""]]

        results = []
        i = 0
        for dummy in range(pkgs.count()):
            results.append([pkgs[i].portageCategory,
                            pkgs[i].packageName,
                            pkgs[i].portageDesc,
                            pkgs[i].portageVersion,
                            pkgs[i].maintainerName,
                            pkgs[i].descShort,
                            pkgs[i].latestReleaseVersion,
                            pkgs[i].latestReleaseDate,
                            pkgs[i].urlHomepage,
                            pkgs[i].urlChangelog
                            ])

            i += 1
        return results

    def getLatest(self):
        """Get today's meat"""
        now = gmtime(mktime(gmtime()))
        date = "%s-%02d-%02d" % (now[0], now[1], now[2])
        return self.getDate(date)
    getLatest.exposed = True

    def getDate(self, date):
        """Get by Freshmeat release date"""
        pkgs = Packages.select(Packages.q.latestReleaseDate == date)
        return self._parsePackages(pkgs)
    getDate.exposed = True

    def getPackage(self, pn):
        """Get by exact package name (No category)"""
        pkgs = Packages.select(Packages.q.packageName == pn)
        return self._parsePackages(pkgs)
    getPackage.exposed = True

    def getPartialPackage(self, pn):
        """Get by partial package name (No category)"""
        pkgs = Packages.select(LIKE(Packages.q.packageName, '%' + pn + '%'))
        return self._parsePackages(pkgs)
    getPartialPackage.exposed = True

    def getCatPackage(self, catpn):
        """Get by exact category/package name"""
        if "/" not in catpn:
            return [["", "", "", "", "", "", "", "", "", ""]]
        category, pn = catpn.split("/")
        pkgs = Packages.select(AND (Packages.q.packageName == pn, Packages.q.portageCategory == category) )
        return self._parsePackages(pkgs)
    getCatPackage.exposed = True

    def getMaintainer(self, maintainer):
        """"Get packages by herd or maintainer email address. Not an exact match."""
        pkgs = Packages.select(LIKE(Packages.q.maintainerName, '%' +  maintainer + '%') )
        pkgs = pkgs.orderBy('latestReleaseDate')
        return self._parsePackages(pkgs)
    getMaintainer.exposed = True

