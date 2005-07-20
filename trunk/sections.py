
from Cheetah.Template import Template
import cherrypy


def header():
    """ Yields header html"""
    logged = False
    if cherrypy.session.get('userid', None):
        logged = True

    template = Template("""
    <html><head><title>Meatoo: Freshmeat-Gentoo Updates</title>
      <link href="/meatoo/static/stylin.css" media="screen" rel="Stylesheet" type="text/css" />
      <link href="http://gentooexperimental.org/meatoo/static/meatoo.xml" rel="alternate" type="application/rss+xml" title="Meatoo Freshmeat-Gentoo RSS Feed" />
    </head>
    <body>
    <table class="table" cellspacing=0 cellpadding=0 border=0>
    <tr border=0><td border=0><a href="/meatoo"><img border=0 src="/meatoo/static/meatoo.png"></a></td>
    <td border=0 align="right"><p align="right">
    <a href="/meatoo/static/faq.html">FAQ</a> | Advanced Search |
    #if $logged:
        <a href="/meatoo/logout"> Logout</a> |
        <a href="/meatoo/options"> Options</a>
    #else
        <a href="/meatoo/login">Login</a>
    #end if
    </p>
    </td>
    </tr>
    <tr><td colspan="2"><b>Find Gentoo packages needing a version bump by checking the latest Freshmeat releases.</b></td></tr>
    </table>

    <table>
    <tr>
        <td>Search by Herd/Maintainer
            <form class="search" id="search" name='search' action="/meatoo/search" method=post>
            <input type='input' name='srch' value="">
            <input type='hidden' name='type' value="herd">

        </form>
        </td>
        <td>Search by Package Name
            <form name='search' action="/meatoo/search" method=post>
            <input type='input' name='srch' value="">
            <input type='hidden' name='type' value="pn">
        </form>
        </td>
        <td>Search by Category
            <form name='search' action="/meatoo/search" method=post>
            <input type='input' name='srch' value="">
            <input type='hidden' name='type' value="cat">
        </form>
        </td>
    </tr>
    </table> 
    <br>
    """, [locals(), globals()])
    return template.respond()

    


def footer():
    """ Yields footer html"""

    return """
        <br>
        <br>
        <hr>
        <a href="http://freshmeat.net">
        <img align="right" border=0 src="/meatoo/static/link_button_3.gif" alt="freshmeat"></a>
        </body>
        </html>
        """

