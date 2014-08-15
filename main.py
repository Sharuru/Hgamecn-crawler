#coding: utf-8
__author__ = 'Mave'

import sys
import re
import urllib2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref


# Database Object
engine = create_engine('sqlite:///Page_Record.db', connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

GameTagsTable = Table('games_tags', Base.metadata,
                      Column('id', Integer, primary_key=True, autoincrement=True),
                      Column('game_id', Integer, ForeignKey('game.id')),
                      Column('tag_id', Integer, ForeignKey('tags.id')))


class GameTable(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    publisher = Column(Integer, ForeignKey('publisher.id'))
    publisher_is = relationship('PublisherTable', backref='games')
    publish_date = Column(String)
    tags = relationship('TagsTable', secondary=GameTagsTable, backref='games')


class PublisherTable(Base):
    __tablename__ = 'publisher'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class TagsTable(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

Base.metadata.create_all(engine)


# Game Class
class Game(object):
    def __init__(self, title, publisher='', date='', tags=[]):
        self.title = title
        self.publisher = publisher
        self.date = date
        self.tags = tags

    def print_game(self):
        print self.title
        print 'Publisher:', self.publisher
        print 'Date:', self.date
        print 'Tags:', ', '.join(self.tags)
        print '\n'


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
    title_list = [title_data[:-6] for title_data in get_title(current_page)]
    for publisher_data in get_publisher(current_page):
        publisher_list.append(publisher_data)
    for publish_date in get_publish_date(current_page):
        publish_date_list.append(publish_date)
    for tag_data in get_tags(current_page):
        tag_data_list.append(tag_data)
    return [Game(title=title_list[lr], publisher=publisher_list[lr],
            date=publish_date_list[lr], tags=tag_data_list[lr]) for lr in range(0, len(title_list))]


# Main Start
now_page = 1
urls = 'http://www.hgamecn.com/htmldata/articlelist/'
total_page = int(count_page(urls)[0])

print 'There are {total} Pages need to be crawled.'.format(total=total_page)
print 'Start crawling...'

for page in range(1, total_page + 1):
    games = crawler(urls)
    now_page += 1

    for glr in games:
        glr.print_game()

        game_info = GameTable(name=glr.title.decode('utf-8'), publish_date=glr.date.decode('utf-8'))
        session.add(game_info)
        session.commit()

    urls = page_switcher(now_page)


print 'Finished.'
