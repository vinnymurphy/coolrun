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
import string   
import sys
import sqlite3
import re
import urllib

from pprint import pprint

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

if __name__ == "__main__":
    words = makeIndex(sys.argv[1])
    sorted_word_list = words.keys()   
    sorted_word_list.sort()
    
    conn = sqlite3.connect('../../Runner.db')
    cur = conn.cursor()
    cur.execute("select distinct(city) from club_city WHERE length(city) > 1")
    city = {}
    for row in cur:
        for r in row[0].split():
            if len(r) > 3:
                r = r.lower()
                print r
                if city.has_key(r):
                    city[r] += 1
                else:
                    city[r] = 1
    excludes = ['east', 'south', 'north', 'west',]
    cities = list(set(city.keys()) - set(excludes))
    pprint(cities)
    hits = []
    total = 0
    city_names = list(set(sorted_word_list).intersection(set(cities)))
    pprint(city_names)
    for city_name in city_names:
        value = int(words[city_name])
        if value:
            hits.append(city_name)
            total += value

    hits.sort()
    print '%s had %d hits for' % (sys.argv[1], total),
    print ', '.join(hits),
