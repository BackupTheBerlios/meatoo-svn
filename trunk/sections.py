
from Cheetah.Template import Template
import cherrypy


def header():
    """Returns logo/links + search bar"""
    return header_top() + search_bar()

def header_top():
    """ Yields logo + links html"""
    logged = False
    if cherrypy.session.get('userid', None):
        logged = True

    template = Template("""
    <html><head><title>Meatoo: Freshmeat-Gentoo Updates</title>
      <link href="/static/stylin.css" media="screen" rel="Stylesheet" type="text/css" />
      <link href="/static/meatoo.xml" rel="alternate" type="application/rss+xml" title="Meatoo Freshmeat-Gentoo RSS Feed" />
    </head>
    <body>
    <table class="table" cellspacing=0 cellpadding=0 border=0>
    <tr border=0><td border=0><a href="/"><img border=0 src="/static/meatoo.png"></a></td>
    <td border=0 align="right"><p align="right">
    <a href="/">Home</a> |
    <a href="/static/faq.html">FAQ</a> | 
    #if $logged:
        <a href="/options"> Options</a> |
        <a href="/logout"> Logout</a> 
    #else
        <a href="/login">Login</a>
    #end if
    </p>
    </td>
    </tr>
    <tr><td colspan="2"><b>Find Gentoo packages needing a version bump by checking the latest Freshmeat releases.</b></td></tr>
    </table>""", [locals(), globals()])
    return template.respond()

def search_bar():
    return """
    <table>
    <tr>
        <td>Search by Herd/Maintainer
            <form class="search" id="search" name='search' action="/search" method=post>
            <input type='input' name='srch' value="">
            <input type='hidden' name='type' value="herd">

        </form>
        </td>
        <td>Search by Package Name
            <form name='search' action="/search" method=post>
            <input type='input' name='srch' value="">
            <input type='hidden' name='type' value="pn">
        </form>
        </td>
        <td>Search by Category
            <form name='search' action="/search" method=post>
            <input type='input' name='srch' value="">
            <input type='hidden' name='type' value="cat">
        </form>
        </td>
    </tr>
    </table> 
    <br>
    """

def footer():
    """ Yields footer html"""

    return """
        <br>
        <br>
        <hr>
        <a href="http://freshmeat.net">
        <img align="right" border=0 src="/static/link_button_3.gif" alt="freshmeat"></a>
        </body>
        </html>
        """

