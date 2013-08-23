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

from desktop.lib.django_util import render
from django.http import Http404

from zookeeper import settings

from zookeeper.conf import CLUSTERS
from zookeeper.forms import CreateZNodeForm, EditZNodeForm
from zookeeper.stats import ZooKeeperStats
from zookeeper.rest import ZooKeeper
from zookeeper.utils import get_cluster_or_404


def _get_global_overview():
  clusters = CLUSTERS.get()
  return dict([(c, _get_overview(clusters[c].HOST_PORTS.get())) for c in clusters])


def _get_overview(host_ports):
  stats = {}

  for s in host_ports.split(','):
    host, port = map(str.strip, s.split(':'))

    zks = ZooKeeperStats(host, port)
    stats[s] = zks.get_stats() or {}

  return stats


def _group_stats_by_role(stats):
  leader, followers = None, []
  for host, stats in stats.items():
    stats['host'] = host

    if stats.get('zk_server_state') == 'leader':
      leader = stats

    elif stats.get('zk_server_state') == 'follower':
      followers.append(stats)

  return leader, followers


def index(request):
  overview = _get_global_overview()

  return render('index.mako', request, {
      'clusters': CLUSTERS.get(),
      'overview': overview
  })


def view(request, id):
  cluster = get_cluster_or_404(id)

  stats = _get_overview(cluster['host_ports'])
  leader, followers = _group_stats_by_role(stats)

  return render('view.mako', request, {
      'cluster': cluster, 'leader': leader, 'followers': followers,
      'clusters': CLUSTERS.get(),
  })


def clients(request, host):
  parts = host.split(':')
  if len(parts) != 2:
    raise Http404

  host, port = parts
  zks = ZooKeeperStats(host, port)
  clients = zks.get_clients()

  return render('clients.mako', request,
    dict(host=host, port=port, clients=clients))


def tree(request, id, path):
  cluster = get_cluster_or_404(id)
  zk = ZooKeeper(cluster['rest_url'])

  znode = zk.get(path)
  children = sorted(zk.get_children_paths(path))

  return render('tree.mako', request, {'cluster': cluster, 'path': path, 'znode': znode, 'children': children, 'clusters': CLUSTERS.get(),})


def delete(request, id, path):
  cluster = get_cluster_or_404(id)
  if request.method == 'POST':
    zk = ZooKeeper(cluster['rest_url'])
    try:
      zk.recursive_delete(path)
    except ZooKeeper.NotFound:
      pass

  return tree(request, id, path[:path.rindex('/')] or '/')


def create(request, id, path):
  cluster = get_cluster_or_404(id)

  if request.method == 'POST':
    form = CreateZNodeForm(request.POST)
    if form.is_valid():
      zk = ZooKeeper(cluster['rest_url'])

      full_path = ("%s/%s" % (path, form.cleaned_data['name'])).replace('//', '/')

      zk.create(full_path, form.cleaned_data['data'], sequence = form.cleaned_data['sequence'])
      return tree(request, id, path)
  else:
    form = CreateZNodeForm()

  return render('create.mako', request, {'path': path, 'form': form, 'clusters': CLUSTERS.get(),})


def edit_as_base64(request, id, path):
  cluster = get_cluster_or_404(id)
  zk = ZooKeeper(cluster['rest_url'])
  node = zk.get(path)

  if request.method == 'POST':
    form = EditZNodeForm(request.POST)
    if form.is_valid():
      # TODO is valid base64 string?
      data = form.cleaned_data['data'].decode('base64')
      zk.set(path, data, form.cleaned_data['version'])

    return tree(request, id, path)
  else:
    form = EditZNodeForm(dict(\
      data=node.get('data64', ''),
      version=node.get('version', '-1')))

  return render('edit.mako', request, {'path': path, 'form': form, 'clusters': CLUSTERS.get(),})


def edit_as_text(request, id, path):
  cluster = get_cluster_or_404(id)
  zk = ZooKeeper(cluster['rest_url'])
  node = zk.get(path)

  if request.method == 'POST':
    form = EditZNodeForm(request.POST)
    if form.is_valid():
      zk.set(path, form.cleaned_data['data'])

    return tree(request, id, path)
  else:
    form = EditZNodeForm(dict(data=node.get('data64', '').decode('base64').strip(), version=node.get('version', '-1')))

  return render('edit.mako', request, {'path': path, 'form': form, 'clusters': CLUSTERS.get(),})
