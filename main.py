__author__ = 'Mave'

import re
import urllib2


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
        print url + 'Website connected.'
        print 'Response Code: ', response.code
        return response.read()


def get_title(data):
    match_title = re.compile('<div class="gtitle"><a href=".*"'
                             ' target="_blank">(.*)</a></div>')
    return match_title.findall(data)


def main():
    current_page = linker(url)
    for title_data in get_title(current_page):
        print title_data[:-6]


url = 'http://www.hgamecn.com/htmldata/articlelist/'
main()