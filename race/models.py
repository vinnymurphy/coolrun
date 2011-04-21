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
from datetime import date
from coolrun.runners.models import City, Runner

class Race(models.Model):
  MEASURE_CHOICES = (('M', 'Mile'), ('K', 'Kilometer'))
  GRAN_PRIX_EVENT = (('N', 'Not a Gran Prix event'),
                     ('Y', 'Gran Prix event'))
  name = models.CharField('Race Name',max_length=120)
  url = models.URLField('URL')
  measure = models.CharField('Miles or Kilometers', max_length=1,
                             choices=MEASURE_CHOICES, default='M')
  distance = models.DecimalField('Distance', max_digits=7, decimal_places=2)
  date = models.DateField(default=date.today)
  city = models.ForeignKey(City)
  finishers = models.PositiveIntegerField()
  gran_prix = models.CharField('Gran Prix?', max_length=1,
                               choices=GRAN_PRIX_EVENT, default='N')

  def __unicode__(self):
    return self.name

  def results(self):
    return Result.objects.filter(race=self.pk).order_by('race_seconds')

  def not_in_newsletter(self):
    return Result.objects.filter(race=self.pk,
                                 in_newsletter='N').order_by('race_seconds')

  def gp_results(self):
    if self.gran_prix == 'Y':
      return Result.objects.filter(race=self.pk).order_by('race_seconds')

class Result(models.Model):
  IN_NEWS = (('N', 'Not in newsletter'), ('Y', 'In newsletter'))
  race   = models.ForeignKey(Race)
  runner = models.ForeignKey(Runner)
  place = models.IntegerField('Place')
  race_time = models.CharField(max_length=8)
  race_seconds = models.IntegerField(editable=False, default=0, blank=True)
  pace_per_mile = models.CharField(max_length=8,editable=False,
                                   default=0, blank=True)
  in_newsletter = models.CharField(max_length=1, choices=IN_NEWS,
                                   default='N')
  class Meta:
    ordering = ('-race_seconds',)
  def __unicode__(self):
    return '%s at %s per mile' % (self.runner, self.pace_per_mile)

  def save(self, **kwargs):
    secs = 0
    mile_k = 1.609344 # kilometers
    if ':' in self.race_time:
      t = self.race_time.split(':')
      if len(t) == 3:
        print t
        secs = int(t[0])*60*60 + int(t[1])*60 + int(t[2])
      if len(t) == 2:
        secs = int(t[0])*60 + int(t[1])
      if len(t) == 1:
        secs = int(t[0])
    self.race_seconds = secs
    mile_distance = self.race.distance
    if self.race.measure == 'K':
      mile_distance = float(self.race.distance) / float(mile_k)
    time_per_mile = secs / float(mile_distance)
    s = time_per_mile % 60
    m = time_per_mile/60
    self.pace_per_mile = '%d:%02d' % (m, s)
    super(Result, self).save(**kwargs)

class Club(models.Model):
  name = models.CharField('Club name', max_length=120)
  url  = models.URLField()

  def __unicode__(self):
    return self.name
