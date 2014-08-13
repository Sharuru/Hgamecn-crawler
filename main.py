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
    return 'http://www.hgamecn.com/htmldata/articlelist/list_{page}.html'.format(page=need_page)


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
    total_page = int(game_content[page_finder_head + 25: page_finder_tail - 13])
    print total_page
    print 'Calculate Finished.'
    print 'Now, I am going to process data in page {number}.'.format(number=1)

    # To Process Data
    for times in range(1, total_page + 1):
        game_title = page_content.find_all('div', 'gtitle')
        game_publisher = page_content.find_all('span', 'maker')
        game_publish_date = page_content.find_all('span', 'date')
        game_tags = page_content.find_all('div', 'tag')
        for records in range(0, game_number_in_current_page):
            game_title_str = str(game_title[records])
            game_publisher_str = str(game_publisher[records])
            game_publish_date_str = str(game_publish_date[records])
            game_tags_str = str(game_tags[records])

            game_title_finder_head = game_title_str.find('target="_blank">')
            game_title_finder_tail = game_title_str.find('</a></div>')
            game_title[records] = game_title_str[game_title_finder_head + 16: game_title_finder_tail - 6]

            game_publisher_finder_head = game_publisher_str.find('>', 32)
            game_publisher_finder_tail = game_publisher_str.find('</a></span>')
            game_publisher[records] = game_publisher_str[game_publisher_finder_head + 1: game_publisher_finder_tail]

            game_publish_date_finder_head = game_publish_date_str.find('>', 36)
            game_publish_date_finder_tail = game_publish_date_str.find('</a></span>')
            game_publish_date[records] = game_publish_date_str[game_publish_date_finder_head + 1: game_publish_date_finder_tail]

            game_tags_finder_head = 0
            game_tags_finder_tail = 0
            current_search_head = 30
            current_game_tags = ""
            for tag_number in range(0, 5):
                game_tags_finder_head = game_tags_str.find('">', current_search_head)
                game_tags_finder_tail = game_tags_str.find('</a>', game_tags_finder_head)
                if game_tags_finder_head == -1:
                    break
                else:
                    current_game_tags = current_game_tags + game_tags_str[game_tags_finder_head + 2: game_tags_finder_tail] + ' '
                    current_search_head = game_tags_finder_tail

            game_tags[records] = current_game_tags

            print game_title[records]
            print game_publisher[records]
            print game_publish_date[records]
            print game_tags[records]

# The following is for test need to be re-build as function !!

        print 'Now, I am going to process data in page {number}.'.format(number=times+1)
        print 'Doing next page..'
        print times
        need = times + 1
        link = page_switcher(need)
        print link
        request = urllib2.Request(link)
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
            page_content = BeautifulSoup(page)
            game_content = page_content.find_all(id='hgc_right')
            game_content = str(game_content[0])