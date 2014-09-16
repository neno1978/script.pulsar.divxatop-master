import sys
import json
import base64
import re
import urllib
import urllib2
import bencode
import hashlib 

PAYLOAD = json.loads(base64.b64decode(sys.argv[1]))
CATEGORY_MOVIES = "1"
CATEGORY_HDMOVIES = "2"
CATEGORY_EPISODES = "3"

def search(query, category=""):
  if category != "":
    category = "&category=" + category
    
  response = urllib2.urlopen("http://cuelgame.net/search.php%s" % (urllib.quote_plus(query), category))
  data = response.read()
  if response.headers.get("Content-Encoding", "") == "gzip":
    import zlib
    data = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(data)

  pmagnet = re.compile(r'magnet:\?[^\'"\s<>\[\]]+')
  ptorrent = re.compile(r'http[s]?://.*\.torrent')
  sections = (data.split("<td"))
  uris = []
  
  for section in sections:
    magnet = pmagnet.search(section)
    if magnet == None:
      torrent = ptorrent.search(section)
      if torrent != None:
        uris.append({"uri": torrent2magnet(torrent.group(0))})
    else:
      uris.append({"uri": magnet.group(0)})
  
  return uris

def search_episode(imdb_id, tvdb_id, name, season, episode):
  # search only for episodes
  return search("%s S%02dE%02d" % (name, season, episode), CATEGORY_EPISODES)


def search_movie(imdb_id, name, year):
  # SD and HD movies are categorized, and we can't search multiple categories
  return search(name + " " + year)

def torrent2magnet(torrent_url):
  response = urllib2.urlopen(torrent_url)
  torrent = response.read()
  metadata = bencode.bdecode(torrent)
  hashcontents = bencode.bencode(metadata['info'])
  digest = hashlib.sha1(hashcontents).digest()
  b32hash = base64.b32encode(digest)
  magneturl = 'magnet:?xt=urn:btih:' + b32hash  + '&dn=' + metadata['info']['name']
  return magneturl

#print json.dumps(globals()[PAYLOAD["method"]](*PAYLOAD["args"]))
urllib2.urlopen(
    PAYLOAD["callback_url"],
    data=json.dumps(globals()[PAYLOAD["method"]](*PAYLOAD["args"]))
)
