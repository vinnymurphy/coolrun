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
import dateutil.parser as dparser
import os
import re

from coolrunner.runner.models import Runner, StreetAddress, Club
from datetime import date
from django.contrib.contenttypes.models import ContentType
from pprint import pprint

THIS_DIR = os.path.dirname(__file__)

# grab the csv file and put it into the database.
update = os.path.join(THIS_DIR, 'latest.csv')
dr = csv.DictReader(open(update))

# id,firstname,MI,lastname,suffix,street_#,street,city,state,zip,
# mobilephone,homephone,dob,email,Member Since,Type,gender,Comp?,
# Exp,email,mailit,Age
gnbtc_obj = Club.objects.get(name='Greater New Bedford Track Club')
for row in dr:
    if row['dob']:
        if re.match(r'\d+/\d+/\d+', row['dob']):
            dob = dparser.parse(row['dob'])
            if dob.year > date.today().year:
                ''' most likely they are not more than 100 years old'''
                dob = dob.replace(year=dob.year - 100)

    runner_obj, created = \
                Runner.objects.get_or_create(first_name=row['firstname'],
                                             last_name=row['lastname'],
                                             gender=row['gender'],
                                             dob=dob,
                                             club=gnbtc_obj )
    ctRunner = ContentType.objects.get(id=runner_obj.id)
    pprint(ctRunner)

#     if row['street_#']:
#         street = '%s %s' % (row['street_#'], row['street'])
#     else:
#         street = row['street']

#     addr_obj, addr_created = StreetAddress.objects.get_or_create(
#         content_type=ctRunner,
# #        object_id=0,
#         street=street,
#         city=row['city'],
#         state=row['state'],
#         zip_code=row['zip'])
                                                                 

