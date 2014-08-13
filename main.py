__author__ = 'Mave'

import re
import urllib2
import sqlite3
from bs4 import BeautifulSoup

# Create Link Object
request = urllib2.Request('http://www.hgamecn.com/htmldata/articlelist/')
request.add_header('User-Agent', 'Macho Macho Man')

# Create Database Object
# Not Used at present
db = sqlite3.connect('Page_Record.db')


# Function Area
def page_switcher(need_page):
    link = 'http://www.hgamecn.com/htmldata/articlelist/list_{page}.html'.format(page=need_page)
    #for debug
    print link

# Link Start! Welcome to Sword Art Online!
print 'Connecting...'
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
    print 'Response Code: ', response.code
    page = response.read()
# Analysis Part
    current_page = 1
    print 'OK...I am going to initialize the analysis part.'
    page_content = BeautifulSoup(page)
    game_content = page_content.find_all(id='hgc_right')
    print 'Gotcha! div id = "hgc_right"'
    print 'Counting Record Numbers...',
    game_content = str(game_content[0])
    game_number_in_current_page = int(game_content.count('gtitle'))
    print game_number_in_current_page
    print 'Counting Record Pages...',
    page_finder_head = game_content.find('<div class="hgc_pages">1/')
    page_finder_tail = game_content.find('<span class="hgc_pages_con">')
    total_page = int(game_content[page_finder_head+25:page_finder_tail-13])
    print total_page
    print 'Calculate Finished.'
    print 'Now, I am going to process data in page {number}.'.format(number=current_page)
    # To Process Data
    game_title = page_content.find_all('div', 'gtitle')
    game_publisher = page_content.find_all('span', 'maker')
    game_publish_date = page_content.find_all('span', 'date')
    game_tags = page_content.find_all('div', 'tag')
    for something in range(0, 20):
        print game_title[something]
        #print game_publisher[something]
        #print game_publish_date[something]
        #print game_tags[something]

