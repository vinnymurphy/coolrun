#!/usr/bin/python
# -*- coding: utf-8 -*-

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

'''lookup a url and see if any of the runners from the club are in the
web page. The output is sent to a temp file so that you can edit and
then when you are done run the results.py script.'''

import itertools
import os
import re
import sys
import tempfile
import urllib

top_dir = \
    os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                    '..', '..', '..'))
sys.path.insert(0, top_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'coolrun.settings'

from coolrun.runners.models import Runner
from coolrun.race.models import Race
from datetime import date
from dateutil import parser

# from pprint import pprint

from django.db.models import Q
from django.forms.models import model_to_dict

if len(sys.argv) < 2:
    sys.stderr.write('Usage: %s <url> [date]\n' % sys.argv[0])
    sys.exit(1)

urls = []
urls.append(sys.argv[1])


def _strip_initial(name):
    if len(name) > 2:
        name_match = re.match(r'^(\w+)\s\w\.?$', name)
        if name_match:
            name = name_match.group(1)
    return name


if len(sys.argv) > 2:
    from_date = parser.parse(sys.argv[2]).date()

    # June 1st is suppose to be the cutoff for updating the gran prix.
    # Todo: * figure out algorithm to do June 1st.
    #       * figure out how we would do the new year.

    races = [u.url for u in Race.objects.filter(date__year=2012,
             gran_prix='N')]

    urls += races
else:
    from_date = None

if from_date:
    all_runners = Runner.objects.filter(Q(date_created__gte=from_date))
else:

#            | Q(date_modified__gte=from_date))

    all_runners = Runner.objects.all()

tmp_directory = '%s/%s' % (tempfile.gettempdir(),
                           date.today().strftime('%Y%m%d'))
if not os.path.exists(tmp_directory):
    os.makedirs(tmp_directory)


def guess_place_and_time(filename, line):
    '''determine where the place in the race is by looking for just a
    number on the line all by itself.  Most likely the runnners place
    is at the beginning of the line but offer up the start and end of
    anything that looks like a place.  The time is deterimined simply
    by looking for some form of 1:30:20 or 12:25.'''

    places = []
    times = []
    for m in re.finditer(r'\b\d+\b(?=\s)', line):
        places.append((m.start(), m.end()))
    for m in re.finditer(r'\b\d+:\d+(?::\d+)?\.?\b', line):
        times.append((m.start(), m.end()))
    if places:
        filename.write('place = ')
        for place in places:
            filename.write('%s,%s ' % (place[0], place[1]))
        filename.write('\n')
    else:
        filename.write('place = 0,10\n')
    if times:
        filename.write('time = ')
        for t in times:
            filename.write('%s,%s ' % (t[0], t[1]))
        filename.write('\n')
    else:
        filename.write('time = 0,10\n')


def guess_distance(race_title):
    '''Look at the title of the race and see if we can determine the
    distance and measurement of the race.'''

    rv_distance_measure = (None, None)
    half_re = re.compile(r'(?:1/2|half)', re.IGNORECASE)
    marathon_re = re.compile(r'marathon', re.IGNORECASE)
    kilometer_re = re.compile(r'.*(\d+(?:\.\d+)?)\s*(?:K|kilometers?)\b'
                              , re.IGNORECASE)
    mile_re = re.compile(r'.*(\d+(?:\.\d+)?)\s*(?:M|mile(?:s|r)?)\b',
                         re.IGNORECASE)

    if marathon_re.search(race_title):
        if half_re.search(race_title):
            rv_distance_measure = (13.11, 'M')
        else:
            rv_distance_measure = (26.22, 'M')
    m_k = kilometer_re.match(race_title)
    if m_k:
        rv_distance_measure = (m_k.group(1), 'K')
    m_m = mile_re.match(race_title)
    if m_m:
        rv_distance_measure = (m_m.group(1), 'M')

    return rv_distance_measure


def name_regx(runners):
    fi_ln_regx = []
    fn_ln_regx = []
    for r in runners:
        runna = model_to_dict(r)
        ln = runna['sur_name']
        if re.search(r'\s+', ln):

            # # add \s* where there are spaces for regexes so that
            # # Pierre de Fermat (Pierre de\s*Fermat) would be picked
            # # up in the results had he not died in the year 1665

            ln = re.sub(r'\s+', '\\s*', ln)

        # need to order it so lastname first or last

        firegx = r'\b%s[a-z]*?\s+(?:\w\.?\s+)?\b%s\b' \
            % ((runna['first_name'])[:1], ln)
        fi_ln_regx.append(firegx)

        # lastname, fi

        firegx = r'\b%s\b\s*%s' % (ln, (runna['first_name'])[:1])
        fi_ln_regx.append(firegx)
        fnregx = r'\b%s\s+\b%s\b' % (runna['first_name'], ln)
        fn_ln_regx.append(fnregx)
        fnregx = r'\b%s,?\s+(?:\w\.?\s+)?\b%s\b' % (ln,
                runna['first_name'])
        fn_ln_regx.append(fnregx)

    fi_ln_regx = r'(?:' + '|'.join(fi_ln_regx) + r')'
    fn_ln_regx = r'(?:' + '|'.join(fn_ln_regx) + r')'
    filn_regx = re.compile(r'(?P<fnln>%s)' % fi_ln_regx, re.IGNORECASE)
    fnln_regx = re.compile(r'(?P<fnln>%s)' % fn_ln_regx, re.IGNORECASE)

    return (filn_regx, fnln_regx)


def race_meta_data(url):
    '''return race name, place and date'''

    (rname, rplace, rdate) = ('', '', '')
    for line in urllib.urlopen(url).readlines():
        m_race_name = re.match('<h1>(.*?)</h1>', line)
        if m_race_name:
            rname = m_race_name.group(1)
        m_h2 = re.match('<h2>(.*?)</h2>', line)
        if m_h2:
            h2 = m_h2.group(1)
            rplace = h2
            rdate = parser.parse(h2, fuzzy=True).date()
    return (rname, rplace, rdate)


for url in urls:
    output = '%s/%s' % (tmp_directory, url.split('/')[-1:][0])
    try:
        f = open(output, 'w')
    except:
        next

    (filn_regx, fnln_regx) = name_regx(all_runners)
    race_name = ''
    race_place = ''
    f.write("results='''\n")


    def get_athlete_object(fnln, first_initial=False):
        '''return the object id of the athlete'''

        def _ath_obj(fname, lname):
            '''return exact match object id(s)'''

            fname = _strip_initial(fname)
            lname = _strip_initial(lname)
            athlete_obj = Runner.objects.filter(sur_name__iexact='%s'
                    % lname.strip(','), first_name__iexact='%s'
                    % fname.strip(','))
            return athlete_obj

        def _ath_fi_obj(fname, lname):
            '''return near match object id(s)'''

            fname = _strip_initial(fname)
            lname = _strip_initial(lname)
            athlete_obj = Runner.objects.filter(sur_name__iexact='%s'
                    % lname.strip(','), first_name__istartswith='%s'
                    % fname[:1])

            return athlete_obj

        a_name = fnln.split()
        if len(a_name) > 2:

            # # The firstname or lastname has a space in it so we split
            # # it up into the permutations and then run it through the
            # # object finder.

            perms = list(itertools.permutations(a_name))
            for perm in perms:
                (fname, lname) = (' '.join(perm[2:]),
                                  ' '.join(perm[:2]))
                perm_obj = _ath_obj(fname, lname)
                if perm_obj:
                    return perm_obj
            for perm in perms:
                (fname, lname) = (' '.join(perm[2:]),
                                  ' '.join(perm[:2]))
                perm_obj = _ath_fi_obj(fname, lname)
                if perm_obj:
                    return perm_obj
        else:
            (fname, lname) = fnln.split(None, 1)

        if first_initial:
            athlete_obj = _ath_fi_obj(fname, lname)
        else:
            athlete_obj = _ath_obj(fname, lname)
        if athlete_obj:
            return athlete_obj
        else:
            if first_initial:
                athlete_obj = _ath_fi_obj(lname, fname)
            else:
                athlete_obj = _ath_obj(lname, fname)
            if athlete_obj:
                return athlete_obj
            else:
                print "Warning: can't find %s %s" % (fname, lname)


    nFinishers = 0
    nFinishRegx = re.compile(r'^\s*(\d+)\s+')
    race_date = None
    ascii = os.popen('lynx --dump -width=200 -nolist ' + url).read()
    (race_name, race_place, race_date) = race_meta_data(url)
    last_line = None
    for line in ascii.split('\n'):
        nFinished = nFinishRegx.search(line)
        if nFinished:
            last_line = line
            nFinishers = nFinished.group(1)

        keepGoing = True
        attempt1 = fnln_regx.search(line)
        if attempt1:
            obj = get_athlete_object(attempt1.group('fnln'))
            if obj:
                f.write(line)
                for athlete in obj:
                    f.write('id:%s' % athlete.id)
                f.write('\n')
            else:

                # # should NOT get here so it is a wtf moment. :-(

                print 'wtf!',
                print 'okay, we can not get corresponding object id for',
                print '%s' % attempt1.group('fnln')
                print line
            keepGoing = False

        if keepGoing:
            attempt2 = filn_regx.search(line)
            if attempt2:
                (fn, ln) = attempt2.group('fnln').split(None, 1)
                obj = get_athlete_object(attempt2.group('fnln'),
                        first_initial=True)

                # could it be one of the following ids?:

                if obj:
                    f.write(line)
                    for athlete in obj:
                        f.write('%s %s- id:%s ' % (athlete.first_name,
                                athlete.sur_name, athlete.id))
                    f.write('\n')
    f.write("'''\n")

    raceinfo = None
    try:
        raceinfo = Race.objects.filter(url=url)[0]
    except:
        pass

    if raceinfo:
        f.write('date = %s\n' % raceinfo.date)
        f.write('distance = %s\n' % raceinfo.distance)
        f.write('finishers = %s\n' % raceinfo.finishers)
        f.write('gran_prix  = %s\n' % raceinfo.gran_prix)
        f.write('location = "%s, %s"\n' % (raceinfo.city.city,
                raceinfo.city.state))
        f.write('measure = %s\n' % raceinfo.measure)
        f.write('name = "%s"\n' % raceinfo.name)
        guess_place_and_time(f, last_line)
        f.write('url = %s\n' % raceinfo.url)
    else:
        if race_date is None:
            f.write('date = \n')
        else:
            f.write('date = %s\n' % race_date)
        (dist, measure) = guess_distance(race_name)
        if dist:
            f.write('distance = %s\n' % dist)
        else:
            f.write('distance = 5\n')
        f.write('finishers = %s\n' % nFinishers)
        f.write('gran_prix  = N\n')
        f.write('location = "%s"\n' % race_place)
        if measure:
            f.write('measure = %s\n' % measure)
        else:
            f.write('measure = M|K\n')
        f.write('name = "%s"\n' % race_name)
        guess_place_and_time(f, last_line)
        f.write('url = %s\n' % url)
    print output
