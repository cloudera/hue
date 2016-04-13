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

import json
import logging
from lxml import etree

from django.utils.translation import ugettext as _

from oozie.models import Coordinator, BundledCoordinator
from oozie.utils import oozie_to_django_datetime


LOG = logging.getLogger(__name__)

OOZIE_NAMESPACES = ['uri:oozie:bundle:0.1', 'uri:oozie:bundle:0.2']


def _set_bundle_properties(bundle, root, namespace):
  """
  Get bundle properties from bundle XML

  Set properties on ``bundle`` with attributes from XML etree ``root``.
  """
  bundle.name = root.get('name')


def _set_controls(bundle, root, namespace):
  """
  Get controls from bundle XML

  Set properties on ``bundle`` with controls from XML etree ``root``.
  """
  namespaces = {
    'n': namespace
  }
  controls = root.xpath('n:controls', namespaces=namespaces)[0]
  kick_off_time = controls.xpath('n:kick-off-time', namespaces=namespaces)
  if kick_off_time:
    bundle.kick_off_time = oozie_to_django_datetime(kick_off_time[0].text)


def _reconcile_coordinators(bundle, root, namespace):
  namespaces = {
    'n': namespace
  }
  bundle.save()

  for coordinator_el in root.xpath('n:coordinator', namespaces=namespaces):
    try:
      coordinator = Coordinator.objects.get(name=coordinator_el.get('name'), owner=bundle.owner)
      bundled_coordinator = BundledCoordinator.objects.create(bundle=bundle, coordinator=coordinator, parameters='[]')
      _set_parameters(bundled_coordinator, root, namespace)
      bundled_coordinator.save()
    except Coordinator.DoesNotExist:
      raise


def _set_parameters(bundled_coordinator, coordinator_el, namespace):
  namespaces = {
    'n': namespace
  }
  properties = []
  props = coordinator_el.xpath('n:configuration/property', namespaces=namespaces)
  for prop in props:
    name = prop.xpath('n:name', namespaces=namespaces)[0]
    value = prop.xpath('n:value', namespaces=namespaces)[0]
    properties.append({'name': name, 'value': value})
  bundled_coordinator.parameters = json.dumps(properties)


def _process_metadata(bundle, metadata):
  # Job attributes
  attributes = metadata.setdefault('attributes', {})
  bundle.description = attributes.setdefault('description', bundle.description)
  bundle.deployment_dir = attributes.setdefault('deployment_dir', bundle.deployment_dir)


def import_bundle_root(bundle, bundle_definition_root, metadata=None):
  try:
    tag = etree.QName(bundle_definition_root.tag)
    schema_version = tag.namespace

    # Ensure namespace exists
    if schema_version not in OOZIE_NAMESPACES:
      raise RuntimeError(_("Tag with namespace %(namespace)s is not valid. Please use one of the following namespaces: %(namespaces)s") % {
        'namespace': bundle_definition_root.tag,
        'namespaces': ', '.join(OOZIE_NAMESPACES)
      })

    # Resolve bundle dependencies and node types and link dependencies
    _set_bundle_properties(bundle, bundle_definition_root, schema_version)
    _set_controls(bundle, bundle_definition_root, schema_version)
    _reconcile_coordinators(bundle, bundle_definition_root, schema_version)
    if metadata:
      _process_metadata(bundle, metadata)

    # Update schema_version
    bundle.schema_version = schema_version
    bundle.save()
  except:
    LOG.exception('failed to import bundle')

    # There was an error importing the bundle so delete every thing associated with it.
    bundle.delete(skip_trash=True)
    raise


def import_bundle(bundle, bundle_definition, metadata=None):
  # Parse Bundle Definition
  bundle_definition_root = etree.fromstring(bundle_definition)
  if bundle_definition_root is None:
    raise RuntimeError(_("Could not find any nodes in Bundle definition. Maybe it's malformed?"))

  return import_bundle_root(bundle, bundle_definition_root, metadata)
