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

''' grab a url, or a file for that matter, and look through it for
members that are generated from the database.'''

import os
import re
import sys
import urllib

top_dir = os.path.abspath(os.path.join(\
        os.path.dirname(os.path.dirname(__file__)), '..', '..', '..'))
sys.path.insert(0, top_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'coolrun.settings'

from coolrun.runners.models import Runner
from coolrun.race.models import Race
from django.forms.models import model_to_dict
from pprint import pprint

def fnlnRegx(objs):
    fi_ln_regx = []
    fn_ln_regx = []
    for obj in objs:
        runner = model_to_dict(obj)
        lastname = runner['sur_name']
        if re.search(r'\s+', lastname):
            lastname = re.sub(r'\s+', '\\s*', lastname)

        # need to order it so lastname first or last
        firegx = r'\b%s[a-z]*?\s+\b%s\b' % (runner['first_name'][:1], lastname)
        fi_ln_regx.append(firegx)
        # lastname, fi
        firegx = r'\b%s\b\s*%s' % (lastname, runner['first_name'][:1])
        fi_ln_regx.append(firegx)
        fnregx = r'\b%s\s+\b%s\b' % (runner['first_name'], lastname)
        fn_ln_regx.append(fnregx)
        fnregx = r'\b%s,?\s+\b%s\b' % (lastname, runner['first_name'])
        fn_ln_regx.append(fnregx)
    fi_ln_regx = r'(?:' + '|'.join(fi_ln_regx) + r')'
    fn_ln_regx = r'(?:' + '|'.join(fn_ln_regx) + r')'
    filn_regx = re.compile(r'(?P<fnln>%s)' % fi_ln_regx, re.IGNORECASE)
    fnln_regx = re.compile(r'(?P<fnln>%s)' % fn_ln_regx, re.IGNORECASE)

    return(filn_regx, fnln_regx)

        
filn_regx, fnln_regx = fnlnRegx(Runner.objects.all())


result_regx = re.compile(r'.*<a href="(/results/\S+.shtml)">')
states = ['ri', 'ma', 'nh', 'vt', 'ct']
states.sort()
coolrunning = 'http://coolrunning.com'
results = dict()
for state in states:
    page = '%s/results/11/%s.shtml' % (coolrunning, state)
    fh = urllib.urlopen(page)
    html = fh.read()
    fh.close()
    state_list = ['%s%s' % (coolrunning, r) for r
                  in result_regx.findall(html)]
    for state_url in state_list:
        raceinfo = None
        try:
            raceinfo = Race.objects.filter(url=state_url)[0]
        except:
            pass
        if not raceinfo:
            results[state_url] = 0
            urlfh = urllib.urlopen(state_url)
            for line in urlfh.readlines():
                m = fnln_regx.search(line[:-1])
                if m:
                    results[state_url] = results[state_url] + 1
                else:
                    m = filn_regx.search(line[:-1])
                    if m:
                        results[state_url] = results[state_url] + 0.25

run_dict = sorted(results.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

pprint(run_dict)    
