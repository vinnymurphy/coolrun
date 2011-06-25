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
''' look through the csv file and populate our models.'''
import csv
import dateutil.parser
import os
import sys

top_dir = os.path.abspath(os.path.join(\
        os.path.dirname(os.path.dirname(__file__)), '..', '..', '..'))
sys.path.insert(0, top_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'coolrun.settings'

from coolrun.runners.models import City, Address
from coolrun.runners.models import Runner
from datetime import datetime

this_dir = os.path.dirname(__file__)

# grab the csv file and put it into the database.
update = os.path.join(this_dir, 'latest.csv')
fh_reader = csv.DictReader(open(update))

## Grab the values out of the spreadsheet.  The values we have for the
## columns are:
## id,firstname,MI,lastname,suffix,street_#,street,city,state,zip,
## mobilephone,homephone,dob,email,Member Since,Type,gender,Comp?,
## Exp,eNewsletter,mailit,Age
for row in fh_reader:
    ## next task: do a try block here because not all cities are in the zip
    ## file
    city_obj, city_created = City.objects.get_or_create(zipcode=row['zip'])
    addr_obj, addr_created = Address.objects.get_or_create(
        number=row['street_#'],
        street=row['street'],
        city=city_obj)
    if row['dob']:
        dob = dateutil.parser.parse(row['dob'])
        if dob > datetime.now():
            dob = datetime(dob.year - 100, dob.month, dob.day)
    # update runners if we have the firstname, lastname and dob.  If
    # the csv file has dob change you'll have to make the change
    # manually.
    filter_attrs = {'first_name': row['firstname'],
                    'sur_name': row['lastname'],
                    'dob': dob}
    attrs = {'gender': row['gender'].upper(),
             'phone': row['homephone'],
             'mobile': row['mobilephone'],
             'address': addr_obj,
             'email': row['email'],}
    runner = Runner.objects.filter(**filter_attrs).update(**attrs)
    if not runner:
        print 'adding %s %s to the database' % (row['firstname'],
                                                row['lastname'])
        attrs.update(filter_attrs)
        obj = Runner.objects.create(**attrs)
