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
import copy
import logging
import re
import StringIO
import time
import zipfile

from datetime import datetime,  timedelta
from string import Template
from itertools import chain

from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.forms.models import inlineformset_factory
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext as _, ugettext_lazy as _t
import django.utils.timezone as dtz

from desktop.log.access import access_warn
from desktop.lib import django_mako
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.models import Document
from hadoop.fs.exceptions import WebHdfsException

from hadoop.fs.hadoopfs import Hdfs
from liboozie.submittion import Submission
from liboozie.submittion import create_directories

from oozie.conf import REMOTE_SAMPLE_DIR
from oozie.utils import utc_datetime_format
from oozie.timezones import TIMEZONES

from desktop.auth.backend import is_admin


LOG = logging.getLogger(__name__)


PATH_MAX = 512
name_validator = RegexValidator(regex='^[a-zA-Z_][\-_a-zA-Z0-9]{1,39}$',
                                message=_('Enter a valid value: combination of 2 - 40 letters and digits starting by a letter'))
# To sync in worklow.models.js
DEFAULT_SLA = [
    {'key': 'enabled', 'value': False},
    {'key': 'nominal-time', 'value': ''},
    {'key': 'should-start', 'value': ''},
    {'key': 'should-end', 'value': ''},
    {'key': 'max-duration', 'value': ''},
    {'key': 'alert-events', 'value': ''},
    {'key': 'alert-contact', 'value': ''},
    {'key': 'notification-msg', 'value': ''},
    {'key': 'upstream-apps', 'value': ''},
]


class JobManager(models.Manager):

  def can_read(self, user, job_id):
    job = Job.objects.select_related().get(pk=job_id).get_full_node()
    return job.can_read(user)

  def can_read_or_exception(self, request, job_id, exception_class=PopupException):
    if job_id is None:
      return
    try:
      job = Job.objects.select_related().get(pk=job_id).get_full_node()
      if job.can_read(request.user):
        return job
      else:
        message = _("Permission denied. %(username)s does not have the permissions required to access job %(id)s") % \
            {'username': request.user.username, 'id': job.id}
        access_warn(request, message)
        request.error(message)
        raise exception_class(message)

    except Job.DoesNotExist:
      raise exception_class(_('job %(id)s does not exist') % {'id': job_id})

  def can_edit_or_exception(self, request, job, exception_class=PopupException):
    if job.is_editable(request.user):
      return True
    else:
      raise exception_class(_('Not allowed to modified this job'))


class Job(models.Model):
  """
  Base class for Oozie Workflows, Coordinators and Bundles.
  """
  owner = models.ForeignKey(User, db_index=True, verbose_name=_t('Owner'), help_text=_t('Person who can modify the job.')) # Deprecated
  name = models.CharField(max_length=255, blank=False, validators=[name_validator], # Deprecated
      help_text=_t('Name of the job, which must be unique per user.'), verbose_name=_t('Name'))
  description = models.CharField(max_length=1024, blank=True, verbose_name=_t('Description'), # Deprecated
                                 help_text=_t('The purpose of the job.'))
  last_modified = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Last modified'))
  schema_version = models.CharField(max_length=128, verbose_name=_t('Schema version'),
                                    help_text=_t('The version of the XML schema used to talk to Oozie.'))
  deployment_dir = models.CharField(max_length=1024, blank=True, verbose_name=_t('HDFS deployment directory'),
                                    help_text=_t('The path on the HDFS where all the workflows and '
                                                'dependencies must be uploaded.'))
  is_shared = models.BooleanField(default=False, db_index=True, verbose_name=_t('Is shared'), # Deprecated
                                  help_text=_t('Enable other users to have access to this job.'))
  parameters = models.TextField(default='[{"name":"oozie.use.system.libpath","value":"true"}]', verbose_name=_t('Oozie parameters'),
                                help_text=_t('Parameters used at the submission time (e.g. market=US, oozie.use.system.libpath=true).'))
  is_trashed = models.BooleanField(default=False, db_index=True, verbose_name=_t('Is trashed'), blank=True, # Deprecated
                                   help_text=_t('If this job is trashed.'))
  doc = GenericRelation(Document, related_query_name='oozie_doc')
  data = models.TextField(blank=True, default=json.dumps({}))  # e.g. data=json.dumps({'sla': [python data], ...})

  objects = JobManager()

  def delete(self, skip_trash=False, *args, **kwargs):
    if skip_trash:
      self.doc.all().delete()
      return super(Job, self).delete(*args, **kwargs)
    else:
      for job in self.doc.all():
        job.send_to_trash()
      return self

  def restore(self):
    self.doc.get().restore_from_trash()
    return self

  def save(self):
    super(Job, self).save()

    if not self.deployment_dir:
      default_dir = Hdfs.join(REMOTE_SAMPLE_DIR.get(), '_%s_-oozie-%s-%s' % (self.owner.username, self.id, time.time()))
      self.deployment_dir = default_dir
      super(Job, self).save()

  def is_deployed(self, fs):
    return self.deployment_dir != '' and fs.exists(self.deployment_dir)

  def __str__(self):
    res = '%s - %s' % (force_unicode(self.name), self.owner)
    return force_unicode(res)

  def get_full_node(self):
    try:
      return self.workflow
    except Workflow.DoesNotExist:
      pass
    try:
      return self.coordinator
    except Coordinator.DoesNotExist:
      pass
    try:
      return self.bundle
    except Bundle.DoesNotExist:
      pass

  def get_type(self):
    return self.get_full_node().get_type()

  def get_absolute_url(self):
    return self.get_full_node().get_absolute_url()

  def get_parameters(self):
    return json.loads(self.parameters)

  def add_parameter(self, name, value):
    oozie_parameters = self.get_parameters()
    oozie_parameters.append({"name": name, "value": value})
    self.parameters = json.dumps(oozie_parameters)

  @property
  def parameters_escapejs(self):
    return self._escapejs_parameters_list(self.parameters)

  def _escapejs_parameters_list(self, parameters):
    return json.dumps(json.loads(parameters), cls=JSONEncoderForHTML)

  @property
  def status(self):
    # TODO
    if self.is_shared:
      return _('shared')
    else:
      return _('personal')

  def find_all_parameters(self):
    params = self.find_parameters()

    if hasattr(self, 'sla') and self.sla_enabled:
      for param in find_json_parameters(self.sla):
        if param not in params:
          params[param] = ''

    for param in self.get_parameters():
      params[param['name'].strip()] = param['value']

    return  [{'name': name, 'value': value} for name, value in params.iteritems()]

  def can_read(self, user):
    try:
      return self.doc.get().can_read(user)
    except Exception, e:
      LOG.error('can_read failed because the object has more than one document: %s' % self.doc.all())
      raise e

  def is_editable(self, user):
    return is_admin(user) or self.owner == user or self.doc.get().can_write(user)

  @property
  def data_dict(self):
    if not self.data:
      self.data = json.dumps({})
    data_python = json.loads(self.data)
    # Backward compatibility
    if 'sla' not in data_python:
      data_python['sla'] = copy.deepcopy(DEFAULT_SLA)
    if 'credentials' not in data_python:
      data_python['credentials'] = []
    return data_python

  @property
  def data_js_escaped(self):
    return json.dumps(self.data_dict, cls=JSONEncoderForHTML)

  @property
  def sla(self):
    return self.data_dict['sla']

  @sla.setter
  def sla(self, sla):
    data_ = self.data_dict
    data_['sla'] = sla
    self.data = json.dumps(data_)

  @property
  def sla_enabled(self):
    return self.sla[0]['value'] # #1 is enabled


class WorkflowManager(models.Manager):
  SCHEMA_VERSION = {
    '0.4': 'uri:oozie:workflow:0.4',
    '0.5': 'uri:oozie:workflow:0.5'
  }

  def new_workflow(self, owner):
    workflow = Workflow(owner=owner, schema_version=WorkflowManager.SCHEMA_VERSION['0.4'])
    workflow.save()

    kill = Kill(name='kill', workflow=workflow, node_type=Kill.node_type)
    end = End(name='end', workflow=workflow, node_type=End.node_type)
    start = Start(name='start', workflow=workflow, node_type=Start.node_type)

    to = Link(parent=start, child=end, name='to')
    related = Link(parent=start, child=end, name='related')

    workflow.start = start
    workflow.start.save()
    workflow.end = end
    workflow.end.save()

    return workflow

  def initialize(self, workflow, fs=None):
    Kill.objects.create(name='kill', workflow=workflow, node_type=Kill.node_type)
    end = End.objects.get(workflow=workflow)
    start = Start.objects.get(workflow=workflow)

    link = Link(parent=start, child=end, name='to')
    link.save()

    Link.objects.create(parent=start, child=end, name='related')

    workflow.start = start
    workflow.end = end
    workflow.save()

    Document.objects.link(workflow, owner=workflow.owner, name=workflow.name, description=workflow.description)

    if fs:
      self.check_workspace(workflow, fs)

  def check_workspace(self, workflow, fs):
    create_directories(fs, [REMOTE_SAMPLE_DIR.get()])
    create_directories(fs)

    if workflow.is_shared:
      perms = 0755
    else:
      perms = 0711

    Submission(workflow.owner, workflow, fs, None, {})._create_dir(workflow.deployment_dir, perms=perms)

  def destroy(self, workflow, fs):
    Submission(workflow.owner, workflow, fs, None, {}).remove_deployment_dir()
    try:
      workflow.coordinator_set.update(workflow=None) # In Django 1.3 could do ON DELETE set NULL
    except:
      LOG.exception('failed to destroy workflow')

    workflow.save()
    workflow.delete(skip_trash=True)

  def managed(self):
    return self.filter(managed=True)

  def unmanaged(self):
    return self.filter(managed=False)


class Workflow(Job):
  is_single = models.BooleanField(default=False)
  start = models.ForeignKey('Start', related_name='start_workflow', blank=True, null=True)
  end  = models.ForeignKey('End', related_name='end_workflow',  blank=True, null=True)
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the Job Properties element override properties specified in the '
                                          'files specified in the Job XML element.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('Job configuration properties used by all the actions of the workflow '
                                                 '(e.g. mapred.job.queue.name=production)'))
  managed = models.BooleanField(default=True)

  objects = WorkflowManager()

  HUE_ID = 'hue-id-w'
  ICON = 'oozie/art/icon_oozie_workflow_48.png'
  METADATA_FORMAT_VERSION = "0.0.1"

  def get_type(self):
    return 'workflow'

  def get_properties(self):
    return json.loads(self.job_properties)

  def clone(self, fs, new_owner=None):
    source_deployment_dir = self.deployment_dir # Needed
    nodes = self.node_set.all()
    links = Link.objects.filter(parent__workflow=self)

    name = self.name + '-copy'
    if new_owner is not None:
      owner = new_owner
    else:
      owner = self.owner

    copy = self
    copy.pk = None
    copy.id = None
    copy.name = name
    copy.deployment_dir = ''
    copy.owner = owner
    copy.save()

    copy_doc = Document.objects.link(copy,
        owner=copy.owner,
        name=copy.name,
        description=copy.description)

    copy_doc.save()
    copy.doc.all().delete()
    copy.doc.add(copy_doc)

    old_nodes_mapping = {}

    for node in nodes:
      prev_id = node.id
      node = node.get_full_node()
      node.pk = None
      node.id = None
      node.workflow = copy
      node.save()
      old_nodes_mapping[prev_id] = node

    for link in links:
      link.pk = None
      link.id = None
      link.parent = old_nodes_mapping[link.parent.id]
      link.child = old_nodes_mapping[link.child.id]
      link.save()

    copy.start = old_nodes_mapping[self.start.id]
    copy.end = old_nodes_mapping[self.end.id]
    copy.save()

    try:
      if copy.is_shared:
        perms = 0755
      else:
        perms = 0711
      fs.copy_remote_dir(source_deployment_dir, copy.deployment_dir, owner=copy.owner, dir_mode=perms)
    except WebHdfsException, e:
      msg = _('The copy of the deployment directory failed: %s.') % e
      LOG.error(msg)
      raise PopupException(msg)

    # Reload workflow from DB... clears relationship cache
    copy = Workflow.objects.get(id=copy.id)

    return copy

  @property
  def job_properties_escapejs(self):
    return self._escapejs_parameters_list(self.job_properties)

  def has_cycle(self):
    """
    Topological sort for detecting cycles in the directed graph.
    """
    queue = set([self.start])
    removed_edges = set()

    while queue:
      node = queue.pop()
      edges = set(node.get_children_links())
      for edge in edges:
        removed_edges.add(edge)
        # Edge has no other incoming edges
        if not set(edge.child.get_parent_links()) - removed_edges:
          queue.add(edge.child)

    graph_edges = set([edge for node in self.node_set.all() for edge in node.get_children_links()])

    return len(graph_edges - removed_edges) > 0 # Graph does not have unseen edges

  def find_parameters(self):
    params = set()

    if self.sla_enabled:
      for param in find_json_parameters(self.sla):
        params.add(param)

    for node in self.node_list:
      if hasattr(node, 'find_parameters'):
        params.update(node.find_parameters())

    return dict([(param, '') for param in list(params)])

  @property
  def actions(self):
    return Node.objects.filter(workflow=self, node_type__in=Action.types)

  @property
  def node_list(self):
    """Return a flatten node list ordered by the hierarchy of the nodes in the workflow"""
    def flatten(nodes):
      flat = []
      if type(nodes) == list:
        for node in nodes:
          flat.extend(flatten(node))
      else:
        flat.append(nodes)
      return flat

    def from_iterable(iterables):
      # Python 2.6 chain.from_iterable(['ABC', 'DEF']) --> A B C D E F
      for it in iterables:
        for element in it:
          yield element

    return list(chain(from_iterable([flatten(row) for row in self.get_hierarchy()])))

  @classmethod
  def get_application_path_key(cls):
    return 'oozie.wf.application.path'

  @classmethod
  def get_application_filename(cls):
    return 'workflow.xml'

  def get_absolute_url(self):
    if self.doc.only('extra').get().extra == 'jobsub':
      return '/jobsub/#edit-design/%s' % self.id
    else:
      return reverse('oozie:edit_workflow', kwargs={'workflow': self.id}) + '#editWorkflow'

  def get_hierarchy(self):
    node = Start.objects.get(workflow=self) # Uncached version of start.
    kill = Kill.objects.get(workflow=node.workflow)
    # Special case: manage error email actions separately
    try:
      kill_nodes = [Link.objects.filter(child=kill).get(name='ok').parent, kill]
    except Link.DoesNotExist:
      kill_nodes = [kill]
    return self.get_hierarchy_rec(node=node) + [kill_nodes, [End.objects.get(workflow=node.workflow)]]

  def get_hierarchy_rec(self, node=None):
    if node is None:
      node = self.start
      if node.id is None:
        return []

    node = node.get_full_node()
    parents = node.get_parents()

    if isinstance(node, End):
      return [] # Not returning the end node
    elif isinstance(node, Decision):
      children = node.get_children('start')
      return [[node] + [[self.get_hierarchy_rec(node=child) for child in children],
                        node.get_child_end()]] + self.get_hierarchy_rec(node.get_child_end().get_child('to'))
    elif isinstance(node, DecisionEnd):
      return []
    elif isinstance(node, Fork):
      children = node.get_children('start')
      return [[node] + [[self.get_hierarchy_rec(node=child) for child in children],
                        node.get_child_join()]] + self.get_hierarchy_rec(node.get_child_join().get_child('to'))
    elif isinstance(node, Join):
      return []

    else:
      child = Link.objects.filter(parent=node).exclude(name__in=['related', 'kill', 'error'])[0].child
      return [node] + self.get_hierarchy_rec(child)

  def gen_status_graph(self, oozie_workflow):
    from oozie.forms import NodeMetaForm  # Circular dependency
    actions = oozie_workflow.get_working_actions()
    controls = oozie_workflow.get_control_flow_actions()
    WorkflowFormSet = inlineformset_factory(Workflow, Node, form=NodeMetaForm, max_num=0, can_order=False, can_delete=False)
    forms = WorkflowFormSet(instance=self).forms
    template = 'editor/gen/workflow-graph-status.xml.mako'

    index = dict([(form.instance.id, form) for form in forms])
    actions_index = dict([(action.name, action) for action in actions])
    controls_index = dict([(control.name.strip(':'), control) for control in controls])

    return django_mako.render_to_string(template, {'nodes': self.get_hierarchy(), 'index': index, 'actions': actions_index, 'controls': controls_index})

  @classmethod
  def gen_status_graph_from_xml(cls, user, oozie_workflow):
    from oozie.importlib.workflows import import_workflow # Circular dependency

    try:
      with transaction.atomic():
        workflow = Workflow.objects.new_workflow(user)
        workflow.save()

        import_workflow(workflow, oozie_workflow.definition)
        graph =  workflow.gen_status_graph(oozie_workflow)
        node_list = workflow.node_list
        workflow.delete(skip_trash=True)
        return graph, node_list
    except Exception, e:
      LOG.warn('Workflow %s could not be converted to a graph: %s' % (oozie_workflow.id, e))

    return None, []

  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}
    tmpl = 'editor/gen/workflow.xml.mako'
    xml = re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {'workflow': self, 'mapping': mapping}))
    return force_unicode(xml)

  def compress(self, mapping=None, fp=StringIO.StringIO()):
    metadata = {
      'version': Workflow.METADATA_FORMAT_VERSION,
      'nodes': {},
      'attributes': {
        'description': self.description,
        'deployment_dir': self.deployment_dir
      }
    }
    for node in self.node_list:
      if hasattr(node, 'jar_path'):
        metadata['nodes'][node.name] = {
          'attributes': {
            'jar_path': node.jar_path
          }
        }

    xml = self.to_xml(mapping=mapping)

    zfile = zipfile.ZipFile(fp, 'w')
    zfile.writestr("workflow.xml", smart_str(xml))
    zfile.writestr("workflow-metadata.json", smart_str(json.dumps(metadata)))
    zfile.close()

    return fp

  @classmethod
  def decompress(cls, fp):
    zfile = zipfile.ZipFile(fp, 'r')
    metadata_json = zfile.read('workflow-metadata.json')
    metadata = json.loads(metadata_json)
    workflow_xml = zfile.read('workflow.xml')
    return workflow_xml, metadata

  @property
  def sla_workflow_enabled(self):
    return self.sla_enabled or any([node.sla_enabled for node in self.node_list if hasattr(node, 'sla_enabled')])

  @property
  def credentials(self):
    sub_lists = [node.credentials for node in self.node_list if hasattr(node, 'credentials')]
    return set([item['name'] for l in sub_lists for item in l if item['value']])


class Link(models.Model):
  # Links to exclude when using get_children_link(), get_parent_links() in the API
  META_LINKS = ('related',)

  parent = models.ForeignKey('Node', related_name='child_node')
  child = models.ForeignKey('Node', related_name='parent_node', verbose_name='')

  name = models.CharField(max_length=40)
  comment = models.CharField(max_length=1024, default='', blank=True)

  def __unicode__(self):
    return '%s %s %s' % (self.parent, self.child, self.name)


class Node(models.Model):
  """
  Base class for the Oozie WorkflowAction or ControlFlow Nodes.

  http://nightly.cloudera.com/cdh4/cdh/4/oozie-3.1.3-cdh4.0.0-SNAPSHOT/WorkflowFunctionalSpec.html#a3_Workflow_Nodes

  The Node model is an abstract base class. All concrete actions derive from it.
  And it provides something for the Action or ControlFlow to reference.

  See https://docs.djangoproject.com/en/dev/topics/db/models/#multi-table-inheritance
  """
  PARAM_FIELDS = ()

  name = models.CharField(max_length=255, validators=[name_validator], verbose_name=_t('Name'),
                          help_text=_t('Name of the action, which must be unique by workflow.'))
  description = models.CharField(max_length=1024, blank=True, default='', verbose_name=_t('Description'),
                                 help_text=_t('The purpose of the action.'))
  node_type = models.CharField(max_length=64, blank=False, verbose_name=_t('Type'),
                               help_text=_t('The type of action (e.g. MapReduce, Pig...)'))
  workflow = models.ForeignKey(Workflow)
  children = models.ManyToManyField('self', related_name='parents', symmetrical=False, through=Link)
  data = models.TextField(blank=True, default=json.dumps({}))

  def get_full_node(self):
    if self.node_type == Mapreduce.node_type:
      node = self.mapreduce
    elif self.node_type == Pig.node_type:
      node = self.pig
    elif self.node_type == Hive.node_type:
      node = self.hive
    elif self.node_type == Sqoop.node_type:
      node = self.sqoop
    elif self.node_type == Ssh.node_type:
      node = self.ssh
    elif self.node_type == Shell.node_type:
      node = self.shell
    elif self.node_type == DistCp.node_type:
      node = self.distcp
    elif self.node_type == Fs.node_type:
      node = self.fs
    elif self.node_type == Email.node_type:
      node = self.email
    elif self.node_type == SubWorkflow.node_type:
      node = self.subworkflow
    elif self.node_type == Streaming.node_type:
      node = self.streaming
    elif self.node_type == Java.node_type:
      node = self.java
    elif self.node_type == Generic.node_type:
      node = self.generic
    elif self.node_type == Start.node_type:
      node = self.start
    elif self.node_type == End.node_type:
      node = self.end
    elif self.node_type == Kill.node_type:
      node = self.kill
    elif self.node_type == Fork.node_type:
      node = self.fork
    elif self.node_type == Join.node_type:
      node = self.join
    elif self.node_type == Decision.node_type:
      node = self.decision
    elif self.node_type == DecisionEnd.node_type:
      node = self.decisionend
    else:
      raise Exception(_('Unknown Node type: %s. Was it set at its creation?'), (self.node_type,))

    return node

  def find_parameters(self):
    return find_parameters(self, self.PARAM_FIELDS)

  def __unicode__(self):
    if self.name != '':
      return '%s' % self.name
    else:
      return '%s-%s' % (self.node_type, self.id)

  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}
    node = self.get_full_node()

    data = {
      'node': node,
      'mapping': mapping
    }

    return django_mako.render_to_string(node.get_template_name(), data)

  # Can't use through relation directly with this Django version?
  # https://docs.djangoproject.com/en/1.2/topics/db/models/#intermediary-manytomany
  def get_link(self, name=None):
    if name is None:
      return Link.objects.exclude(name__in=Link.META_LINKS).get(parent=self)
    else:
      return Link.objects.exclude(name__in=Link.META_LINKS).get(parent=self, name=name)

  def get_child_link(self, name=None):
    return self.get_link(name)

  def get_child(self, name=None):
    """Includes DecisionEnd nodes"""
    return self.get_link(name).child.get_full_node()

  def get_oozie_child(self, name=None):
    """Resolves DecisionEnd nodes"""
    child = self.get_link(name).child.get_full_node()
    if child and child.node_type == DecisionEnd.node_type:
      child = child.get_oozie_child('to')
    return child

  def get_children(self, name=None):
    if name is not None:
      return [link.child for link in Link.objects.exclude(name__in=Link.META_LINKS).filter(parent=self, name=name)]
    else:
      return [link.child for link in Link.objects.exclude(name__in=Link.META_LINKS).filter(parent=self)]

  def get_parent(self, name=None):
    if name is not None:
      return self.get_parent_link(name).parent.get_full_node()
    else:
      return self.get_parent_link().parent.get_full_node()

  def get_parents(self):
    return [link.parent for link in self.get_parent_links()]

  def get_parent_link(self, name=None):
    if name is not None:
      return Link.objects.get(child=self, name=name)
    else:
      return Link.objects.get(child=self)

  def get_parent_links(self):
    return Link.objects.filter(child=self).exclude(name__in=Link.META_LINKS)

  def get_children_links(self, name=None):
    if name is None:
      return Link.objects.exclude(name__in=Link.META_LINKS).filter(parent=self)
    else:
      return Link.objects.exclude(name__in=Link.META_LINKS).filter(parent=self, name=name)

  def get_all_children_links(self):
    return Link.objects.filter(parent=self)

  def get_template_name(self):
    return 'editor/gen/workflow-%s.xml.mako' % self.node_type

  def is_visible(self):
    return True

  def add_node(self, child):
    raise NotImplementedError(_("%(node_type)s has not implemented the 'add_node' method.") % {
      'node_type': self.node_type
    })

  @property
  def data_dict(self):
    if not self.data:
      self.data = json.dumps({})
    data_python = json.loads(self.data)
    # Backward compatibility
    if 'sla' not in data_python:
      data_python['sla'] = copy.deepcopy(DEFAULT_SLA)
    if 'credentials' not in data_python:
      data_python['credentials'] = []
    return data_python

  @property
  def sla(self):
    return self.data_dict['sla']

  @sla.setter
  def sla(self, sla):
    data_ = self.data_dict
    data_['sla'] = sla
    self.data = json.dumps(data_)

  @property
  def sla_enabled(self):
    return self.sla[0]['value'] # #1 is enabled

  @property
  def credentials(self):
    return self.data_dict['credentials']

  @credentials.setter
  def credentials(self, credentials):
    data_ = self.data_dict
    data_['credentials'] = credentials
    self.data = json.dumps(data_)


class Action(Node):
  types = ()

  class Meta:
    # Cloning does not work anymore if not abstract
    abstract = True

  def add_node(self, child):
    Link.objects.filter(parent=self, name='ok').delete()
    Link.objects.create(parent=self, child=child, name='ok')
    if not Link.objects.filter(parent=self, name='error').exists():
      Link.objects.create(parent=self, child=Kill.objects.get(name='kill', workflow=self.workflow), name='error')


# The fields with '[]' as default value are JSON dictionaries
# When adding a new action, also update
#  - Action.types below
#  - Node.get_full_node()
#  - forms.py _node_type_TO_FORM_CLS
#  - workflow.js
#  - maybe actions_utils.mako

class Mapreduce(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'jar_path', 'prepares', 'sla')
  node_type = 'mapreduce'

  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production)'))
  jar_path = models.CharField(max_length=PATH_MAX, verbose_name=_t('Jar name'),
                              help_text=_t('Name or path to the %(program)s jar file on HDFS. E.g. examples.jar.') % {'program': 'MapReduce'})
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete and then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup.'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the Job Properties element override properties specified in the '
                                          'files specified in the Job XML element.'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)

  def get_prepares(self):
    return json.loads(self.prepares)


class Streaming(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'mapper', 'reducer', 'sla')
  node_type = "streaming"

  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production)'))
  mapper = models.CharField(max_length=PATH_MAX, blank=False, verbose_name=_t('Mapper'),
                            help_text=_t('The executable/script to be used as mapper.'))
  reducer = models.CharField(max_length=PATH_MAX, blank=False, verbose_name=_t('Reducer'),
                             help_text=_t('The executable/script to be used as reducer.'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)


class Java(Action):
  PARAM_FIELDS = ('files', 'archives', 'jar_path', 'main_class', 'args',
                  'java_opts', 'job_properties', 'prepares', 'sla')
  node_type = "java"

  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  jar_path = models.CharField(max_length=PATH_MAX, blank=False, verbose_name=_t('Jar name'),
                              help_text=_t('Name or path to the %(program)s jar file on HDFS. E.g. examples.jar.') % {'program': 'Java'})
  main_class = models.CharField(max_length=256, blank=False, verbose_name=_t('Main class'),
                                help_text=_t('Full name of the Java class. E.g. org.apache.hadoop.examples.Grep'))
  args = models.TextField(blank=True, verbose_name=_t('Arguments'),
                          help_text=_t('Arguments of the main method. The value of each arg element is considered a single argument '
                                       'and they are passed to the main method in the same order.'))
  java_opts = models.CharField(max_length=256, blank=True, verbose_name=_t('Java options'),
                               help_text=_t('Command-line parameters used to start the JVM that will execute '
                                            'the Java application. Using this element is equivalent to using the mapred.child.java.opts '
                                            'configuration property. E.g. -Dexample-property=hue'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production)'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete and then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup.'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the Job Properties element override properties specified in the '
                                          'files specified in the Job XML element.'))
  capture_output = models.BooleanField(default=False, verbose_name=_t('Capture output'),
                              help_text=_t('Capture output of the stdout of the %(program)s command execution. The %(program)s '
                                           'command output must be in Java Properties file format and it must not exceed 2KB. '
                                           'From within the workflow definition, the output of an %(program)s action node is accessible '
                                           'via the String action:output(String node, String key) function') % {'program': node_type.title()})

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)

  def get_prepares(self):
    return json.loads(self.prepares)


class Pig(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'params', 'prepares', 'sla', 'credentials')
  node_type = 'pig'

  script_path = models.CharField(max_length=256, blank=False, verbose_name=_t('Script name'),
                                 help_text=_t('Script name or path to the Pig script. E.g. my_script.pig.'))
  params = models.TextField(default="[]", verbose_name=_t('Parameters'),
                            help_text=_t('The Pig parameters of the script. e.g. "-param", "INPUT=${inputDir}"'))
  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production)'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete and then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup.'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the Job Properties element override properties specified in the '
                                          'files specified in the Job XML element.'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)

  def get_params(self):
    return json.loads(self.params)

  def get_prepares(self):
    return json.loads(self.prepares)


class Hive(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'params', 'prepares', 'sla', 'credentials')
  node_type = 'hive'

  script_path = models.CharField(max_length=256, blank=False, verbose_name=_t('Script name'),
                                 help_text=_t('Script name or path to the %(type)s script. E.g. my_script.sql.') % {'type': node_type.title()})
  params = models.TextField(default="[]", verbose_name=_t('Parameters'),
                            help_text=_t('The %(type)s parameters of the script. E.g. N=5, INPUT=${inputDir}')  % {'type': node_type.title()})
  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[]',
                                    verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production)'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete, then create, before starting the application. '
                                           'This should be used exclusively for directory cleanup.'))
  job_xml = models.CharField(max_length=PATH_MAX, default='hive-config.xml', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hive hive-config.xml file bundled in the workflow deployment directory. Pick a name different than hive-site.xml.'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)

  def get_params(self):
    return json.loads(self.params)

  def get_prepares(self):
    return json.loads(self.prepares)


class Sqoop(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'params', 'prepares', 'sla', 'credentials')
  node_type = 'sqoop'

  script_path = models.TextField(blank=True, verbose_name=_t('Command'), default='',
                                 help_text=_t('The full %(type)s command. Either put it here or split it by spaces and insert the parts as multiple parameters below.')
                                             % {'type': node_type.title()})
  params = models.TextField(default="[]", verbose_name=_t('Parameters'),
                            help_text=_t('If no command is specified, split the command by spaces and insert the %(type)s parameters '
                                         'here e.g. import, --connect, jdbc:hsqldb:file:db.hsqldb, ...') % {'type': node_type.title()})
  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[]',
                                    verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production)'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the Job Properties element override properties specified in the '
                                          'files specified in the Job XML element.'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)

  def get_params(self):
    return json.loads(self.params)

  def get_prepares(self):
    return json.loads(self.prepares)


class Ssh(Action):
  PARAM_FIELDS = ('user', 'host', 'command', 'params', 'sla', 'credentials')
  node_type = 'ssh'

  user = models.CharField(max_length=64, verbose_name=_t('User'),
                          help_text=_t('User executing the shell command.'))
  host = models.CharField(max_length=256, verbose_name=_t('Host'),
                         help_text=_t('Where the shell will be executed.'))
  command = models.CharField(max_length=256, verbose_name=_t('%(type)s command') % {'type': node_type.title()},
                             help_text=_t('The command that will be executed.'))
  params = models.TextField(default="[]", verbose_name=_t('Arguments'),
                            help_text=_t('The arguments of the %(type)s command.')  % {'type': node_type.title()})
  capture_output = models.BooleanField(default=False, verbose_name=_t('Capture output'),
                              help_text=_t('Capture output of the stdout of the %(program)s command execution. The %(program)s '
                                           'command output must be in Java properties file format and it must not exceed 2KB. '
                                           'From within the workflow definition, the output of an %(program)s action node is accessible '
                                           'via the String action:output(String node, String key) function') % {'program': node_type.title()})

  def get_params(self):
    return json.loads(self.params)


class Shell(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'params', 'prepares', 'sla', 'credentials')
  node_type = 'shell'

  command = models.CharField(max_length=256, blank=False, verbose_name=_t('%(type)s command') % {'type': node_type.title()},
                             help_text=_t('The path of the Shell command to execute.'))
  params = models.TextField(default="[]", verbose_name=_t('Arguments'),
                            help_text=_t('The arguments of Shell command can then be specified using one or more argument element.'))
  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production)'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the Job Properties element override properties specified in the '
                                          'files specified in the Job XML element.'))
  capture_output = models.BooleanField(default=False, verbose_name=_t('Capture output'),
                              help_text=_t('Capture output of the stdout of the %(program)s command execution. The %(program)s '
                                           'command output must be in Java Properties file format and it must not exceed 2KB. '
                                           'From within the workflow definition, the output of an %(program)s action node is accessible '
                                           'via the String action:output(String node, String key) function') % {'program': node_type.title()})

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)

  def get_params(self):
    return json.loads(self.params)

  def get_prepares(self):
    return json.loads(self.prepares)


class DistCp(Action):
  PARAM_FIELDS = ('job_properties', 'params', 'prepares', 'sla', 'credentials')
  node_type = 'distcp'

  params = models.TextField(default="[]", verbose_name=_t('Arguments'),
                            help_text=_t('The arguments of the %(type)s command. Put options first, then source paths, then destination path.')
                                        % {'type': node_type.title()})
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the Job Properties element override properties specified in the '
                                          'files specified in the Job XML element.'))


  def get_properties(self):
    return json.loads(self.job_properties)

  def get_params(self):
    return json.loads(self.params)

  def get_prepares(self):
    return json.loads(self.prepares)


class Fs(Action):
  PARAM_FIELDS = ('deletes', 'mkdirs', 'moves', 'chmods', 'touchzs', 'sla', 'credentials')
  node_type = 'fs'

  deletes = models.TextField(default="[]", verbose_name=_t('Delete path'), blank=True,
                            help_text=_t('Delete the specified path, if it is a directory it deletes recursively all its content and '
                                         'then deletes the directory.'))
  mkdirs = models.TextField(default="[]", verbose_name=_t('Create directory'), blank=True,
                            help_text=_t('Create the specified directory, it creates all missing directories in the path. '
                                         'If the directory already exist it does a no-op.'))
  moves = models.TextField(default="[]", verbose_name=_t('Move file'), blank=True,
                            help_text=_t('Move a file or directory to another path.'))
  chmods = models.TextField(default="[]", verbose_name=_t('Change permissions'), blank=True,
                            help_text=_t('Change the permissions for the specified path. Permissions can be specified using the Unix Symbolic '
                                         'representation (e.g. -rwxrw-rw-) or an octal representation (755).'))
  touchzs = models.TextField(default="[]", verbose_name=_t('Create or touch a file'), blank=True,
                            help_text=_t('Creates a zero length file in the specified path if none exists or touch it.'))


  def get_deletes(self):
    return json.loads(self.deletes)

  def get_mkdirs(self):
    return json.loads(self.mkdirs)

  def get_moves(self):
    return json.loads(self.moves)

  def get_chmods(self):
    return json.loads(self.chmods)

  def get_touchzs(self):
    return json.loads(self.touchzs)


class Email(Action):
  PARAM_FIELDS = ('to', 'cc', 'subject', 'body', 'sla', 'credentials')
  node_type = 'email'

  to = models.TextField(default='', verbose_name=_t('TO addresses'), help_text=_t('Comma-separated values.'))
  cc = models.TextField(default='', verbose_name=_t('CC addresses (optional)'), blank=True, help_text=_t('Comma-separated values.'))
  subject = models.TextField(default='', verbose_name=_t('Subject'), help_text=_t('Plain-text.'))
  body = models.TextField(default='', verbose_name=_t('Body'), help_text=_t('Plain-text.'))


class SubWorkflow(Action):
  PARAM_FIELDS = ('subworkflow', 'propagate_configuration', 'job_properties', 'sla', 'credentials')
  node_type = 'subworkflow'

  sub_workflow = models.ForeignKey(Workflow, default=None, db_index=True, blank=True, null=True, verbose_name=_t('Sub-workflow'),
                            help_text=_t('The sub-workflow application to include. You must own all the sub-workflows.'))
  propagate_configuration = models.BooleanField(default=True, verbose_name=_t('Propagate configuration'), blank=True,
                            help_text=_t('If the workflow job configuration should be propagated to the child workflow.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('Can be used to specify the job properties that are required to run the child workflow job.'))

  def get_properties(self):
    return json.loads(self.job_properties)


class Generic(Action):
  PARAM_FIELDS = ('xml', 'credentials', 'sla', 'credentials')
  node_type = 'generic'

  xml = models.TextField(default='', verbose_name=_t('XML of the custom action'),
                         help_text=_t('This will be inserted verbatim in the action %(action)s. '
                                      'E.g. all the XML content like %(xml_action)s '
                                      'will be inserted into the action and produce %(full_action)s') % {
                                      'action': '&lt;action name="email"&gt;...&lt;/action&gt;',
                                      'xml_action': '&lt;email&gt;&lt;cc&gt;hue@hue.org&lt;/cc&gt;&lt;/email&gt;',
                                      'full_action': '&lt;action name="email"&gt;&lt;email&gt;&lt;cc&gt;hue@hue.org&lt;/cc&gt;&lt;/email&gt;&lt;ok/&gt;&lt;error/&gt;&lt;/action&gt;'})


Action.types = (Mapreduce.node_type, Streaming.node_type, Java.node_type, Pig.node_type, Hive.node_type, Sqoop.node_type, Ssh.node_type, Shell.node_type,
                DistCp.node_type, Fs.node_type, Email.node_type, SubWorkflow.node_type, Generic.node_type)


class ControlFlow(Node):
  """
  http://incubator.apache.org/oozie/docs/3.2.0-incubating/docs/WorkflowFunctionalSpec.html#a3.1_Control_Flow_Nodes
  """
  class Meta:
    abstract = True

  def get_xml(self):
    return django_mako.render_to_string(self.get_template_name(), {})

  def is_visible(self):
    return True


# Could not make this abstract
class Start(ControlFlow):
  node_type = 'start'

  def add_node(self, child):
    Link.objects.filter(parent=self).delete()
    link = Link.objects.create(parent=self, child=child, name='to')


class End(ControlFlow):
  node_type = 'end'

  def add_node(self, child):
    raise RuntimeError(_("End should not have any children."))


class Kill(ControlFlow):
  node_type = 'kill'

  message = models.CharField(max_length=256, blank=False, default='Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]')

  def add_node(self, child):
    raise RuntimeError(_("Kill should not have any children."))

  def is_visible(self):
    return False


class Fork(ControlFlow):
  """
  A Fork can be converted into a Decision node.
  """
  node_type = 'fork'

  def is_visible(self):
    return True

  def get_child_join(self):
    return Link.objects.get(parent=self, name='related').child.get_full_node()

  def convert_to_decision(self):
    self.remove_join()

    decision = Decision.objects.create(workflow=self.workflow, node_type=Decision.node_type)
    decision.save()

    links = self.get_all_children_links()
    has_default = False
    for link in links:
      if link.name == 'default':
        has_default = True
        link.parent = decision

    # Defaults to end
    if not has_default:
      link = Link.objects.create(name="default", parent=decision, child=self.workflow.end)
      link.save()

    self.delete()

    return decision

  def remove_join(self):
    join = self.get_child_join()
    after_join = join.get_child('to')

    for parent in join.get_parent_actions():
      link = parent.get_link('ok')
      link.child = after_join
      link.save()

    # Automatically delete links thought foreign keys
    join.delete()


class Join(ControlFlow):
  node_type = 'join'

  def is_visible(self):
    return True

  def get_parent_fork(self):
    return self.get_parent_link('related').parent.get_full_node()

  def get_parent_actions(self):
    return [link.parent for link in self.get_parent_links()]


class Decision(ControlFlow):
  """
  Essentially a fork where only one of the paths of execution are chosen.
  Graphically, this is represented the same way as a fork.
  The DecisionEnd node is not represented in Oozie, only in Hue.
  """
  node_type = 'decision'

  def get_child_end(self):
    return Link.objects.get(parent=self, name='related').child.get_full_node()

  def is_visible(self):
    return True

  def update_description(self):
    self.description = ', '.join(self.get_children_links().values_list('comment', flat=True))
    self.save()


class DecisionEnd(ControlFlow):
  """
  Defines the end of a join.
  This node exists purely in the Hue application to provide a smooth transition
  from Decision to Endself.

  NOTE: NOT AN OOZIE NODE
  """
  node_type = 'decisionend'

  def is_visible(self):
    return False

  def get_parent_decision(self):
    return self.get_parent_link('related').parent.get_full_node()

  def get_parent_actions(self):
    return [link.parent for link in self.get_parent_links()]

  def to_xml(self, mapping):
    return ''


FREQUENCY_UNITS = (('minutes', _('Minutes')),
                   ('hours', _('Hours')),
                   ('days', _('Days')),
                   ('months', _('Months')))
FREQUENCY_NUMBERS = [(i, i) for i in xrange(1, 61)]
DATASET_FREQUENCY = ['MINUTE', 'HOUR', 'DAY', 'MONTH', 'YEAR']


class Coordinator(Job):
  frequency_number = models.SmallIntegerField(default=1, choices=FREQUENCY_NUMBERS, verbose_name=_t('Frequency number'),
                                              help_text=_t('The number of units of the rate at which '
                                                           'data is periodically created.')) # unused
  frequency_unit = models.CharField(max_length=20, choices=FREQUENCY_UNITS, default='days', verbose_name=_t('Frequency unit'),
                                    help_text=_t('The unit of the rate at which data is periodically created.')) # unused
  timezone = models.CharField(max_length=24, choices=TIMEZONES, default='America/Los_Angeles', verbose_name=_t('Timezone'),
                              help_text=_t('The timezone of the coordinator. Only used for managing the daylight saving time changes when combining several coordinators.'))
  start = models.DateTimeField(auto_now=True, verbose_name=_t('Start'),
                               help_text=_t('When to start the first workflow.'))
  end = models.DateTimeField(auto_now=True, verbose_name=_t('End'),
                             help_text=_t('When to start the last workflow.'))
  coordinatorworkflow = models.ForeignKey(Workflow, null=True, verbose_name=_t('Workflow'),
                               help_text=_t('The workflow to schedule repeatedly.'))
  timeout = models.SmallIntegerField(null=True, blank=True, verbose_name=_t('Timeout'),
                                     help_text=_t('Number of minutes the coordinator action will be in '
                                                  'WAITING or READY status before giving up on its execution.'))
  concurrency = models.PositiveSmallIntegerField(null=True, blank=True, choices=FREQUENCY_NUMBERS, verbose_name=_t('Concurrency'),
                                 help_text=_t('The number of coordinator actions that are allowed to run concurrently (RUNNING status) '
                                              'before the coordinator engine starts throttling them.'))
  execution = models.CharField(max_length=10, null=True, blank=True, verbose_name=_t('Execution'),
                               choices=(('FIFO', _t('FIFO (oldest first) default')),
                                        ('LIFO', _t('LIFO (newest first)')),
                                        ('LAST_ONLY', _t('LAST_ONLY (discards all older materializations)'))),
                                 help_text=_t('Execution strategy of its coordinator actions when there is backlog of coordinator '
                                              'actions in the coordinator engine. The different execution strategies are \'oldest first\', '
                                              '\'newest first\' and \'last one only\'. A backlog normally happens because of delayed '
                                              'input data, concurrency control or because manual re-runs of coordinator jobs.'))
  throttle = models.PositiveSmallIntegerField(null=True, blank=True, choices=FREQUENCY_NUMBERS, verbose_name=_t('Throttle'),
                                 help_text=_t('The materialization or creation throttle value for its coordinator actions. '
                                              'Number of maximum coordinator actions that are allowed to be in WAITING state concurrently.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Workflow properties'),
                                    help_text=_t('Additional properties to transmit to the workflow, e.g. limit=100, and EL functions, e.g. username=${coord:user()}'))

  HUE_ID = 'hue-id-c'
  ICON = 'oozie/art/icon_oozie_coordinator_48.png'
  METADATA_FORMAT_VERSION = "0.0.1"
  CRON_MAPPING = {
    '0,15,30,45 * * * *': _('Every 15 minutes'),
    '0,30 * * * *': _('Every 30 minutes'),
    '0 * * * *': _('Every hour'),
    '0 0 * * *': _('Every day'),
    '0 0 * * 0': _('Every week'),
    '0 0 1 * *': _('Every month'),
    '0 0 1 1 *': _('Every year'),
  }

  def get_type(self):
    return 'coordinator'

  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}
    tmpl = "editor/gen/coordinator.xml.mako"
    return re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {'coord': self, 'mapping': mapping})).encode('utf-8', 'xmlcharrefreplace')

  def clone(self, new_owner=None):
    datasets = Dataset.objects.filter(coordinator=self)
    data_inputs = DataInput.objects.filter(coordinator=self)
    data_outputs = DataOutput.objects.filter(coordinator=self)

    name = self.name + '-copy'
    if new_owner is not None:
      owner = new_owner
    else:
      owner = self.owner

    copy = self
    copy.pk = None
    copy.id = None
    copy.name = name
    copy.deployment_dir = ''
    copy.owner = owner
    copy.save()

    copy_doc = Document.objects.link(copy,
        owner=copy.owner,
        name=copy.name,
        description=copy.description)

    copy.doc.all().delete()
    copy.doc.add(copy_doc)

    old_dataset_mapping = {}

    for dataset in datasets:
      prev_id = dataset.id
      dataset.pk = None
      dataset.id = None
      dataset.coordinator = copy
      dataset.save()
      old_dataset_mapping[prev_id] = dataset

    for data_input in data_inputs:
      data_input.pk = None
      data_input.id = None
      data_input.coordinator = copy
      data_input.dataset = old_dataset_mapping[data_input.dataset.id]
      data_input.save()

    for data_output in data_outputs:
      data_output.pk = None
      data_output.id = None
      data_output.coordinator = copy
      data_output.dataset = old_dataset_mapping[data_output.dataset.id]
      data_output.save()

    return copy

  @classmethod
  def get_application_path_key(cls):
    return 'oozie.coord.application.path'

  @classmethod
  def get_application_filename(cls):
    return 'coordinator.xml'

  def get_properties(self):
    props = json.loads(self.job_properties)
    index = [prop['name'] for prop in props]

    for prop in self.coordinatorworkflow.get_parameters():
      if not prop['name'] in index:
        props.append(prop)
        index.append(prop['name'])

    # Remove DataInputs and DataOutputs
    datainput_names = [_input.name for _input in self.datainput_set.all()]
    dataoutput_names = [_output.name for _output in self.dataoutput_set.all()]
    removable_names = datainput_names + dataoutput_names
    props = filter(lambda prop: prop['name'] not in removable_names, props)

    return props

  @property
  def job_properties_escapejs(self):
    return self._escapejs_parameters_list(self.job_properties)

  @property
  def start_utc(self):
    return utc_datetime_format(self.start)

  @property
  def end_utc(self):
    return utc_datetime_format(self.end)

  def get_absolute_url(self):
    return reverse('oozie:edit_coordinator', kwargs={'coordinator': self.id})

  @property
  def frequency(self):
    return '${coord:%(unit)s(%(number)d)}' % {'unit': self.frequency_unit, 'number': self.frequency_number}

  @property
  def text_frequency(self):
    return '%(number)d %(unit)s' % {'unit': self.frequency_unit, 'number': self.frequency_number}

  def find_parameters(self):
    params = self.coordinatorworkflow.find_parameters()

    for param in find_parameters(self, ['job_properties']):
      params[param] = ''

    if self.sla_enabled:
      for param in find_json_parameters(self.sla):
        params.add(param)

    for dataset in self.dataset_set.all():
      for param in find_parameters(dataset, ['uri']):
        if param not in set(DATASET_FREQUENCY):
          params[param] = ''

    for ds in self.datainput_set.all():
      params.pop(ds.name, None)

    for ds in self.dataoutput_set.all():
      params.pop(ds.name, None)

    for wf_param in json.loads(self.job_properties):
      params.pop(wf_param['name'], None)

    return params

  def compress(self, mapping=None, fp=StringIO.StringIO()):
    metadata = {
      'version': Coordinator.METADATA_FORMAT_VERSION,
      'workflow': self.workflow.name,
      'attributes': {
        'description': self.description,
        'deployment_dir': self.deployment_dir
      }
    }

    xml = self.to_xml(mapping=mapping)

    zfile = zipfile.ZipFile(fp, 'w')
    zfile.writestr("coordinator.xml", smart_str(xml))
    zfile.writestr("coordinator-metadata.json", smart_str(json.dumps(metadata)))
    zfile.close()

    return fp

  @classmethod
  def decompress(cls, fp):
    zfile = zipfile.ZipFile(fp, 'r')
    metadata_json = zfile.read('coordinator-metadata.json')
    metadata = json.loads(metadata_json)
    xml = zfile.read('coordinator.xml')
    return xml, metadata

  @property
  def sla_jsescaped(self):
    return json.dumps(self.sla, cls=JSONEncoderForHTML)

  @property
  def cron_frequency(self):
    if 'cron_frequency' in self.data_dict:
      return self.data_dict['cron_frequency']
    else:
      # Backward compatibility
      freq = '0 0 * * *'
      if self.frequency_number == 1:
        if self.frequency_unit == 'MINUTES':
          freq = '* * * * *'
        elif self.frequency_unit == 'HOURS':
          freq = '0 * * * *'
        elif self.frequency_unit == 'DAYS':
          freq = '0 0 * * *'
        elif self.frequency_unit == 'MONTH':
          freq = '0 0 * * *'
      return {'frequency': freq, 'isAdvancedCron': False}

  @property
  def cron_frequency_human(self):
    frequency = self.cron_frequency['frequency']
    return Coordinator.CRON_MAPPING.get(frequency, frequency)

  @cron_frequency.setter
  def cron_frequency(self, cron_frequency):
    data_ = self.data_dict
    data_['cron_frequency'] = cron_frequency
    self.data = json.dumps(data_)


class DatasetManager(models.Manager):
  def can_read_or_exception(self, request, dataset_id):
    if dataset_id is None:
      return
    try:
      dataset = Dataset.objects.get(pk=dataset_id)
      if dataset.coordinator.can_read(request.user):
        return dataset
      else:
        message = _("Permission denied. %(username)s does not have the permissions to access dataset %(id)s.") % \
            {'username': request.user.username, 'id': dataset.id}
        access_warn(request, message)
        request.error(message)
        raise PopupException(message)

    except Dataset.DoesNotExist:
      raise PopupException(_('dataset %(id)s not exist') % {'id': dataset_id})


class Dataset(models.Model):
  """
  http://oozie.apache.org/docs/3.3.0/CoordinatorFunctionalSpec.html#a6.3._Synchronous_Coordinator_Application_Definition
  """
  name = models.CharField(max_length=40, validators=[name_validator], verbose_name=_t('Name'),
                          help_text=_t('The name of the dataset.'))
  description = models.CharField(max_length=1024, blank=True, default='', verbose_name=_t('Description'),
                                 help_text=_t('A description of the dataset.'))
  start = models.DateTimeField(auto_now=True, verbose_name=_t('Start'),
                               help_text=_t(' The UTC datetime of the initial instance of the dataset. The initial instance also provides '
                                            'the baseline datetime to compute instances of the dataset using multiples of the frequency.'))
  frequency_number = models.SmallIntegerField(default=1, choices=FREQUENCY_NUMBERS, verbose_name=_t('Frequency number'),
                                              help_text=_t('The number of units of the rate at which '
                                                           'data is periodically created.'))
  frequency_unit = models.CharField(max_length=20, choices=FREQUENCY_UNITS, default='days', verbose_name=_t('Frequency unit'),
                                    help_text=_t('The unit of the rate at which data is periodically created.'))
  uri = models.CharField(max_length=1024, default='/data/${YEAR}${MONTH}${DAY}', verbose_name=_t('URI'),
                         help_text=_t('The URI template that identifies the dataset and can be resolved into concrete URIs to identify a particular '
                                      'dataset instance. The URI consist of constants (e.g. ${YEAR}/${MONTH}) and '
                                      'configuration properties (e.g. /home/${USER}/projects/${PROJECT})'))
  timezone = models.CharField(max_length=24, choices=TIMEZONES, default='America/Los_Angeles', verbose_name=_t('Timezone'),
                              help_text=_t('The timezone of the dataset. Only used for managing the daylight saving time changes when combining several datasets.'))
  done_flag = models.CharField(max_length=64, blank=True, default='', verbose_name=_t('Done flag'),
                               help_text=_t('The done file for the data set. If the Done flag is not specified, then Oozie '
                                            'configures Hadoop to create a _SUCCESS file in the output directory. If Done '
                                            'flag is set to empty, then Coordinator looks for the existence of the directory itself.'))
  coordinator = models.ForeignKey(Coordinator, verbose_name=_t('Coordinator'),
                                  help_text=_t('The coordinator associated with this data.'))
  instance_choice = models.CharField(max_length=10, default='default', verbose_name=_t('Instance type'),
                               help_text=_t('Customize the date instance(s), e.g. define a range of dates, use EL functions...'))
  advanced_start_instance  = models.CharField(max_length=128, default='0', verbose_name=_t('Start instance'),
                               help_text=_t('Shift the frequency for gettting past/future start date or enter verbatim the Oozie start instance, e.g. ${coord:current(0)}'))
  advanced_end_instance  = models.CharField(max_length=128, blank=True, default='0', verbose_name=_t('End instance'),
                               help_text=_t('Optional: Shift the frequency for gettting past/future end dates or enter verbatim the Oozie end instance.'))

  objects = DatasetManager()

  def __unicode__(self):
    return '%s' % (self.name,)

  @property
  def start_utc(self):
    return utc_datetime_format(self.start)

  @property
  def frequency(self):
    return '${coord:%(unit)s(%(number)d)}' % {'unit': self.frequency_unit, 'number': self.frequency_number}

  @property
  def text_frequency(self):
    return '%(number)d %(unit)s' % {'unit': self.frequency_unit, 'number': self.frequency_number}

  @property
  def start_instance(self):
    if not self.is_advanced_start_instance:
      return int(self.advanced_start_instance)
    else:
      return 0

  @property
  def is_advanced_start_instance(self):
    return not self.is_int(self.advanced_start_instance)

  def is_int(self, text):
    try:
      int(text)
      return True
    except ValueError:
      return False

  @property
  def end_instance(self):
    if not self.is_advanced_end_instance:
      return int(self.advanced_end_instance)
    else:
      return 0

  @property
  def is_advanced_end_instance(self):
    return not self.is_int(self.advanced_end_instance)


class DataInput(models.Model):
  name = models.CharField(max_length=40, validators=[name_validator], verbose_name=_t('Name of an input variable in the workflow.'),
                          help_text=_t('The name of the variable of the workflow to automatically fill up.'))
  dataset = models.OneToOneField(Dataset, verbose_name=_t('The dataset representing format of the data input.'),
                                 help_text=_t('The pattern of the input data we want to process.'))
  coordinator = models.ForeignKey(Coordinator)


class DataOutput(models.Model):
  name = models.CharField(max_length=40, validators=[name_validator], verbose_name=_t('Name of an output variable in the workflow'),
                          help_text=_t('The name of the variable of the workflow to automatically filled up.'))
  dataset = models.OneToOneField(Dataset, verbose_name=_t('The dataset representing the format of the data output.'),
                                 help_text=_t('The pattern of the output data we want to generate.'))
  coordinator = models.ForeignKey(Coordinator)


class BundledCoordinator(models.Model):
  bundle = models.ForeignKey('Bundle', verbose_name=_t('Bundle'),
                             help_text=_t('The bundle regrouping all the coordinators.'))
  coordinator = models.ForeignKey(Coordinator, verbose_name=_t('Coordinator'),
                                  help_text=_t('The coordinator to batch with other coordinators.'))

  parameters = models.TextField(default='[{"name":"oozie.use.system.libpath","value":"true"}]', verbose_name=_t('Parameters'),
                                help_text=_t('Constants used at the submission time (e.g. market=US, oozie.use.system.libpath=true).'))

  def get_parameters(self):
    return json.loads(self.parameters)


class Bundle(Job):
  kick_off_time = models.DateTimeField(auto_now=True, verbose_name=_t('Start'),
                                       help_text=_t('When to start the first coordinators.'))
  coordinators = models.ManyToManyField(Coordinator, through='BundledCoordinator')

  HUE_ID = 'hue-id-b'
  ICON = 'oozie/art/icon_oozie_bundle_48.png'
  METADATA_FORMAT_VERSION = '0.0.1'

  def get_type(self):
    return 'bundle'

  def to_xml(self, mapping=None):
    if mapping is None:
      mapping = {}
    tmpl = "editor/gen/bundle.xml.mako"

    return force_unicode(
              re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {
                'bundle': self,
                'mapping': mapping
           })))

  def clone(self, new_owner=None):
    bundleds = BundledCoordinator.objects.filter(bundle=self)

    name = self.name + '-copy'
    if new_owner is not None:
      owner = new_owner
    else:
      owner = self.owner

    copy = self
    copy.pk = None
    copy.id = None
    copy.name = name
    copy.deployment_dir = ''
    copy.owner = owner
    copy.save()

    copy_doc = Document.objects.link(copy,
        owner=copy.owner,
        name=copy.name,
        description=copy.description)

    copy.doc.all().delete()
    copy.doc.add(copy_doc)

    for bundled in bundleds:
      bundled.pk = None
      bundled.id = None
      bundled.bundle = copy
      bundled.save()

    return copy

  @classmethod
  def get_application_path_key(cls):
    return 'oozie.bundle.application.path'

  @classmethod
  def get_application_filename(cls):
    return 'bundle.xml'

  def get_absolute_url(self):
    return reverse('oozie:edit_bundle', kwargs={'bundle': self.id})

  def find_parameters(self):
    params = {}

    for bundled in BundledCoordinator.objects.filter(bundle=self):
      for param in bundled.coordinator.find_parameters():
        params[param] = ''

      for param in bundled.get_parameters():
        params.pop(param['name'], None)

    return params

  @property
  def kick_off_time_utc(self):
    return utc_datetime_format(self.kick_off_time)

  def compress(self, mapping=None, fp=StringIO.StringIO()):
    metadata = {
      'version': Bundle.METADATA_FORMAT_VERSION,
      'attributes': {
        'description': self.description,
        'deployment_dir': self.deployment_dir
      }
    }

    xml = self.to_xml(mapping=mapping)

    zfile = zipfile.ZipFile(fp, 'w')
    zfile.writestr("bundle.xml", smart_str(xml))
    zfile.writestr("bundle-metadata.json", smart_str(json.dumps(metadata)))
    zfile.close()

    return fp

  @classmethod
  def decompress(cls, fp):
    zfile = zipfile.ZipFile(fp, 'r')
    metadata_json = zfile.read('bundle-metadata.json')
    metadata = json.loads(metadata_json)
    xml = zfile.read('bundle.xml')
    return xml, metadata


class HistoryManager(models.Manager):
  def create_from_submission(self, submission):
    History.objects.create(submitter=submission.user,
                           oozie_job_id=submission.oozie_id,
                           job=submission.job,
                           properties=json.dumps(submission.properties))


class History(models.Model):
  """
  Contains information on submitted workflows/coordinators.
  """
  submitter = models.ForeignKey(User, db_index=True)
  submission_date = models.DateTimeField(auto_now=True, db_index=True)
  oozie_job_id = models.CharField(max_length=128)
  job = models.ForeignKey(Job, db_index=True)
  properties = models.TextField()

  objects = HistoryManager()

  @property
  def properties_dict(self):
    return json.loads(self.properties)

  def get_absolute_oozie_url(self):
    view = 'oozie:list_oozie_workflow'

    if self.oozie_job_id.endswith('C'):
      view = 'oozie:list_oozie_coordinator'
    elif self.oozie_job_id.endswith('B'):
      view = 'oozie:list_oozie_bundle'

    return reverse(view, kwargs={'job_id': self.oozie_job_id})

  def get_workflow(self):
    if self.oozie_job_id.endswith('W'):
      return self.job.get_full_node()

  def get_coordinator(self):
    if self.oozie_job_id.endswith('C'):
      return self.job.get_full_node()

  @classmethod
  def get_workflow_from_config(self, conf_dict):
    try:
      return Workflow.objects.get(id=conf_dict.get(Workflow.HUE_ID))
    except Workflow.DoesNotExist:
      pass

  @classmethod
  def get_coordinator_from_config(self, conf_dict):
    try:
      return Coordinator.objects.get(id=conf_dict.get(Coordinator.HUE_ID))
    except Coordinator.DoesNotExist:
      pass

  @classmethod
  def cross_reference_submission_history(cls, user, oozie_id):
    # Try do get the history
    history = None
    try:
      history = History.objects.get(oozie_job_id=oozie_id)
      if history.job.owner != user:
        history = None
    except History.DoesNotExist:
      pass

    return history


def get_link(oozie_id):
  link = ''

  if 'W@' in oozie_id:
    link = reverse('oozie:list_oozie_workflow_action', kwargs={'action': oozie_id})
  elif oozie_id.endswith('W'):
    link = reverse('oozie:list_oozie_workflow', kwargs={'job_id': oozie_id})
  elif oozie_id.endswith('C'):
    link = reverse('oozie:list_oozie_coordinator', kwargs={'job_id': oozie_id})
  elif 'C@' in oozie_id:
    link = reverse('oozie:list_oozie_coordinator', kwargs={'job_id': oozie_id.split('@')[0]})
  elif 'B@' in oozie_id:
    link = reverse('oozie:list_oozie_bundle', kwargs={'job_id': oozie_id.split('@')[0]})

  return link


def find_parameters(instance, fields=None):
  """Find parameters in the given fields"""
  if fields is None:
    fields = [field.name for field in instance._meta.fields]

  params = []
  for field in fields:
    data = getattr(instance, field)
    if field == 'sla' and not instance.sla_enabled:
      continue
    if isinstance(data, list):
      params.extend(find_json_parameters(data))
    elif isinstance(data, basestring):
      for match in Template.pattern.finditer(data):
        name = match.group('braced')
        if name is not None:
          params.append(name)

  return params

def find_json_parameters(fields):
  # To make smarter
  # Input is list of json dict
  params = []

  for field in fields:
    for data in field.values():
      if isinstance(data, basestring):
        for match in Template.pattern.finditer(data):
          name = match.group('braced')
          if name is not None:
            params.append(name)

  return params


# See http://wiki.apache.org/hadoop/JobConfFile
_STD_PROPERTIES = [
  'mapred.input.dir',
  'mapred.output.dir',
  'mapred.job.name',
  'mapred.job.queue.name',
  'mapred.mapper.class',
  'mapred.reducer.class',
  'mapred.combiner.class',
  'mapred.partitioner.class',
  'mapred.map.tasks',
  'mapred.reduce.tasks',
  'mapred.input.format.class',
  'mapred.output.format.class',
  'mapred.input.key.class',
  'mapred.input.value.class',
  'mapred.output.key.class',
  'mapred.output.value.class',
  'mapred.mapoutput.key.class',
  'mapred.mapoutput.value.class',
  'mapred.combine.buffer.size',
  'mapred.min.split.size',
  'mapred.speculative.execution',
  'mapred.map.tasks.speculative.execution',
  'mapred.reduce.tasks.speculative.execution',
  'mapred.queue.default.acl-administer-jobs',
]

ACTION_TYPES = {
  Mapreduce.node_type: Mapreduce,
  Streaming.node_type: Streaming,
  Java.node_type: Java,
  Pig.node_type: Pig,
  Hive.node_type: Hive,
  Sqoop.node_type: Sqoop,
  Ssh.node_type: Ssh,
  Shell.node_type: Shell,
  DistCp.node_type: DistCp,
  Fs.node_type: Fs,
  Email.node_type: Email,
  SubWorkflow.node_type: SubWorkflow,
  Generic.node_type: Generic,
}

CONTROL_TYPES = {
  Fork.node_type: Fork,
  Join.node_type: Join,
  Decision.node_type: Decision,
  DecisionEnd.node_type: DecisionEnd,
  Start.node_type: Start,
  End.node_type: End,
}

NODE_TYPES = ACTION_TYPES.copy()
NODE_TYPES.update(CONTROL_TYPES)
