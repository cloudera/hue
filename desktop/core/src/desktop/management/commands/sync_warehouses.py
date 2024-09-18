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

# HUE_CONF_DIR=/etc/hue/conf HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1 /opt/hive/build/env/bin/hue sync_warehouses

import os
import re
import sys
import json
import logging

from django.core.management.base import BaseCommand
from kubernetes import client, config

from beeswax import models
from beeswax.conf import AUTH_PASSWORD, AUTH_USERNAME
from hadoop import confparse

LOG = logging.getLogger()

if (config.incluster_config.SERVICE_HOST_ENV_NAME in os.environ
    and config.incluster_config.SERVICE_PORT_ENV_NAME in os.environ):
  # We are running in a k8s environment and must use service account
  config.load_incluster_config()
else:
  # Try loading the default kubernetes config file. Intended for local dev
  config.load_kube_config()

core_v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
networking_v1 = client.NetworkingV1Api()

SERVER_HELP = r"""
  Sync up the desktop_connectors with the available hive and impala warehouses
"""


class Command(BaseCommand):
  def add_arguments(self, parser):
    pass

  def handle(self, *args, **options):
    sync_warehouses(args, options)

  def usage(self, subcommand):
    return SERVER_HELP


def sync_warehouses(args, options):
  computes = get_computes_from_k8s()

  hives = [c for c in computes if c['dialect'] == 'hive']
  impalas = [c for c in computes if c['dialect'] == 'impala']
  trinos = [c for c in computes if c['dialect'] == 'trino']

  (hive_warehouse, created) = models.Namespace.objects.get_or_create(
    external_id="CDW_HIVE_WAREHOUSE",
    defaults={'name': 'CDW Hive', 'description': 'CDW Hive Warehouse', 'dialect': 'hive', 'interface': 'hiveserver2'})
  add_computes_to_warehouse(hive_warehouse, hives)

  (impala_warehouse, created) = models.Namespace.objects.get_or_create(
    external_id="CDW_IMPALA_WAREHOUSE",
    defaults={'name': 'CDW Impala', 'description': 'CDW Impala Warehouse', 'dialect': 'impala', 'interface': 'hiveserver2'})
  add_computes_to_warehouse(impala_warehouse, impalas)

  (trino_warehouse, created) = models.Namespace.objects.get_or_create(
    external_id="CDW_TRINO_WAREHOUSE",
    defaults={'name': 'CDW Trino', 'description': 'CDW Trino Warehouse', 'dialect': 'trino', 'interface': 'trino'})
  add_computes_to_warehouse(trino_warehouse, trinos)

  LOG.info("Synced computes")
  LOG.debug("Current computes %s" % models.Compute.objects.all())


def add_computes_to_warehouse(warehouse, computes):
  for c in computes:
    c['namespace'] = warehouse
    models.Compute.objects.update_or_create(external_id=c['external_id'], defaults=c)
  external_ids = [c['external_id'] for c in computes]
  models.Compute.objects.filter(namespace=warehouse).exclude(external_id__in=external_ids).delete()


if __name__ == '__main__':
  args = sys.argv[1:]
  options = {}
  sync_warehouses(args, options)


def get_computes_from_k8s():
  catalogs = []
  computes = []

  label_selector = os.environ.get("K8S_LABEL_SELECTOR")  # clusterid=env-urmgt6-env

  for n in core_v1.list_namespace(label_selector=label_selector).items:
    try:
      namespace = n.metadata.name
      LOG.info('Getting details for ns: %s' % namespace)
      item = {
        'name': n.metadata.labels.get('displayname', namespace),
        'description': '%s (%s)' % (n.metadata.labels.get('displayname'), n.metadata.name),
        'external_id': namespace,
        # 'creation_timestamp': n.metadata.labels.get('creation_timestamp'),
      }

      if namespace.startswith('warehouse-'):
        catalogs.append(item)
      elif namespace.startswith('compute-'):
        update_hive_configs(namespace, item, 'hiveserver2-service.%s.svc.cluster.local' % namespace)
        computes.append(item)
      elif namespace.startswith('impala-'):
        populate_impala(namespace, item)
        computes.append(item)
      elif namespace.startswith('trino-'):
        update_trino_configs(namespace, item)
        computes.append(item)
    except Exception as e:
      LOG.exception('Could not get details for ns: %s' % (n.metadata.name if n.metadata is not None else n))

  return computes


def update_hive_configs(namespace, hive, host, port=80):
  hs2_stfs = apps_v1.read_namespaced_stateful_set('hiveserver2', namespace)

  hive_configs = core_v1.read_namespaced_config_map('hive-conf-hiveserver2', namespace)
  hive_site_data = confparse.ConfParse(hive_configs.data['hive-site.xml'])
  ldap_groups = hive_site_data.get('hive.server2.authentication.ldap.groupFilter', '')
  hive_metastore_uris = hive_site_data.get('hive.metastore.uris')

  settings = [
    {"name": "server_host", "value": host},
    {"name": "server_port", "value": port},
    {"name": "transport_mode", "value": 'http'},
    {"name": "http_url", "value": 'http://%s:%s/cliservice' % (host, port)},
    {"name": "auth_username", "value": AUTH_USERNAME.get()},
    {"name": "auth_password", "value": AUTH_PASSWORD.get()},
    {"name": "is_llap", "value": False},
    {"name": "use_sasl", "value": True},
    {"name": "hive_metastore_uris", "value": hive_metastore_uris},
  ]

  hive.update({
    'dialect': 'hive',
    'interface': 'hiveserver2',
    'is_ready': bool(hs2_stfs.status.ready_replicas),
    'ldap_groups': ldap_groups.split(",") if ldap_groups else None,
    'settings': json.dumps(settings)
  })


def populate_impala(namespace, impala):
  deployments = apps_v1.list_namespaced_deployment(namespace).items
  stfs = apps_v1.list_namespaced_stateful_set(namespace).items
  catalogd_dep = next((d for d in deployments if d.metadata.labels['app'] == 'catalogd'), None)
  catalogd_stfs = next((s for s in stfs if s.metadata.labels['app'] == 'catalogd'), None)
  statestore_dep = next((d for d in deployments if d.metadata.labels['app'] == 'statestored'), None)
  admissiond_dep = next((d for d in deployments if d.metadata.labels['app'] == 'admissiond'), None)

  impala['is_ready'] = bool(((catalogd_dep and catalogd_dep.status.ready_replicas) or (
        catalogd_stfs and catalogd_stfs.status.ready_replicas))
                     and (statestore_dep and statestore_dep.status.ready_replicas)
                     and (admissiond_dep and admissiond_dep.status.ready_replicas))

  if not impala['is_ready']:
    LOG.info("Impala %s not ready" % namespace)

  impala_proxy = next((d for d in deployments if d.metadata.labels['app'] == 'impala-proxy'), None)
  if impala_proxy:
    impala['server_port'] = 25000
    impala['api_port'] = 25000
    update_impala_configs(namespace, impala, 'impala-proxy.%s.svc.cluster.local' % namespace)
  else:
    coordinator = next((s for s in stfs if s.metadata.labels['app'] == 'coordinator'), None)
    impala['is_ready'] = impala['is_ready'] and (coordinator and coordinator.status.ready_replicas)

    hs2_stfs = next((s for s in stfs if s.metadata.labels['app'] == 'hiveserver2'), None)
    if hs2_stfs:
      # Impala is running with UA
      impala['is_ready'] = impala['is_ready'] and hs2_stfs.status.ready_replicas
      update_hive_configs(namespace, impala, 'hiveserver2-service.%s.svc.cluster.local' % namespace)
    else:
      # Impala is not running with UA
      svcs = core_v1.list_namespaced_service(namespace).items
      coordinator_svc = next((s for s in svcs if s.metadata.labels['app'] == 'coordinator'), None)
      ports = coordinator_svc.spec.ports if coordinator_svc else []
      impala['server_port'] = next((p.port for p in ports if p.name == 'http'), 28000)
      impala['api_port'] = next((p.port for p in ports if p.name == 'web'), 25000)
      update_impala_configs(namespace, impala, 'coordinator.%s.svc.cluster.local' % namespace)


def update_impala_configs(namespace, impala, host):
  hive_configs = core_v1.read_namespaced_config_map('impala-coordinator-hive-conf', namespace)
  hive_site_data = confparse.ConfParse(hive_configs.data['hive-site.xml'])
  hive_metastore_uris = hive_site_data.get('hive.metastore.uris')

  impala_flag_file = core_v1.read_namespaced_config_map('impala-coordinator-flagfile', namespace)
  flag_file_data = impala_flag_file.data['flagfile']
  ldap_regex = r'--ldap_group_filter=(.*)'
  match = re.search(ldap_regex, flag_file_data)
  ldap_groups = match.group(1) if match and match.group(1) else None

  settings = [
    {"name": "server_host", "value": host},
    {"name": "server_port", "value": impala['server_port']},
    {"name": "api_port", "value": impala['api_port']},
    {"name": "transport_mode", "value": 'http'},
    {"name": "http_url", "value": 'http://%s:%s/cliservice' % (host, impala['server_port'])},
    {"name": "api_url", "value": 'http://%s:%s' % (host, impala['api_port'])},
    {"name": "impersonation_enabled", "value": False},
    {"name": "use_sasl", "value": False},
    {"name": "hive_metastore_uris", "value": hive_metastore_uris},
  ]

  impala.pop('server_port', None)
  impala.pop('api_port', None)
  impala.update({
    'dialect': 'impala',
    'interface': 'hiveserver2',
    'ldap_groups': ldap_groups.split(",") if ldap_groups else None,
    'settings': json.dumps(settings)
  })


def update_trino_configs(namespace, trino):
  deployments = apps_v1.list_namespaced_deployment(namespace).items
  stfs = apps_v1.list_namespaced_stateful_set(namespace).items
  ingresses = networking_v1.list_namespaced_ingress(namespace).items
  trino_worker_dep = next((d for d in deployments
                           if d.metadata.labels['app'] == 'trino' and d.metadata.labels['component'] == 'trino-worker'),
                          None)
  trino_coordinator_stfs = next((s for s in stfs if s.metadata.labels['app'] == 'trino-coordinator'), None)
  trino_coordinator_ingress = next((i for i in ingresses if i.metadata.name == 'trino-coordinator-ingress'), None)

  trino['is_ready'] = bool(trino_worker_dep and trino_worker_dep.status.ready_replicas
                       and trino_coordinator_stfs and trino_coordinator_stfs.status.ready_replicas)

  if not trino['is_ready']:
    LOG.info("Trino %s not ready" % namespace)

  coordinator_url = 'http://trino-coordinator.%s.svc.cluster.local:8080' % namespace
  settings = []

  trino_coordinator_configs = core_v1.read_namespaced_config_map('trino-coordinator-config', namespace)
  core_site_data = confparse.ConfParse(trino_coordinator_configs.data['core-site.xml'])
  ldap_bin_user = core_site_data.get('hadoop.security.group.mapping.ldap.bind.user')
  if ldap_bin_user:
    ldap_user_regex = '.*uid=([^,]+).*'
    match = re.search(ldap_user_regex, ldap_bin_user)
    ldap_user_id = match.group(1) if match and match.group(1) else None
    settings.append({"name": "auth_username", "value": ldap_user_id})
    settings.append({"name": "auth_password_script", "value": "/etc/hue/conf/altscript.sh hue.binduser.password"})
    if trino_coordinator_ingress and trino_coordinator_ingress.spec.rules:
      coordinator_url = 'https://%s:443' % trino_coordinator_ingress.spec.rules[0].host

  settings.append({"name": "url", "value": coordinator_url})

  trino.update({
    'dialect': 'trino',
    'interface': 'trino',
    'settings': json.dumps(settings)
  })
