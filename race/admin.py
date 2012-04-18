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
from django.contrib import admin
from race.models import Result
from runners.models import City, Address, Runner, Club

def make_published(modeladmin, request, queryset):
    queryset.update(in_newsletter='Y')

make_published.short_description = "Mark selected runners as published in newsletter"

def name_race(self):
    return self.race.name

def date_race(self):
    return self.race.date

def url_race(self):
    return self.race.url

class ResultAdmin(admin.ModelAdmin):
    list_display = [name_race, date_race, url_race, 'runner',
                    'place', 'race_time', 'in_newsletter']
    ordering = ['-race__date',]
    search_fields = ['runner__first_name', 'runner__sur_name',
                     'race__name']
    actions = [make_published]

admin.site.register(Result, ResultAdmin)

