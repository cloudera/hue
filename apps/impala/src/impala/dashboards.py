#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
import json

from math import log

from django.utils.translation import ugettext as _

from desktop.context_processors import get_app_name
from desktop.lib.django_util import JsonResponse, render
from desktop.models import Document2

from beeswax.design import hql_query
from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config

from impala.models import Dashboard, Controller


LOG = logging.getLogger(__name__)


def dashboard(request):
  dashboard_id = request.GET.get('dashboard')
  
  if dashboard_id:
    dashboard = Dashboard(document=Document2.objects.get(id=dashboard_id))
  else:
    dashboard = Dashboard()

  return render('dashboard.mako', request, {
    'query_json': json.dumps({}),
    'dashboard_json': dashboard.get_json(request.user), 
    'initial_json': json.dumps('')
  })


def query(request):  
  result = {
    'status': -1,
    'data': {}
  }
  
  dashboard = json.loads(request.POST['dashboard'])
  fqs = json.loads(request.POST['query'])['fqs']

  database = dashboard['properties'][0]['database']
  table = dashboard['properties'][0]['table']
  
  
  if fqs:
    filters = ' AND '.join(['%s = %s' % (fq['field'], value) for fq in fqs for value in fq['filter']])
  else:
    filters = ''

  if 'facet' in request.POST:
    facet = json.loads(request.POST.get('facet'))
    slot = None

    if facet['type'] == 'field':
      template = "SELECT %(field)s, COUNT(*) AS top FROM %(database)s.%(table)s WHERE %(field)s IS NOT NULL %(filters)s GROUP BY %(field)s ORDER BY top DESC LIMIT %(limit)s"
    elif facet['type'] == 'range':
      slot = (facet['properties']['end'] - facet['properties']['start']) / facet['properties']['limit']
      template = """select cast(%(field)s / %(slot)s AS int) * %(slot)s, count(*) AS top, cast(%(field)s / %(slot)s as int) as s 
       FROM %(database)s.%(table)s WHERE %(field)s IS NOT NULL GROUP BY s ORDER BY s DESC LIMIT %(limit)s"""    
    else:            
      # Simple Top
      template = "SELECT DISTINCT %(field)s FROM %(database)s.%(table)s WHERE %(field)s IS NOT NULL %(filters)s ORDER BY %(field)s DESC LIMIT %(limit)s"
    
    facet = json.loads(request.POST['facet'])
    hql = template % {
        'database': database,
        'table': table,
        'limit': facet['properties']['limit'],
        'field': facet['field'],
        'filters': (' AND ' + filters) if filters else '',
        'slot': slot
    }
    result['id'] = facet['id']
    result['field'] = facet['field']
    fields = [fq['field'] for fq in fqs]
    result['selected'] = facet['field'] in fields
  else:
    dashboard['resultsetSelectedFields'] = map(lambda f: '`%s`' % f if f in ('date',) else f, dashboard['resultsetSelectedFields'])
    fields = ', '.join(dashboard['resultsetSelectedFields']) if dashboard['resultsetSelectedFields'] else '*'
    hql = "SELECT %(fields)s FROM %(database)s.%(table)s" % {
        'database': database, 
        'table': table,
        'fields': fields
    }
    if filters:
      hql += ' WHERE ' + filters
    hql += ' LIMIT 100'

  query_server = get_query_server_config(name='impala')
  db = dbms.get(request.user, query_server=query_server)
  
  print hql
  query = hql_query(hql)  
  handle = db.execute_and_wait(query, timeout_sec=35.0)

  if handle:
    data = db.fetch(handle, rows=100)
    if 'facet' in request.POST:
      facet = json.loads(request.POST.get('facet'))
      result['type'] = facet['type']
      if facet['type'] == 'top':
        result['data'] = [{"value": row[0], "count": None, "selected": False, "cat": facet['field']} for row in data.rows()]
      else:
        result['data'] = [{"value": row[0], "count": row[1], "selected": False, "cat": facet['field']} for row in data.rows()]
    else:
      result['data'] = list(data.rows())

    result['cols'] = list(data.cols())
    result['status'] = 0
    db.close(handle)

  return JsonResponse(result)


def new_facet(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    dashboard = json.loads(request.POST.get('dashboard', '{}')) # Perms
    facet_json = json.loads(request.POST.get('facet_json', '{}'))
    facet_field = request.POST['field']

    result['message'] = ''
    result['facet'] = _create_facet(dashboard, request.user, facet_json, facet_field)

    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


def new_search(request):

  return render('dashboard.mako', request, {
    'query_json': json.dumps({}),
    'dashboard_json': json.dumps({
      'id': None,
      'layout': [],
      'dashboard': {
          'facets': [],
          'properties': [{'database': '', 'table': '', 'fields': []}]
        }
      }),
     'initial_json': json.dumps({
        'layout': [
           {"size":2,"rows":[{"widgets":[]}],"drops":["temp"],"klass":"card card-home card-column span2"},
           {"size":10,"rows":[{"widgets":[
               {"size":12,"name":"Grid Results","id":"52f07188-f30f-1296-2450-f77e02e1a5c0","widgetType":"resultset-widget",
                "properties":{},"offset":0,"isLoading":True,"klass":"card card-widget span12"}]}],
               "drops":["temp"],"klass":"card card-home card-column span10"}
         ]
     })
  })


def save(request):
  response = {'status': -1}

  dashboard = json.loads(request.POST.get('dashboard', '{}')) # TODO perms
  layout = json.loads(request.POST.get('layout', '{}'))

  if dashboard:
    name = '%s.%s' % (dashboard['properties'][0]['database'], dashboard['properties'][0]['table']) # Dynamic currently

    if dashboard.get('id'):
      dashboard_doc = Document2.objects.get(id=dashboard['id'])
    else:
      dashboard_doc = Document2.objects.create(name=name, type='impala-dashboard', owner=request.user)

    dashboard_doc.update_data({'dashboard': dashboard})
    dashboard_doc.update_data({'layout': layout})
    dashboard_doc.name = name
    dashboard_doc.save()
    response['status'] = 0
    response['id'] = dashboard_doc.id
    response['message'] = _('Page saved !')
  else:
    response['message'] = _('There is no dashboard to search.')

  return JsonResponse(response)


def get_fields(request):
  result = {'status': -1, 'message': 'Error'}

  try:
    database = request.POST.get('database')
    table = request.POST.get('table')

    result['message'] = ''
    result['fields'] = Controller(request.user).get_fields(database, table)
    result['status'] = 0
  except Exception, e:
    result['message'] = unicode(str(e), "utf8")

  return JsonResponse(result)


def _round_number_range(n):
  if n <= 10:
    return n, n + 1
  else:
    i = int(log(n, 10))
    end = round(n, -i)
    start = end - 10 ** i
    return start, end
  

def _guess_range(user, dashboard, field):
    
    hql = "SELECT MIN(%(field)s), MAX(%(field)s) FROM %(database)s.%(table)s" % {
      'field': field['name'],
      'database': dashboard['properties'][0]['database'],
      'table': dashboard['properties'][0]['table']      
    }
    
    query_server = get_query_server_config(name='impala')
    db = dbms.get(user, query_server=query_server)
    
    query = hql_query(hql)
    handle = db.execute_and_wait(query, timeout_sec=35.0)    

    data = db.fetch(handle, rows=1)
    stats_min, stats_max = list(data.rows())[0]
    db.close(handle)
    
    _min, _m = _round_number_range(stats_min)
    _m, _max = _round_number_range(stats_max)    

    properties = {
      'min': stats_min,
      'max': stats_max,
      'start': _min,
      'end': _max,
      #'gap': gap,
      'canRange': True,
      'isDate': False,
    }
    
    return properties


def _create_facet(dashboard, user, facet_json, facet_field):
  properties = {
    'sort': 'desc',
    'canRange': False,
    'stacked': False,
    'limit': 10,
    'mincount': 0,
    'isDate': False,
  }

  field = [field for field in dashboard['fields'] if field['name'] == facet_field][0]

  if field['type'] == 'int':
    facet_type = 'range'
    _props = _guess_range(user, dashboard, field)
    properties.update(_props)
  else:
    facet_type = 'field'
  
  # facet_type = 'top'
  

  if facet_json['widgetType'] == 'map-widget':
    properties['scope'] = 'world'
    properties['mincount'] = 1
    properties['limit'] = 100

  return {
    'id': facet_json['id'],
    'label': facet_field,
    'field': facet_field,
    'type': facet_type,
    'widgetType': facet_json['widgetType'],
    'properties': properties
  }
