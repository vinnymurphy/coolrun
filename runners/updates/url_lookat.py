#! /usr/bin/python -tt
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

import itertools
import os
import re
import sys
import tempfile
import urllib

top_dir = os.path.abspath(os.path.join(\
        os.path.dirname(os.path.dirname(__file__)), '..', '..', '..'))
sys.path.insert(0, top_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'coolrun.settings'

from coolrun.runners.models import City, Address
from coolrun.runners.models import Club, Runner
from coolrun.race.models import Race
from datetime import date
from dateutil import parser
from pprint import pprint

from django.db.models import Q
from django.forms.models import model_to_dict

if len(sys.argv) < 2:
    sys.stderr.write('Usage: %s <url> [date]\n' % (sys.argv[0]))
    sys.exit(1)

urls = []
urls.append(sys.argv[1])

if len(sys.argv) > 2:
    from_date = parser.parse(sys.argv[2]).date()
    # June 1st is suppose to be the cutoff for updating the gran prix.
    # Todo: * figure out algorithm to do June 1st.
    #       * figure out how we would do the new year.
    #races = [u.url for u in Race.objects.filter(date__year=2011,
    #                                            gran_prix='N')]
    races = [u.url for u in Race.objects.filter(date__year=2011)]
    urls += races
else:
    from_date = None

if from_date:
    all_runners = Runner.objects.filter(
        Q(date_created__gte = from_date) |
        Q(date_modified__gte = from_date)
        )
else:
    all_runners = Runner.objects.all()

tmpDir = '%s/%s' % (tempfile.gettempdir(),
                    date.today().strftime('%Y%m%d'))
if not os.path.exists(tmpDir):
    os.makedirs(tmpDir)

def guess_distance(race_name):
    rv = (None,None)
    half_re = re.compile(r'(?:1/2|half)', re.IGNORECASE)
    marathon_re = re.compile(r'marathon', re.IGNORECASE)
    kilometer_re = re.compile(r'(\d+)\s*(?:K|kilometers?)\b', re.IGNORECASE)
    mile_re = re.compile(r'(\d+)\s*(?:M|mile(?:s|r)?)\b', re.IGNORECASE)
    
    if marathon_re.search(race_name):
        if half_re.search(race_name):
            rv = (13.11, 'M')
        else:
            rv = (26.22, 'M')
    m = kilometer_re.match(race_name)
    if m:
        rv = (m.group(1), 'K')
    m = mile_re.match(race_name)
    if m:
        rv = (m.group(1), 'M')

    return(rv)
    
    
for url in urls:
    output = '%s/%s' % (tmpDir, url.split('/')[-1:][0])
    f = open(output, 'w')

    fi_ln_regx = []
    fn_ln_regx = []
    for r in all_runners:
        runna = model_to_dict(r)
        ln = runna['sur_name']
        if re.search(r'\s+', ln):
          '''add \s* where there are spaces for regexes so that Pierre de
          Fermat (Pierre de\s*Fermat) would be picked up in the results
          had he not died in the year 1665'''
          ln = re.sub(r'\s+','\\s*',ln)

        # need to order it so lastname first or last
        firegx = r'\b%s[a-z]*?\s+\b%s\b' % (runna['first_name'][:1], ln)
        fi_ln_regx.append(firegx)
        # lastname, fi
        firegx = r'\b%s\b\s*%s' % (ln, runna['first_name'][:1])
        fi_ln_regx.append(firegx)
        fnregx = r'\b%s\s+\b%s\b' % (runna['first_name'], ln)
        fn_ln_regx.append(fnregx)
        fnregx = r'\b%s,?\s+\b%s\b' % (ln, runna['first_name'])
        fn_ln_regx.append(fnregx)

    fi_ln_regx = r'(?:' + '|'.join(fi_ln_regx) + r')';
    fn_ln_regx = r'(?:' + '|'.join(fn_ln_regx) + r')';
    filn_regx = re.compile(r'(?P<fnln>%s)' % fi_ln_regx,re.IGNORECASE)
    fnln_regx = re.compile(r'(?P<fnln>%s)' % fn_ln_regx,re.IGNORECASE)

    filehandle = urllib.urlopen(url)
    race_name = ''
    race_place = ''
    f.write("results='''\n")

    def getAthleteObj(fnln,first_initial=False):
        def _ath_obj(fn,ln):
            aObj = Runner.objects.filter(sur_name__iexact='%s' % (ln.strip(',')),
                                         first_name__iexact='%s' % (fn.strip(',')))
            return(aObj)
        def _ath_fi_obj(fn,ln):
            aObj = Runner.objects.filter(sur_name__iexact='%s' % (ln.strip(',')),
                                         first_name__istartswith='%s' % (fn[:1]))

            return(aObj)

        aName = fnln.split()
        if len(aName) > 2:
            '''The firstname or lastname has a space in it so we split it
            up into the permutations and then run it through the object
            finder.'''
            perms = list(itertools.permutations(aName))
            for p in perms:
                fn, ln = ' '.join(p[2:]), ' '.join(p[:2])
                obj = _ath_obj(fn, ln)
                if obj:
                    return(obj)
            for p in perms:
                fn, ln = ' '.join(p[2:]), ' '.join(p[:2])
                obj = _ath_fi_obj(fn, ln)
                if obj:
                    return(obj)
        else:
            fn,ln = fnln.split(None,1)

        if first_initial:
            aObj = _ath_fi_obj(fn,ln)
        else:
            aObj = _ath_obj(fn,ln)
        if aObj:
            return(aObj)
        else:
            if first_initial:
                aObj = _ath_fi_obj(ln,fn)
            else:
                aObj = _ath_obj(ln,fn)
            if aObj:
                return(aObj)
            else:
                print "Warning: can't find %s %s" % (fn,ln)

    nFinishers = 0
    nFinishRegx = re.compile(r'^\s*(\d+)')
    race_date = None
    for line in filehandle.readlines():
        nFinished = nFinishRegx.search(line[:-1])
        if nFinished:
            nFinishers = nFinished.group(1)

        m_race_name = re.match('<h1>(.*?)</h1>', line[:-1])
        if m_race_name:
            race_name = m_race_name.group(1)
        m_h2 = re.match('<h2>(.*?)</h2>', line[:-1])
        if m_h2:
            h2 = m_h2.group(1)
            race_place = h2
            race_date = parser.parse(h2, fuzzy=True).date()

        keepGoing = True
        attempt1 = fnln_regx.search(line[:-1])
        if attempt1:
            e = getAthleteObj(attempt1.group('fnln'))
            if e:
                f.write(line[:-1])
                for r in e:
                  f.write('id:%s' % r.id)
                f.write("\n")
            else:
                '''should NOT get here so it is a wtf moment. :-('''
                print 'wtf!',
                print 'okay, we can not get corresponding object id for',
                print '%s' % (attempt1.group('fnln'))
                print line[:-1]
            keepGoing = False

        if keepGoing:
            attempt2 = filn_regx.search(line[:-1])
            if attempt2:
                fn,ln = attempt2.group('fnln').split(None,1)
                e = getAthleteObj(attempt2.group('fnln'),first_initial=True)
                # could it be one of the following ids?:
                if e:
                    f.write(line[:-1])
                    for r in e:
                      f.write('%s %s- id:%s ' % (r.first_name, r.sur_name, r.id))
                    f.write("\n")
    f.write("'''\n")

    raceinfo = None
    try:
        raceinfo = Race.objects.filter(url=url)[0]
    except:
        pass

    if raceinfo:
        f.write('date = %s\n' % (raceinfo.date))
        f.write('distance = %s\n' % (raceinfo.distance))
        f.write('finishers = %s\n' % (raceinfo.finishers))
        f.write('gran_prix  = %s\n' % (raceinfo.gran_prix))
        f.write('location = "%s, %s"\n' % (raceinfo.city.city, raceinfo.city.state))
        f.write('measure = %s\n' % (raceinfo.measure))
        f.write('name = "%s"\n' % (raceinfo.name))
        f.write('place = 0, 10\n')
        f.write('time = 0, 10\n')
        f.write('url = %s\n' % (raceinfo.url))
    else:
        if race_date is None:
            f.write('date = \n')
        else:
            f.write('date = %s\n' % race_date)
        dist, measure = guess_distance(race_name)
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
        f.write('place = 0, 10\n')
        f.write('time = 0, 10\n')
        f.write('url = %s\n' % url)
    print output
