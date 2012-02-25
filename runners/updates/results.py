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

import csv
import datetime
import os
import re
import sys
import time

TOP_DIR = \
    os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)),
                    '..', '..', '..'))
sys.path.insert(0, TOP_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'coolrun.settings'

from configobj import ConfigObj
from coolrun.runners.models import City, Address
from coolrun.runners.models import Club, Runner
from coolrun.race.models import Race, Result
from dateutil.parser import parse
from pprint import pprint


def run_results(filename):
    '''get the results for the athlete and run them through the django
    objects'''
    if not os.path.exists(filename):
        sys.stderr.write('Error: %s does not exist\n' % filename)
        sys.exit(1)

    result = []
    config = ConfigObj(filename)
    for line in config['results'].split('\n'):
        place = line[int(config['place'][0]):int(config['place'
                ][1])].lstrip()
        runtime = line[int(config['time'][0]):int(config['time'][1])]

        m = re.match('.*id:(\d+)', line)
        if m:
            print place, runtime
            result.append((place, runtime, m.group(1)))

        # get the zipcode

        (city, state) = config['location'].split(',', 1)
        csv_file = os.path.join(os.path.dirname(__file__),
                                '../zipcode.csv')
        reader = csv.reader(open(csv_file, 'rb'))
        city_found = False
        for row in reader:
            if row[1].lower() == city.lower() and row[2].lower() \
                == state.lower().strip():
                (city_obj, city_created) = \
                    City.objects.get_or_create(city=row[1],
                        state=row[2], zipcode=row[0])
                city_found = True
                break
        if not city_found:
            print 'Crap, can not find the city'
            sys.exit()

        # get the race information

        (race_obj, race_created) = Race.objects.get_or_create(
            name=config['name'],
            url=config['url'],
            date=config['date'],
            finishers=config['finishers'],
            measure=config['measure'],
            distance=config['distance'],
            gran_prix=config['gran_prix'],
            city=city_obj,
            )

        # insert individual results.

        for (place, t, rid) in result:
            run_obj = Runner.objects.get(pk=rid)
            print t, place, rid
            (result_obj, result_created) = \
                Result.objects.get_or_create(race=race_obj,
                    runner=run_obj, place=int(place), race_time=t)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Usage: %s <file name>\n' % sys.argv[0])
        sys.exit(1)
    run_results(sys.argv[1])
