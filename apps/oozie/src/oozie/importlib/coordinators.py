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
import os
from lxml import etree

from django.core import serializers
from django.utils.translation import ugettext as _

from oozie import conf
from oozie.models import Workflow, Dataset, DataInput, DataOutput
from oozie.utils import oozie_to_django_datetime, oozie_to_hue_frequency


LOG = logging.getLogger(__name__)

OOZIE_NAMESPACES = ['uri:oozie:coordinator:0.1', 'uri:oozie:coordinator:0.2', 'uri:oozie:coordinator:0.3', 'uri:oozie:coordinator:0.4']


def _set_coordinator_properties(coordinator, root, namespace):
  """
  Get coordinator properties from coordinator XML

  Set properties on ``coordinator`` with attributes from XML etree ``root``.
  """
  coordinator.name = root.get('name')
  coordinator.timezone = root.get('timezone')
  coordinator.start = oozie_to_django_datetime(root.get('start'))
  coordinator.end = oozie_to_django_datetime(root.get('end'))
  coordinator.frequency_unit, coordinator.frequency_number = oozie_to_hue_frequency(root.get('frequency'))


def _set_controls(coordinator, root, namespace):
  """
  Get controls from coordinator XML

  Set properties on ``coordinator`` with controls from XML etree ``root``.
  """
  namespaces = {
    'n': namespace
  }
  controls_list = root.xpath('n:controls', namespaces=namespaces)

  if controls_list:
    controls = controls_list[0]
    concurrency = controls.xpath('n:concurrency', namespaces=namespaces)
    timeout = controls.xpath('n:timeout', namespaces=namespaces)
    execution = controls.xpath('n:execution', namespaces=namespaces)
    throttle = controls.xpath('n:throttle', namespaces=namespaces)
    if concurrency:
      coordinator.concurrency = concurrency[0].text
    if timeout:
      coordinator.timeout = timeout[0].text
    if execution:
      coordinator.execution = execution[0].text
    if throttle:
      coordinator.throttle = throttle[0].text


def _reconcile_datasets(coordinator, objects, root, namespace):
  """
  Reconcile datasets, datainputs, and dataoutputs.
  datasets and tied to datainputs and dataoutputs.
  Other dataset properties are set from XML tree.

  ``coordinator`` is used for look ups and creating relevant objects.
  ``objects`` should be transformed from XSLTs and loaded via django deserializers.
  ``root`` is the element root of the coordinator (lxml).
  ``namespace`` defines the XML coordinator namespace and schema version.
  """
  namespaces = {
    'n': namespace
  }
  datasets = {}
  datainputs = []
  dataoutputs = []
  coordinator.save()

  for obj in objects:
    obj.object.coordinator = coordinator
    if isinstance(obj.object, Dataset):
      obj.object.pk = None
      obj.object.save()
      dataset_elements = root.xpath('//n:dataset[@name="%s"]' % obj.object.name, namespaces=namespaces)
      for dataset_element in dataset_elements:
        obj.object.start = oozie_to_django_datetime(dataset_element.get('initial-instance'))
      datasets[obj.object.name] = obj.object
      obj.object.save()
    elif isinstance(obj.object, DataInput):
      datainputs.append(obj.object)
    elif isinstance(obj.object, DataOutput):
      dataoutputs.append(obj.object)

  for datainput in datainputs:
    datainput_elements = root.xpath('//n:data-in[@name="%s"]' % datainput.name, namespaces=namespaces)
    for datainput_element in datainput_elements:
      datainput.dataset = datasets[datainput_element.get('dataset')]
    datainput.pk = None
    datainput.save()

  for dataoutput in dataoutputs:
    dataoutput_elements = root.xpath('//n:data-out[@name="%s"]' % dataoutput.name, namespaces=namespaces)
    for dataoutput_element in dataoutput_elements:
      dataoutput.dataset = datasets[dataoutput_element.get('dataset')]
    dataoutput.pk = None
    dataoutput.save()
  # @TODO(abe): reconcile instance times

def _set_properties(coordinator, root, namespace):
  namespaces = {
    'n': namespace
  }
  properties = []
  props = root.xpath('n:action/n:workflow/n:configuration/n:property', namespaces=namespaces)
  seen = {}
  for prop in props:
    name = prop.xpath('n:name', namespaces=namespaces)[0].text
    value = prop.xpath('n:value', namespaces=namespaces)[0].text
    if name not in seen:
      properties.append({'name': name, 'value': value})
      seen[name] = True
  coordinator.job_properties = json.dumps(properties)


def _process_metadata(coordinator, metadata):
  # Job attributes
  attributes = metadata.setdefault('attributes', {})
  coordinator.description = attributes.setdefault('description', coordinator.description)
  coordinator.deployment_dir = attributes.setdefault('deployment_dir', coordinator.deployment_dir)

  try:
    # @TODO(abe): Handle managed and unmanaged cases.
    coordinator.workflow = Workflow.objects.get(name=metadata['workflow'], owner=coordinator.owner, managed=True)
  except Workflow.DoesNotExist:
    raise


def import_coordinator_root(coordinator, coordinator_definition_root, metadata=None):
  xslt_definition_fh = open("%(xslt_dir)s/coordinator.xslt" % {
    'xslt_dir': os.path.join(conf.DEFINITION_XSLT_DIR.get(), 'coordinators')
  })

  tag = etree.QName(coordinator_definition_root.tag)
  schema_version = tag.namespace

  # Ensure namespace exists
  if schema_version not in OOZIE_NAMESPACES:
    raise RuntimeError(_("Tag with namespace %(namespace)s is not valid. Please use one of the following namespaces: %(namespaces)s") % {
      'namespace': coordinator_definition_root.tag,
      'namespaces': ', '.join(OOZIE_NAMESPACES)
    })

  # Get XSLT and Transform XML
  parser = etree.XMLParser(resolve_entities=False)
  xslt = etree.parse(xslt_definition_fh, parser=parser)
  xslt_definition_fh.close()
  transform = etree.XSLT(xslt)
  transformed_root = transform(coordinator_definition_root)

  # Deserialize XML
  objects = serializers.deserialize('xml', etree.tostring(transformed_root))
  # Resolve coordinator dependencies and node types and link dependencies
  _set_coordinator_properties(coordinator, coordinator_definition_root, schema_version)
  _set_controls(coordinator, coordinator_definition_root, schema_version)
  _reconcile_datasets(coordinator, objects, coordinator_definition_root, schema_version)
  _set_properties(coordinator, coordinator_definition_root, schema_version)
  if metadata:
    _process_metadata(coordinator, metadata)

  # Update schema_version
  coordinator.schema_version = schema_version
  coordinator.save()


def import_coordinator(coordinator, coordinator_definition, metadata=None):
  # Parse Coordinator Definition
  coordinator_definition_root = etree.fromstring(coordinator_definition)
  if coordinator_definition_root is None:
    raise RuntimeError(_("Could not find any nodes in Coordinator definition. Maybe it's malformed?"))

  return import_coordinator_root(coordinator, coordinator_definition_root, metadata)
