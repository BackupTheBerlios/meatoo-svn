
def header():
    """ Yields header html"""
    return """<html>
    <head>
      <title>Meatoo: Freshmeat-Gentoo Updates</title>
      <link href="/meatoo/static/stylin.css" media="screen" rel="Stylesheet" type="text/css" />
      <link href="http://gentooexperimental.org/meatoo/static/meatoo.xml" rel="alternate" type="application/rss+xml" title="Meatoo Freshmeat-Gentoo RSS Feed" />
    </head>
    <body>

    <h1><a href="/meatoo">Meatoo</a></h1>
    <br>
    Meatoo is a database of the latest Freshmeat releases having name matches
    in Gentoo's portage.<br>
    The database is updated twice a day at approximately 12am and 12pm UTC<br>

    <br>
    Please read the <a href="/meatoo/static/faq.html">FAQ</a> for more info.
    <br>
    <br>
    <br>
    <table>
    <tr>
        <td>Search by Herd/Maintainer
            <form name='search' action="/meatoo/search" method=post>
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
    """
    


def footer():
    """ Yields footer html"""

    return """
        <br>
        <br>
        <a href="http://freshmeat.net">
        <img border=0 src="/meatoo/static/link_button_3.gif" alt="freshmeat"></a>
        </body>
        </html>
        """

