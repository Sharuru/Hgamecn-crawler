#-*-coding:utf-8 -*-
__author__ = 'Mave'

import re
import urllib2
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError


reload(__import__('sys')).setdefaultencoding('utf-8')


# Database Object
engine = create_engine('sqlite:///Page_Record.db', connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine, autoflush=False)
session = Session()

GameTagsTable = Table('games_tags', Base.metadata,
                      Column('id', Integer, primary_key=True, autoincrement=True),
                      Column('game_id', Integer, ForeignKey('game.id')),
                      Column('tag_id', Integer, ForeignKey('tags.id')))


class GameTable(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    publisher = Column(String, ForeignKey('publisher.name'))
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
    def __init__(self, id, title, publisher='', date='', tags=[]):
        self.id = id
        self.title = title
        self.publisher = publisher
        self.date = date
        self.tags = tags

    def print_game(self):
        print self.id
        print self.title
        print 'Publisher:', self.publisher
        print 'Date:', self.date
        print 'Tags:', ', '.join(self.tags)


# Function Area
def page_switcher(need_page):
    if need_page > 999:
        return 'Finished.'
    else:
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


def init_count(url):
    current_page = linker(url)
    match_page_count = re.compile(u'<div class="hgc_pages">1/(.*) ')
    newest_record_id = re.compile(u'<div class="gtitle"><a href="/htmldata/article/(.*).html" target="_blank">')
    return [match_page_count.findall(current_page)[0], newest_record_id.findall(current_page)[0]]


def get_id(current_page):
    match_id = re.compile('<div class="gtitle"><a href="/htmldata/article/(.*).html" target="_blank">')
    return match_id.findall(current_page)


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
    id_list = []
    title_list = []
    publisher_list = []
    publish_date_list = []
    tag_data_list = []
    current_page = linker(url).decode('utf-8')
    print 'I am operating data in this page...'
    for id_data in get_id(current_page):
        id_list.append(id_data)
    #title_list = [title_data[:-6] for title_data in get_title(current_page)]
    # It seems kawaii if they use same method :)
    for title_data in get_title(current_page):
        title_list.append(title_data[:-2])
    for publisher_data in get_publisher(current_page):
        publisher_list.append(publisher_data)
    for publish_date in get_publish_date(current_page):
        publish_date_list.append(publish_date)
    for tag_data in get_tags(current_page):
        tag_data_list.append(tag_data)
    return [Game(id=id_list[lr], title=title_list[lr], publisher=publisher_list[lr],
            date=publish_date_list[lr], tags=tag_data_list[lr]) for lr in range(0, len(title_list))]


def check_record(return_type):
    head_record = session.query(GameTable).first()
    if head_record is None:
        head_record = 0
    else:
        head_record = head_record.id
    row_count = session.query(GameTable).count()
    record_in_database = head_record + row_count - 1
    if return_type is 0:
        return record_in_database
    elif record_in_database > row_count and return_type is 1:
        return False
    elif return_type is 1:
        return True


def operation_finished():
    print 'Record is Updated.'
    print 'All Operation Finished.'
    exit()

# Main Start
now_page = 1
urls = 'http://www.hgamecn.com/htmldata/articlelist/'

# Init Count
count = init_count(urls)
total_page = int(count[0])
newest_id = int(count[1])

print 'The Latest Record ID is {id}'.format(id=newest_id)
print 'The Latest Local Record ID is {id}'.format(id=check_record(0))

print 'If you are FIRST running this crawler'
print 'There are {total} Pages need to be crawled.'.format(total=total_page)

# Check Miss
miss_flag = False
if check_record(1) is False:
    print 'And It seems You MISSED some record in Local, I will try to refill it.'
    miss_flag = True

print 'Start crawling...'

for page in range(1, total_page + 1):
    games = crawler(urls)
    for glr in games:
        # Flag set
        if check_record(1) is False:
            miss_flag = True
        else:
            miss_flag = False
        # Game Info Check & Commit
        if int(glr.id) <= check_record(0) and miss_flag is False:
            operation_finished()
        else:
            game_info = GameTable(id=int(glr.id), name=glr.title,
                                  publisher=glr.publisher, publish_date=glr.date)
            session.add(game_info)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
            # Publisher Info Check & Commit
            try:
                publisher_new = session.query(PublisherTable).filter(PublisherTable.name == glr.publisher).one()
            except NoResultFound:
                publisher_new = PublisherTable(name=glr.publisher)
                session.add(publisher_new)
                session.commit()
            # Tag Info Check & Commit
            for one_tag in glr.tags:
                try:
                    tag_new = session.query(TagsTable).filter(TagsTable.name == one_tag).one()
                except NoResultFound:
                    tag_new = TagsTable(name=one_tag)
                    session.add(tag_new)
                    session.commit()
                #finally:
                    # Find Game ID & Tag ID Here
                    #game_id = session.query(GameTable).filter(GameTable.name == glr.title.decode('utf-8')).one().id
                    #tag_id = session.query(TagsTable).filter(TagsTable.name == one_tag.decode('utf-8')).one().id
                    #games_tags_new = GameTagsTable(game_id=game_id, tag_id=tag_id)
            # GameTagsTable Check & Commit (Under Developing)
            #glr.print_game()

    now_page += 1
    urls = page_switcher(now_page)

operation_finished()
