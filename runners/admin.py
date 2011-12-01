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
from runners.models import City, Address, Runner
from runners.models import Club, Membership
from race.models import Race

class RunnerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'sur_name', 'maiden_name',
                    'address', 'email', 'phone', 'mobile',
                    'dob']
    ordering = ['sur_name', 'first_name', 'dob',]
    search_fields = ['first_name', 'sur_name', ]

class RaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'distance', 'measure',
                    'date', 'city', 'finishers', 'gran_prix']
    ordering = ['-date',]
    search_fields = ['name',]

class MembershipAdmin(admin.ModelAdmin):
    list_display = ['club', 'runner', 'expiration']
    ordering = ('-expiration',)

admin.site.register(Address)
admin.site.register(City)
admin.site.register(Club)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Race, RaceAdmin)
admin.site.register(Runner, RunnerAdmin)
