__author__ = 'Mave'

import urllib2
import sqlite3
#Create Link Object
request = urllib2.Request('http://www.hgamecn.com/htmldata/articlelist/')
request.add_header('User-Agent', 'Macho Macho Man')

#Create Database Object
db = sqlite3.connect('Page_Record.db')


#Function Area
def page_switcher(need_page):
    link = 'http://www.hgamecn.com/htmldata/articlelist/list_'+str(need_page)+'.html'
    #for debug
    print link

#Main Start
try:
    response = urllib2.urlopen(request, timeout=5)
except urllib2.URLError as e:
    if hasattr(e, 'reason'):
        print 'Sorry, I can not get the target website. (Because of me)'
        print 'Reason: ', e.reason
    elif hasattr(e, 'code'):
        print 'Sorry, I can not get the target website. (Because of station)'
        print 'Error Code: ', e.code
else:
    print 'All right, I can get the target website.'
    print 'Code: ', response.code
    page = response.read()
    print page
    print 'Current Page Print Finished.'

#Analysis Part




