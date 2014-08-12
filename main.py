__author__ = 'Mave'

import urllib2
request = urllib2.Request('http://www.hgamecn.com/htmldata/articlelist/')

try:
    response = urllib2.urlopen(request)
except urllib2.URLError as e:
    if hasattr(e, 'reason'):
        print 'Sorry, I can not get the target website. (Because of me)'
        print 'Reason: ', e.reason
    elif hasattr(e, 'code'):
        print 'Sorry, I can not get the target website. (Because of station)'
        print 'Error Code: ', e.code
else:
    print 'All right, I can get the target website.'
    page = response.read()
    print page



