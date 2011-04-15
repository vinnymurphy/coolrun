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

from django.db import models
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.models import PhoneNumberField
from datetime import date

class City(models.Model):
  city = models.CharField('City', max_length=40)
  state = models.CharField('State', max_length=2, choices=STATE_CHOICES,
                           default='MA')
  zipcode = models.CharField('ZIP Code', max_length=5,
                             blank=True, unique=True)
  latitude = models.DecimalField(max_digits=9, decimal_places=6,
                                 editable=False, default=0, blank=True)
  longitude = models.DecimalField(max_digits=9, decimal_places=6,
                                  editable=False, default=0, blank=True)

  class Meta:
    db_table = 'club_city'
    ordering = ('zipcode',)
    verbose_name_plural = 'Cities'

  def __unicode__(self):
    return "%s, %s %s" % ( self.city, self.state, self.zipcode )

  def save(self, **kwargs):
    '''
    There is a file called zipcode.csv that has the list of zipcodes
    throughout the country. Grab that and check to see if we have the
    longitude/latitude in it before we save off the object.
    '''
    if self.longitude == 0 and self.latitude == 0:
      import csv, os
      csv_file = os.path.join(os.path.dirname(__file__), 'zipcode.csv')
      reader = csv.reader(open(csv_file, 'rb'))
      for row in reader:
        if row and row[0].count(self.zipcode):
          self.longitude = row[4]
          self.latitude  = row[3]
          ## override any of the city/states to what we have in this
          ## file:
          self.city      = row[1]
          self.state     = row[2]
    super(City, self).save(**kwargs)

  
class Address(models.Model):
  number = models.CharField('Number', max_length=30, blank=True,
                            null=True)
  street = models.CharField('Address', max_length=40, blank=True,
                            null=True)
  city = models.ForeignKey(City)

  def __unicode__(self):
    return "%s %s, %s %s" % (self.number, self.street,
                             self.city.city, self.city.state)

  class Meta:
    db_table = 'club_address'
    verbose_name_plural = 'Addresses'

class Runner(models.Model):
  GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    )
  first_name = models.CharField('First name', max_length=50)
  nickname = models.CharField('Nickname', max_length=50,
                                  blank=True, null=True)
  sur_name = models.CharField('Last name', max_length=50)
  maiden_name = models.CharField('Maiden name', max_length=50,
                                   blank=True, null=True)
  address = models.ForeignKey(Address)
  email = models.EmailField()
  phone = PhoneNumberField('Home Phone', blank=True)
  mobile = PhoneNumberField('Mobile Phone', blank=True)
  dob = models.DateField()
  date_created = models.DateField(editable=False)
  date_modified = models.DateField(editable=False)
  gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

  class Meta:
    db_table = 'club_runner'
    ordering = ('sur_name', 'first_name')
    unique_together   = ('first_name', 'sur_name', 'dob')

  def __unicode__(self):
    return "%s %s" % ( self.first_name, self.sur_name)

  def save(self, **kwargs):
    if self.date_created == None:
      self.date_created = date.today()
    self.date_modified = date.today()
    super(Runner, self).save(**kwargs)

  def age(self):
    today = date.today()
    try:
      bday = self.dob.replace(year=today.year)
    except ValueError:
      bday = self.dob.replace(year=today.year, day=self.dob.day-1)
    if bday > today:
      return today.year - self.dob.year - 1
    else:
      return today.year - self.dob.year


class Club(models.Model):
  name = models.CharField('Club name', max_length=120)
  url  = models.URLField()

  class Meta:
    db_table = 'clubs'
  def __unicode__(self):
    return self.name
  
