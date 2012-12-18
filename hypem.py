import requests
from pyquery import PyQuery as pq
import urllib
import urlparse
import json
import unicodedata
import re

# for x in range(0, 3):
#     user_agent = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11'}
#     r = requests.get("http://hypem.com/joelrojo", headers = user_agent)
#     cookies = r.cookies
#     r_serve = requests.get("http://hypem.com/serve/source/1qhnq/d7d15759b344c244275fb7633447de93", headers = user_agent, cookies=cookies)
#     page = pq(r_serve.content)
#     print page("title")
#     if page("title") == "Error 404: Not Found":
#         print "***** Found 404, page doesn't exist. Trying next song...\n"
#         continue
#     else:
#         print "yayyy"

def url_fix(s, charset='utf-8'):
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def normalize_string(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip())
    value = unicode(re.sub('[-\s]+', '-', value)) 
    return value

user_agent = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11'}
p = 1
total = 0
print "Calculating number of pages"
while True:
    r_url = "http://hypem.com/joelrojo/%s/" % str(p)
    print "\nHitting page %s - %s ....\n*********************************************************\n" % (str(p), r_url)
    r = requests.get(r_url, headers = user_agent)
    page = pq(r.content)
    if page("title") == "Error 404: Not Found":
        print "***** Reached the end of favorites. Stopping script...\n"
        break
    print "DOWNLOADING TRACKS....\n"
    cookies = r.cookies
    dl = json.loads(page("#displayList-data").html())
    for track in dl['tracks']:
        url = "http://hypem.com/serve/source/%s/%s" % (track['id'], track['key'])
        filename = '%s - %s' % (track['artist'], track['song'])
        destination = '/Users/joelrojo/Desktop/hypem/%s.mp3' % (normalize_string(unicode(filename)))
        r_serve = requests.get(url, headers = user_agent, cookies=cookies)
        page = pq(r_serve.content)
        title = page("title")
        if title == "Error 404: Not Found":
            print "***** Found 404, page doesn't exist. Trying next song...\n"
            continue
        if title == "Error 403: Not Authorized":
            print "***** Found 403, not authorized to view page. Trying next song...\n"
            continue
        try:
            source_url = url_fix(json.loads(r_serve.content).get('url'))
        except:
            print "JSON could not be decoded. Trying next song... \n"
            continue
        print "%s - %s\nurl: %s\n" % (track['artist'], track['song'], source_url)
        try:
            requests.get(source_url, headers = user_agent, timeout=3)
        except:
            print "***** URL failed to load. Trying next song...\n"
            continue
        urllib.urlretrieve(source_url, destination)
        total += 1
    p += 1
print "Total Tracks downloaded: %s\nHave a nice day :-)" % (str(total))