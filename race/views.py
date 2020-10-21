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
import calendar

from coolrun.race.models import Race, Result
from datetime import date, datetime
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from itertools import groupby
from pprint import pprint

AGE_GROUPS = ((0,19),(20,29),(30,39),(40,49),
              (50,59), (60,99))

def results(request, yyyy, mm):
    '''grab the results for the month and pair together the urls with
    dates that are the same.'''
    races = Race.objects.all().filter(date__year=yyyy,
                                      date__month=mm).order_by('-date')
    field = lambda race: race.date
    cal = [(day, list(items)) for day, items in groupby(races, field)]
    cal.sort(reverse=True)
    return render_to_response('results/yyyy_mm.html',
                              { 'races': races,
                                'calendar': cal})

def topDistance(request, yyyy, numRunners=20):
    kilometer = 0.621371192
    numRunners = int(numRunners)
    results = Result.objects.filter(race__date__year=yyyy)
    runnerDict = {}
    males = []
    females = []

    for result in results:
        # differentiate same names with the date-of-birth
        runnerKey = '%s %s %s' % (result.runner.gender, result.runner,
                                  result.runner.dob)
        distance = float(result.race.distance)
        if result.race.measure == 'K':
            distance *= kilometer
        try:
            runnerDict[runnerKey].append(distance)
        except KeyError:
            runnerDict[runnerKey] = [distance]

    for athlete in runnerDict:
        if athlete.startswith('M '):
            males.append((sum(runnerDict[athlete]), athlete[2:-11],
                          len(runnerDict[athlete])))
        else:
            females.append((sum(runnerDict[athlete]), athlete[2:-11],
                            len(runnerDict[athlete])))
    males.sort()
    females.sort()
    allList = zip(females[-numRunners:], males[-numRunners:])

    return render_to_response('results/top_distance.html',
                              { 'distances': sorted(list(allList),
                                                    reverse=True) })


def news_letter_results(request):
    races = Race.objects.all().order_by('date')

    return render_to_response('results/news_letter.html',
                              {'races': races})

def age(dob, today=date.today()):
    if today.month < dob.month or \
            (today.month == dob.month and today.day < dob.day):
        return today.year - dob.year - 1
    else:
        return today.year - dob.year

def gp(request, yyyy):
    results = Result.objects.filter(race__gran_prix='Y',
                                    race__date__year=yyyy)
    year_end_date = date(int(yyyy)+1, 1, 1)

    race_results = []
    for r in results:
        
        print r.runner.firstname, r.race.name
    
        
    return render_to_response('results/gp.html',
                              {'results': results})

def gran_prix(request, yyyy):
    races = Race.objects.all().filter(gran_prix='Y',
                                      date__year=yyyy).order_by('date')

    '''calculate the grandprix with a certain date.  Ours is the
    determined by anything less than the first day of next year (new
    years day)'''
    year_end_date = date(int(yyyy)+1, 1, 1)
    runDict = {}

    raceDict = {}
    raceids = [(r.date,r.id,r.name) for r in races]
    for ageMin, ageMax in AGE_GROUPS:
        for race in races:
            for result in race.results():
                runAge = int(age(result.runner.dob,year_end_date))
                if runAge >= int(ageMin) and runAge <= int(ageMax):
                    if result.runner.id in runDict:
                        runDict[result.runner.id].append({
                            'age': runAge,
                            'ageMax': ageMax,
                            'ageMin': ageMin,
                            'gender': result.runner.gender,
                            'raceId': race.id,
                            'result': result.runner,
                            'time': result.race_time,
                            })
                    else:
                        runDict[result.runner.id] = [{
                            'age': runAge,
                            'ageMax': ageMax,
                            'ageMin': ageMin,
                            'gender': result.runner.gender,
                            'raceId': race.id,
                            'result': result.runner,
                            'time': result.race_time,
                            }]

    l = sorted(runDict, key=lambda x: (runDict[x][0]['gender'].lower(),
                                       runDict[x][0]['age']))
    raceids.sort()
    res = [['Name','Age Group', races]]
    for runid in l:
        a = [runDict[runid][0]['result'], '%s to %s' % ( runDict[runid][0]['ageMin'],
                                runDict[runid][0]['ageMax'])]
        z = [x['raceId'] for x in runDict[runid]]
        events = []
        for dt, rid, n in raceids:
            if rid in z:
                events.append(runDict[runid][z.index(rid)]['time'])
            else:
                events.append(None)
        a.append(events)
        res.append(a)

    response = HttpResponse(mimetype='text/csv')
    fname = 'gp-%s.csv' % (datetime.today().strftime('%d%b%Y%H%M'))
    response['Content-Disposition'] = 'attachment; filename=%s' %(fname)
    writer = csv.writer(response)
    for n,r,races in res:
        a = [n,r]
        for race in races:
            a.append(race)
        writer.writerow(a)

    return response
    

def yyyyresults(request, yyyy):
    races = Race.objects.all().filter(date__year=yyyy).order_by('-date')
    field = lambda race: race.date
    cal = [(day, list(items)) for day, items in groupby(races, field)]
    cal.sort(reverse=True)

    return render_to_response('results/yyyy_mm.html',
                              { 'races': races,
                                'calendar': cal})
        
