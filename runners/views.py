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

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


from coolrun.runners.forms  import RunnerForm
from coolrun.runners.forms  import RaceForm
from coolrun.runners.forms  import CityForm
from coolrun.runners.models import Runner
from coolrun.runners.models import City

def index(request):
    return HttpResponse("Hello, world. You're at the poll index.")

def birthday_month(request, mm):
  bdays = Runner.objects.all().filter(dob__month=mm)
  people_by_day = [(person.dob.day, person) for person in bdays]
  people_by_day.sort()
  p = [ person_by_day[1] for person_by_day in people_by_day ]
  return render_to_response('runners/birthday.html',
                            {'bdays': p})

def runners(request):
    runners_list = Runner.objects.all().order_by('sur_name',
                                                 'first_name')
    runners_context = {
      'runners_list': runners_list
    }
    return render_to_response('runners/index.html', runners_context,)

def runner(request, runner_id):
    try:
        m = Runner.objects.get(pk=runner_id)
    except Runner.DoesNotExist:
        raise Http404
    return render_to_response('runners/detail.html',
                              {'runner': m})

def cities(request):
    cities_list = City.objects.all().order_by('zipcode')
    return render_to_response('cities/index.html',
                              {'cities_list' : cities_list })

def city(request, city_id):
    try:
        c = City.objects.get(pk=city_id)
    except City.DoesNotExist:
        raise Http404
    return render_to_response('cities/detail.html', {'city': c})

def create(request):
  form = RunnerForm(request.POST or None)
  if form.is_valid():
    event = form.save(commit=False)
    event.save()
    if 'next' in request.POST:
      next = request.POST['next']
    else:
      next = reverse('runner_create')
    return HttpResponseRedirect(next)
  return render_to_response(
    'runners/create.html',
    { 'form': form},
    context_instance = RequestContext(request),
    )

def race_create(request):
  form = RaceForm(request.POST or None)
  if form.is_valid():
    event = form.save(commit=False)
    event.save()
    if 'next' in request.POST:
      next = request.POST['next']
    else:
      next = reverse('runner_create')
    return HttpResponseRedirect(next)
  return render_to_response(
    'runners/race_create.html',
    { 'form': form},
    context_instance = RequestContext(request),
    )

def city_create(request):
  form = CityForm(request.POST or None)
  if form.is_valid():
    event = form.save(commit=False)
    
    event.save()
    if 'next' in request.POST:
      next = request.POST['next']
    else:
      next = reverse('city_creation')
    return HttpResponseRedirect(next)
  
  return render_to_response(
    'runners/city_create.html',
    { 'form': form},
    context_instance = RequestContext(request),
  )
