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

''' look through the csv file and populate our models.'''

import csv
import dateutil.parser
import os
import sys

def get_city_obj(zipcode, city, state):
    '''get or create the city object.  If nothing is passed in for the
    zipcode simply make it a 00000 value and live with it.'''

    zipcode = zipcode.zfill(5)
    try:
        city_obj = City.objects.get(zipcode=zipcode)
    except City.DoesNotExist:
        (city_obj, city_created) = \
            City.objects.get_or_create(city=city, zipcode=zipcode,
                state=state)
        if city_created:
            print 'created %s, %s with zipcode of %s' % (city, state,
                    zipcode)
    return city_obj


def get_dob(dob):
    '''Use dateutil parser to figure out the date.  A side effect of
    parser is that we get future dates.  Since we cannot predict
    future babies lets live in the reality we have now.'''

    if dob:
        try:
            dob = dateutil.parser.parse(dob)
            if dob > datetime.now():
                dob = datetime(dob.year - 100, dob.month, dob.day)
        except ValueError:
            print 'error with date %s' % dob
            raise

    return dob


def update_runner(r_dict):
    '''update all the runners in the database with the latest update
    from the csv file.'''

    city_obj = get_city_obj(r_dict['Zip'], r_dict['City'],
                            state=r_dict['State'])
    (addr_obj, addr_created) = \
        Address.objects.get_or_create(number=r_dict['Street #'],
            street=r_dict['Street'], city=city_obj)
    if addr_created:
        print 'created new address.'
    fname = r_dict['First Name']
    lname = r_dict['Last Name']

    filter_attrs = {'first_name': fname, 'sur_name': lname}
    runners = Runner.objects.filter(**filter_attrs)
    if len(runners) > 1:
        print 'We see %s runners matching %s %s' % (len(runners),
                fname, lname),
        for runner in runners:
            print runner.id,
        print

    filter_attrs['dob'] = get_dob(r_dict['D.O.B.'])
    if not isinstance(filter_attrs['dob'], datetime):
        del filter_attrs['dob']

    attrs = {
        'gender': r_dict['Gender'].upper(),
        'phone': r_dict['homephone'],
        'mobile': r_dict['mobilephone'],
        'address': addr_obj,
        'email': r_dict['Email'],
        }

    runner = Runner.objects.filter(**filter_attrs).update(**attrs)

    if not runner:
        print 'adding %s %s to the database' % (r_dict['First Name'],
                r_dict['Last Name'])
        attrs.update(filter_attrs)
        runner = Runner.objects.create(**attrs)

    return runner


def update_membership(runner, year):
    '''update all the memberships in the database with the latest
    update from the csv file.'''
    club_name = 'GNBTC'

    (gnbtc, gnbtc_created) = Club.objects.get_or_create(name=club_name)
    if gnbtc_created:
        print 'We created a new Club called %s' % club_name

    expiration = date(year=int(year), month=12, day=31)
    mem_filter_attrs = {'club': gnbtc, 'runner': runner_obj}
    mem_attrs = {'expiration': expiration}
    membership = \
        Membership.objects.filter(**mem_filter_attrs).update(**mem_attrs)

    if not membership:
        print '%s %s is now a member' % (runner.first_name,
                runner.sur_name)
        mem_attrs.update(mem_filter_attrs)
        membership = Membership.objects.create(**mem_attrs)


if __name__ == "__main__":
    TOP_DIR = os.path.abspath(
        os.path.join(
            os.path.dirname(
                os.path.dirname(__file__))
            , '..', '..', '..'))
    sys.path.insert(0, TOP_DIR)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'coolrun.settings'

    from coolrun.runners.models import City, Address
    from coolrun.runners.models import Runner
    from coolrun.runners.models import Membership, Club
    from datetime import datetime, date

    THIS_DIR = os.path.dirname(__file__)
    UPDATE = os.path.join(THIS_DIR, 'latest.csv')
    FH_READER = csv.DictReader(open(UPDATE))


    for row in FH_READER:
        runner_obj = update_runner(r_dict=row)
        update_membership(runner=runner_obj, year=row['Exp'])

