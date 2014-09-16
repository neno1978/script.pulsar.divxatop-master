import sys
import json
import base64
import re
import urllib
import urllib2
from xml.dom import minidom
from HTMLParser import HTMLParser

PAYLOAD = json.loads(base64.b64decode(sys.argv[1]))

def search(query):
    response = urllib2.urlopen("http://cuelgame.net/rss2.php?q=%s" % urllib.quote_plus(query))
    data = response.read()
    if response.headers.get("Content-Encoding", "") == "gzip":
        import zlib
        data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(data)

    #convert the rss feed to an xml dom and get all the "<item>" elements that has a category of "cine"
    items = minidom.parseString(data).getElementsByTagName("item")
    items = [item for item in items if item.getElementsByTagName("category").item(0).childNodes.item(0).toxml() == '<![CDATA[cine]]>'];
    
    magnets = []

    #extract the url from each item and append it to the result list
    for node in items:
        magnets.append({"uri" : HTMLParser.unescape.__func__(HTMLParser, node.getElementsByTagName("cuelgame:url").item(0).childNodes.item(0).toxml())})
        
    return magnets


def search_episode(imdb_id, tvdb_id, name, season, episode):
    return search("%s S%02dE%02d" % (name, season, episode))


def search_movie(imdb_id, name, year):
    return search(imdb_id)

urllib2.urlopen(
    PAYLOAD["callback_url"],
    data=json.dumps(globals()[PAYLOAD["method"]](*PAYLOAD["args"]))
)
