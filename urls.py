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
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  (r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('coolrun.runners.views',
  (r'^runners/', "runners"),
  (r'^cities/', "cities"),
  (r'^runner/(?P<runner_id>\d+)/$', "runner"),
  (r'^create/$', "create"),
  (r'^race_create/$', "race_create"),
  (r'^city/(?P<city_id>\d+)/$', "city"),
  (r'^birthday/(?P<mm>\d+)/$', "birthday_month"),
  url(r'^city_create/$', 'city_create', name='city_creation'),
  url(r'^search/', 'runners_search', name='runners_search'),
)
urlpatterns += patterns('coolrun.race.views',
  (r'^results/(?P<yyyy>\d+)/(?P<mm>\d+)/$', "results"),
  (r'^gran_prix/(?P<yyyy>\d+)/$', "gran_prix"),
  (r'^results/(?P<yyyy>\d+)/$', "yyyyresults"),
  (r'^longrun/(?P<yyyy>\d+)/$', 'topDistance'),
  (r'^newsletter/$', 'news_letter_results'),
)
