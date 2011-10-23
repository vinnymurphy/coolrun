#! /usr/bin/python -tt
#
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
import string   
import sqlite3
import re
import urllib

from datetime import datetime

CITY_LENGTH_MIN = 3
COOLRUNNING_URL = 'http://www.coolrunning.com'

def make_index(myurl):
    '''open the local html file'''
    url_handle = urllib.urlopen(myurl)
       
    # initialize stuff here   
    words     = { }   
       
    for line in url_handle.readlines():
        line = line.strip()
        for word in re.split(   
                "[" + string.whitespace + string.punctuation + "]+" ,   
                line ) :
            if len(word) > CITY_LENGTH_MIN:
                word = string.lower( word )   
                if re.match( "^[" + string.lowercase + "]+$" , word ) :   
                    if words.has_key( word ) :   
                        words[ word ] += 1   
                    else :   
                        words[ word ] = 1   
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
    excludes = ['east', 'south', 'north', 'west', ]
    return(list(set(city.keys()) - set(excludes)))

def result_urls(page):
    '''find the /results/... html pages.'''
    result_regx = re.compile(r'.*<a href="(/results/\S+.shtml)">')
    webpage = urllib.urlopen(page)
    html = webpage.read()
    webpage.close()
    return (['%s%s' % (COOLRUNNING_URL, r) for r in result_regx.findall(html)])

def update_db(dbfile, urls):
    '''enter the url into the db file'''
    create_table = False
    if not os.path.exists(dbfile):
        create_table = True
    conn = sqlite3.connect(dbfile)
    curs = conn.cursor()
    if create_table:
        curs.execute('''CREATE TABLE state_urls(state TEXT NOT NULL,
                        url TEXT NOT NULL, PRIMARY KEY(state, url))''')
    for url_info in urls:
        curs.execute('insert into state_urls values (?,?)', url_info)
    conn.commit()
        
    
def cool_urls_in_db(urls, dbfile):
    '''find the urls in the database'''
    if not os.path.exists(dbfile):
        return(urls)
    
    conn = sqlite3.connect(dbfile)
    curs = conn.cursor()
    curs.execute('''SELECT state, url FROM state_urls''')
    db_urls = []
    for row in curs:
        db_urls.append((row[0], row[1]))
    exclusive = list(set(urls).difference(set(db_urls)))
    
    return(exclusive)



def cool_urls():
    '''pick up the urls from coolrunning that are from the states
    variable and the current year'''
    states = ['ma', 'ri', 'ct', 'vt', 'nh', 'fl', 'ny']
    state_page = COOLRUNNING_URL + '/results/%s/%s.shtml'
    today = datetime.now()
    urls = []
    cities = city_words('../../Runner.db')
    for state in states:
        pages = result_urls(state_page % (today.strftime('%y'), state))
        for page in pages:
            urls.append((state, page))
    dbfile = os.path.join(os.path.dirname(__file__), 'coolurl.db')
    inserts = cool_urls_in_db(urls, dbfile)
    intersection = []
    for insert in inserts:
        index_dict = make_index(insert[1])
        intersection = list(set(index_dict.keys()).intersection(set(cities)))
        if intersection:
            total = 0
            intersection.sort()
            for inter in intersection:
                total += int(index_dict[inter])
            print '%s has %d references to %s' % (insert[1],
                                                  total,
                                                  ', '.join(intersection))
    update_db(dbfile, inserts)
    
    

if __name__ == "__main__":
    cool_urls()
