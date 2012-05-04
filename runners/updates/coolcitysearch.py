#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
######################################################################
File: urlwords.py

########################################################################
# Copyright (c) 2011 by Vinny Murphy
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
########################################################################

Date Created: Sun Aug 14 19:10:47 2011

Description: look up the cities in the database for runners and for
the urls in the new england states and give a list of how many hits
total for the cities.
######################################################################
'''

import os
import sqlite3
import re
import urllib

from datetime import datetime

CITY_LENGTH_MIN = 3
COOLRUNNING_URL = 'http://www.coolrunning.com'


def make_index(myurl):
    '''parse to file to get all the words in it that are greater than
    CITY_LENGTH_MIN long'''

    url_handle = urllib.urlopen(myurl)
    words = {}

    for line in url_handle.readlines():
        line = re.sub(r'[^a-z]', ' ', line.lower())
        for word in line.split():
            if len(word) > CITY_LENGTH_MIN:
                try:
                    words[word] += 1
                except KeyError:
                    words[word] = 1
    return words


def city_words(database):
    '''pick out the cities that the runners live in.'''

    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute('''
SELECT DISTINCT(city) FROM club_address
  LEFT JOIN club_city WHERE club_city.id = club_address.city_id
''')
    city = {}
    for row in cur:
        for city_name in row[0].split():
            if len(city_name) > CITY_LENGTH_MIN:
                city_name = city_name.lower()
                if city.has_key(city_name):
                    city[city_name] += 1
                else:
                    city[city_name] = 1
    excludes = ['east', 'south', 'north', 'west', 'city']
    return list(set(city.keys()) - set(excludes))


def result_urls(page):
    '''find the /results/... html pages.'''

    result_regx = re.compile(r'.*<a href="(/results/\S+.shtml)">')
    webpage = urllib.urlopen(page)
    html = webpage.read()
    webpage.close()
    return ['%s%s' % (COOLRUNNING_URL, r) for r in
            result_regx.findall(html)]


def sub_urls(page):
    '''find the sublist on this results page'''

    result_regx = re.compile(r'<a href="(./\S+.shtml)">')
    webpage = urllib.urlopen(page)
    html = webpage.read()
    webpage.close()
    url_part = page.rpartition('/')[0]
    results = ['%s/%s' % (url_part, r[2:]) for r in
               result_regx.findall(html)]
    return list(set(results))


def update_db(dbfile, urls):
    '''enter the url into the db file'''

    create_table = False
    if not os.path.exists(dbfile):
        create_table = True
    conn = sqlite3.connect(dbfile)
    curs = conn.cursor()
    if create_table:
        curs.execute('''CREATE TABLE state_urls(state TEXT NOT NULL,
                        url TEXT NOT NULL, PRIMARY KEY(state, url))'''
                     )
    for url_info in urls:
        curs.execute('insert into state_urls values (?,?)', url_info)
    conn.commit()


def put_cool_urls_in_db(urls, dbfile):
    '''find the urls in the database'''

    if not os.path.exists(dbfile):
        return urls

    conn = sqlite3.connect(dbfile)
    curs = conn.cursor()
    curs.execute('''SELECT state, url FROM state_urls''')
    db_urls = []
    for row in curs:
        db_urls.append((row[0], row[1]))
    exclusive = list(set(urls).difference(set(db_urls)))

    return exclusive


def get_cool_urls_from_db(dbfile):
    '''get the urls from the database'''

    if not os.path.exists(dbfile):
        return None

    conn = sqlite3.connect(dbfile)
    curs = conn.cursor()
    curs.execute('''SELECT url FROM state_urls''')
    db_urls = []
    for row in curs:
        db_urls.append(row[0])
    exclusive = set(db_urls)
    return exclusive


def get_state_urls(existing_urls):
    '''walk through the list of states on the coolrunning website and
    grab results that we have not seen'''

    states = ['ct', 'fl', 'ma', 'nh', 'ny', 'ri', 'vt', ]
    state_page = COOLRUNNING_URL + '/results/%s/%s.shtml'
    today = datetime.now()
    years = [int(today.strftime('%y'))]

    if 1 == today.month:
        years.append(int(today.strftime('%y')) - 1)

    urls = []
    for state in states:
        for year in years:
            pages = result_urls(state_page % (year, state))
            for page in pages:
                if page not in existing_urls:
                    urls.append((state, page))
                    sub_pages = sub_urls(page)
                    for sub_page in sub_pages:
                        urls.append((state, sub_page))
    return list(set(urls))


def cool_urls():
    '''pick up the urls from coolrunning that are from the states
    variable and the current year.  If it is January then look at last
    years pages too.'''

    dbfile = os.path.join(os.path.dirname(__file__), 'coolurl.db')
    cities = city_words('../../Runner.db')
    urls = get_state_urls(get_cool_urls_from_db(dbfile))
    inserts = put_cool_urls_in_db(urls, dbfile)

    intersection = []
    for insert in inserts:
        index_dict = make_index(insert[1])
        intersection = \
            list(set(index_dict.keys()).intersection(set(cities)))
        if intersection:
            total = 0
            intersection.sort()
            for inter in intersection:
                total += int(index_dict[inter])
            print '%s has %d references to %s' % (insert[1], total,
                    ', '.join(intersection))
    update_db(dbfile, inserts)


if __name__ == '__main__':
    cool_urls()
