#! /usr/bin/python -tt
#
# -*- coding: utf-8 -*-
'''
######################################################################
File: urlwords.py

Copyright (c) 2011 by Cisco Systems, Inc.
All rights reserved.
Author: Vinny Murphy

Date Created: Sun Aug 14 19:10:47 2011

Description:
<insert file description here!>
######################################################################
'''
import os
import string   
import sys
import sqlite3
import re
import urllib

from datetime import datetime

def makeIndex(myurl):
    # open local html file   
    page = myurl
    url_handle = urllib.urlopen(myurl)
       
    # initialize stuff here   
    wordcount = 0   
    words     = { }   
       
    for line in url_handle.readlines():
        line = string.strip( line )    
        for word in re.split(   
                "[" + string.whitespace + string.punctuation + "]+" ,   
                line ) :
            if len(word) > 3:
                word = string.lower( word )   
                if re.match( "^[" + string.lowercase + "]+$" , word ) :   
                    wordcount += 1   
                    if words.has_key( word ) :   
                        words[ word ] += 1   
                    else :   
                        words[ word ] = 1   
    return words

def cityWords(database):
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute("select distinct(city) from club_city WHERE length(city) > 3")
    city = {}
    for row in cur:
        for r in row[0].split():
            if len(r) > 3:
                r = r.lower()
                if city.has_key(r):
                    city[r] += 1
                else:
                    city[r] = 1
    excludes = ['east', 'south', 'north', 'west',]
    return(list(set(city.keys()) - set(excludes)))

def resultURLS(page):
    result_regx = re.compile(r'.*<a href="(/results/\S+.shtml)">')
    coolrunning = 'http://coolrunning.com'
    webpage = urllib.urlopen(page)
    html = webpage.read()
    webpage.close()
    return (['%s%s' % (coolrunning, r) for r in result_regx.findall(html)])

def updateDB(dbfile, urls):
    create_table = False
    if not os.path.exists(dbfile):
        create_table = True
    conn = sqlite3.connect(dbfile)
    curs = conn.cursor()
    if create_table:
        curs.execute('''CREATE TABLE state_urls(state TEXT NOT NULL,
                        url TEXT NOT NULL, PRIMARY KEY(state, url))''')
    for t in urls:
        curs.execute('insert into state_urls values (?,?)', t)
    conn.commit()
        
    
def coolURLSinDB(urls, dbfile):
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



def coolURLS():
    states = ['ma', 'ri', 'ct','vt', 'nh']
    RESURL = 'http://www.coolrunning.com/results/%s/%s.shtml'
    today = datetime.now()
    urls = []
    city_words = cityWords('../../Runner.db')
    for state in states:
        pages = resultURLS(RESURL % (today.strftime('%y'), state))
        for page in pages:
            urls.append((state, page))
    dbfile = os.path.join(os.path.dirname(__file__), 'coolurl.db')
    inserts = coolURLSinDB(urls, dbfile)
    intersection = []
    for u in inserts:
        index_dict = makeIndex(u[1])
        intersection = list(set(index_dict.keys()).intersection(set(city_words)))
        if intersection:
            total = 0
            intersection.sort()
            for inter in intersection:
                total += int(index_dict[inter])
            print '%s has %d references to %s' % (u[1],
                                                  total,
                                                  ', '.join(intersection))
    updateDB(dbfile, inserts)
    
    

if __name__ == "__main__":
    coolURLS()
