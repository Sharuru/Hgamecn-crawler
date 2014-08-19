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
                      Column('game_id', Integer, ForeignKey('games.id')),
                      Column('tag_id', Integer, ForeignKey('tags.id')))


class TagsTable(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class PublisherTable(Base):
    __tablename__ = 'publishers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class GameTable(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    publisher_id = Column(Integer, ForeignKey('publishers.id'))
    _publisher = relationship("Publisher", backref='games')
    publish_date = Column(String)
    _tags = relationship('TagsTable', secondary=GameTagsTable, backref='games')

    def _find_or_create_publisher(self, publisher):
        p = session.query(PublisherTable).filter(PublisherTable.name == publisher)
        if not(p):
            p = PublisherTable(name=publisher)
        return p

    def _get_publisher(self):
        return self._publisher

    def _set_publisher(self, value):
        GameTable(publisher_id=self._find_or_create_publisher(value).id)

    publisher = property(_get_publisher, _set_publisher, "PublisherTable")

    def _find_or_create_tag(self, tag):
        q = session.query(TagsTable).filter(TagsTable.name == tag)
        t = q.first()
        if not(t):
            t = TagsTable(name=tag)
        return t

    def _get_tags(self):
        return self._tags

    def _set_tags(self, value):
        # clear the list first
        while self._tags:
            del self._tags[0]
        # add new tags
        for tag in value:
            self._tags.append(self._find_or_create_tag(tag))

    tags = property(_get_tags, _set_tags, "TagsTable")

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
    match_page_count = re.compile('<div class="hgc_pages">1/(.*) ')
    newest_record_id = re.compile('<div class="gtitle"><a href="/htmldata/article/(.*).html" target="_blank">')

    return [match_page_count.findall(current_page)[0], newest_record_id.findall(current_page)[0]]


def record_count(need):
    latest_id_local = session.query(GameTable).order_by(GameTable.id.desc()).first()
    if latest_id_local is None:
        latest_id_local = 0
    else:
        latest_id_local = latest_id_local.id
    if need == 'local':
        return latest_id_local
    elif need == 'row':
        return session.query(GameTable).count()


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
latest_id_at_remote = int(count[1])
latest_id_at_local = record_count('local')
row_count = record_count('row')

print 'The Latest Record ID at Remote is {id}'.format(id=latest_id_at_remote)
print 'The Latest Record ID at Local is {id}'.format(id=latest_id_at_local)

# Check Miss
miss_flag = False
if latest_id_at_local != row_count:
    print 'But It seems You MISSED some record in Local, I will try to refill it.'
    miss_flag = True

print 'If you are FIRST running this crawler'
print 'There are {total} Pages need to be crawled.'.format(total=total_page)

print 'Start crawling...'

for page in range(1, total_page + 1):
    games = crawler(urls)
    for glr in games:
        # Flag set
        if record_count('local') != record_count('row') or record_count('local') != latest_id_at_remote:
            miss_flag = True
        else:
            miss_flag = False
        # Game Info Check & Commit
        if int(glr.id) <= latest_id_at_remote and miss_flag is False:
            operation_finished()
        else:
            game = GameTable(id=int(glr.id), name=glr.title, publish_date=glr.date)
            game.tags = glr.tags
            game.publisher = glr.publisher
            session.add(game)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
            # Publisher Info Check & Commit
            '''try:
                publisher_new = session.query(PublisherTable).filter(PublisherTable.name == glr.publisher).one()
            except NoResultFound:
                publisher_new = PublisherTable(name=glr.publisher)
                session.add(publisher_new)
                session.commit()'''

    now_page += 1
    urls = page_switcher(now_page)

operation_finished()
