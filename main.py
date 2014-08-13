__author__ = 'Mave'

import re
import urllib2

games = []


class Game(object):
    def __init__(self, title, publisher='', date='', tags=[]):
        self.title = title
        self.publisher = publisher
        self.date = date
        self.tags = tags


# Function Area
def page_switcher(need_page):
    return 'http://www.hgamecn.com/htmldata/articlelist/list_{page}.html'.format(page=need_page)


def linker(url):
    print 'Connecting the target website...'
    request = urllib2.Request(url)
    request.add_header('User-Agent', 'Macho Macho Man')
    try:
        response = urllib2.urlopen(request, timeout=5)
    except urllib2.URLError as e:
        if hasattr(e, 'reason'):
            print 'Sorry, I can not get the target website. (Because of me)'
            print 'Reason: ', e.reason
            exit()
        elif hasattr(e, 'code'):
            print 'Sorry, I can not get the target website. (Because of station)'
            print 'Error Code: ', e.code
            exit()
    else:
        print url,
        print 'Connected.'
        print 'Response Code: ', response.code
        return response.read()


def count_page(url):
    current_page = linker(url)
    match_page_count = re.compile('<div class="hgc_pages">1/(.*) \xe9')
    return match_page_count.findall(current_page)


def get_title(current_page):
    match_title = re.compile('<div class="gtitle"><a href=".*" target="_blank">(.*)</a></div>')
    return match_title.findall(current_page)


def get_publisher(current_page):
    match_publisher = re.compile('<span class="maker">.*?<a href=".*?">(.*?)</a></span>')
    return match_publisher.findall(current_page)


def get_publish_date(current_page):
    match_publish_date = re.compile('<span class="date">.*?>(.*?)</a></span>')
    return match_publish_date.findall(current_page)


def get_tags(current_page):
    match_tags = re.compile('<div class="tag">(.*?)</div>')
    match_tag = re.compile('<a href=".*?">(.*?)</a>')
    return [match_tag.findall(tags) for tags in match_tags.findall(current_page)]


def crawler(url):
    title_list = []
    publisher_list = []
    publish_date_list = []
    tag_data_list = []
    current_page = linker(url)
    print 'I am operating data in this page...'
    for title_data in get_title(current_page):
        title_list.append(title_data[:-6])
    for publisher_data in get_publisher(current_page):
        publisher_list.append(publisher_data)
    for publish_date in get_publish_date(current_page):
        publish_date_list.append(publish_date)
    for tag_data in get_tags(current_page):
        tag_data_list.append(tag_data)
    for lr in range(0, len(title_list)):
        games.append(Game(title=title_list[lr], publisher=publisher_list[lr],
                          date=publish_date_list[lr], tags=tag_data_list[lr]))

# Main Start
now_page = 1
urls = 'http://www.hgamecn.com/htmldata/articlelist/'
total_page = int(count_page(urls)[0])
x=0
y=20
print total_page
for page in range(0, total_page):
    crawler(urls)
    now_page += 1
    for glr in games[x:y]:
        print '\n' + glr.title,
        print glr.publisher,
        print glr.date,
        for tr in glr.tags:
            print tr,
    print '\n'
    x = y
    y = y + 20
    urls = page_switcher(now_page)


for glr in games:
    print '\n' + glr.title,
    print glr.publisher,
    print glr.date,
    for tr in glr.tags:
        print tr,
print '\n'