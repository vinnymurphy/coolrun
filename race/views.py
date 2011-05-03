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
from datetime import date

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from coolrun.race.models import Race, Result
from pprint import pprint

def results(request, yyyy, mm):
    races = Race.objects.all().filter(date__year=yyyy,
                                      date__month=mm).order_by('date')
    return render_to_response('results/yyyy_mm.html',
                              { 'races': races})

def news_letter_results(request):
    races = Race.objects.all().order_by('date')

    return render_to_response('results/news_letter.html',
                              {'races': races})

def gran_prix(request, yyyy):
    races = Race.objects.all().filter(gran_prix='Y',
                                      date__year=yyyy).order_by('date')
    age_groups = ((0,19),(20,29),(30,39),(40,49),
                  (50,59), (60,99))
    gender = ['F','M']
    def age(dob, today=date.today()):
        if today.month < dob.month or \
                (today.month == dob.month and today.day < dob.day):
            return today.year - dob.year - 1
        else:
            return today.year - dob.year
    '''calculate the grandprix with a certain date.  Ours is the
    determined by anything less than the first day of next year (new
    years day)'''
    year_end_date = date(int(yyyy)+1, 1, 1)
    runDict = {}
    for g in gender:
        raceDict = {}
        for ageMin, ageMax in age_groups:
            for race in races:
                for result in race.results():
                    runAge = int(age(result.runner.dob,year_end_date))
                    if runAge >= int(ageMin) and runAge <= int(ageMax)\
                           and g == result.runner.gender:
                        if result.runner.id in runDict:
                            runDict[result.runner.id].append({
                                'ageMin': ageMin,
                                'ageMax': ageMax,
                                'age': runAge,
                                'raceId': race.id,
                                'time': result.race_time,
                                'result': result.runner,})
                        else:
                            runDict[result.runner.id] = [{
                                'ageMin': ageMin,
                                'ageMax': ageMax,
                                'age': runAge,
                                'raceId': race.id,
                                'time': result.race_time,
                                'result': result.runner,}]
    pprint(runDict)
    return render_to_response('results/gp.html',
                              {'races': races, 'runners': runDict,} )
    

def yyyyresults(request, yyyy):
    races = Race.objects.all().filter(date__year=yyyy).order_by('-date')
    return render_to_response('results/yyyy_mm.html',
                              { 'races': races})
        
