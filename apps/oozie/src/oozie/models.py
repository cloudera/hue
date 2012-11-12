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

try:
  import json
except ImportError:
  import simplejson as json
import re
from datetime import datetime,  timedelta
from string import Template
from itertools import chain

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.log.access import access_warn
from desktop.lib import django_mako
from desktop.lib.exceptions import PopupException
from hadoop.fs.exceptions import WebHdfsException

from hadoop.fs.hadoopfs import Hdfs
from liboozie.submittion import Submission

from oozie.management.commands import oozie_setup
from oozie.conf import REMOTE_SAMPLE_DIR, SHARE_JOBS
from timezones import TIMEZONES


LOG = logging.getLogger(__name__)


PATH_MAX = 512
name_validator = RegexValidator(regex='[a-zA-Z_][\-_a-zA-Z0-9]{1,39}',
                                message=_('Please enter a valid value: combination of 2 and 40 letters and digits starting by a letter'))


"""
Permissions:

A Workflow/Coordinator can be accessed/submitted by its owner, a superuser or by anyone if its 'is_shared'
property and SHARE_JOBS are set to True.

A Workflow/Coordinator can be modified only by its owner or a superuser.

Permissions checking happens by adding the decorators.
"""
class JobManager(models.Manager):
  def is_accessible_or_exception(self, request, job_id):
    if job_id is None:
      return
    try:
      job = Job.objects.select_related().get(pk=job_id).get_full_node()
      if job.is_accessible(request.user):
        return job
      else:
        message = _("Permission denied. %(username)s don't have the permissions to access job %(id)s") % \
            {'username': request.user.username, 'id': job.id}
        access_warn(request, message)
        request.error(message)
        raise PopupException(message)

    except Job.DoesNotExist:
      raise PopupException(_('job %(id)s not exist') % {'id': job_id})

  def can_edit_or_exception(self, request, job):
    if job.is_editable(request.user):
      return True
    else:
      raise PopupException(_('Not allowed to modified this job'))


class Job(models.Model):
  """
  Base class for Workflows and Coordinators.

  http://incubator.apache.org/oozie/docs/3.2.0-incubating/docs/index.html
  """
  owner = models.ForeignKey(User, db_index=True, verbose_name=_t('Owner'), help_text=_t('Person who can modify the job.'))
  name = models.CharField(max_length=40, blank=False, validators=[name_validator],
      help_text=_t('Name of the job, which must be unique per user.'), verbose_name=_t('Name'))
  description = models.CharField(max_length=1024, blank=True, verbose_name=_t('Description'),
                                 help_text=_t('What is the purpose of the job.'))
  last_modified = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Last modified'))
  schema_version = models.CharField(max_length=128, verbose_name=_t('Schema version'),
                                    help_text=_t('The version of the XML schema used to talk to Oozie.'))
  deployment_dir = models.CharField(max_length=1024, blank=True, verbose_name=_t('HDFS deployment directory'),
                                    help_text=_t('The path on the HDFS where all the workflows and '
                                                'dependencies must be uploaded.'))
  is_shared = models.BooleanField(default=False, db_index=True, verbose_name=_t('Is shared'),
                                  help_text=_t('Check if you want to have some other users to have access to this job.'))
  parameters = models.TextField(default='[{"name":"oozie.use.system.libpath","value":"true"}]', verbose_name=_t('Oozie parameters'),
                                help_text=_t('Set some parameters used at the submission time (e.g. market=US, oozie.use.system.libpath=true).'))

  objects = JobManager()
  unique_together = ('owner', 'name')

  def save(self):
    super(Job, self).save()

    if not self.deployment_dir:
      default_dir = Hdfs.join(REMOTE_SAMPLE_DIR.get(), '_%s_-oozie-%s' % (self.owner.username, self.id))
      self.deployment_dir = default_dir
      super(Job, self).save()

  def is_deployed(self, fs):
    return self.deployment_dir != '' and fs.exists(self.deployment_dir)

  def __str__(self):
    return '%s - %s' % (self.name, self.owner)

  def get_full_node(self):
    try:
      return self.workflow
    except Workflow.DoesNotExist:
      pass
    try:
      return self.coordinator
    except Coordinator.DoesNotExist:
      pass

  def get_type(self):
    return self.get_full_node().get_type()

  def get_absolute_url(self):
    return self.get_full_node().get_absolute_url()

  def get_parameters(self):
    return json.loads(self.parameters)

  @property
  def status(self):
    if self.is_shared:
      return _('shared')
    else:
      return _('personal')

  def find_all_parameters(self):
    params = self.find_parameters()

    for param in self.get_parameters():
      params[param['name'].strip()] = param['value']

    return  [{'name': name, 'value': value} for name, value in params.iteritems()]

  def is_accessible(self, user):
    return user.is_superuser or self.owner == user or (SHARE_JOBS.get() and self.is_shared)

  def is_editable(self, user):
    """Only owners or admins can modify a job."""
    return user.is_superuser or self.owner == user


class WorkflowManager(models.Manager):
  def new_workflow(self, owner):
    workflow = Workflow(owner=owner, schema_version='uri:oozie:workflow:0.4')

    kill = Kill(name='kill', workflow=workflow, node_type=Kill.node_type)
    end = End(name='end', workflow=workflow, node_type=End.node_type)
    start = Start(name='start', workflow=workflow, node_type=Start.node_type)

    to = Link(parent=start, child=end, name='to')
    related = Link(parent=start, child=end, name='related')

    workflow.start = start
    workflow.end = end

    return workflow

  def initialize(self, workflow, fs):
    Kill.objects.create(name='kill', workflow=workflow, node_type=Kill.node_type)
    end = End.objects.create(name='end', workflow=workflow, node_type=End.node_type)
    start = Start.objects.create(name='start', workflow=workflow, node_type=Start.node_type)

    link = Link(parent=start, child=end, name='to')
    link.save()

    Link.objects.create(parent=start, child=end, name='related')

    workflow.start = start
    workflow.end = end
    workflow.save()

    self.check_workspace(workflow, fs)

  def check_workspace(self, workflow, fs):
    oozie_setup.create_directories(fs)

    if workflow.is_shared:
      perms = 0755
    else:
      perms = 0711

    Submission(workflow.owner, workflow, fs, {})._create_dir(workflow.deployment_dir, perms=perms)

  def destroy(self, workflow, fs):
    Submission(workflow.owner, workflow, fs, {}).remove_deployment_dir()
    workflow.coordinator_set.update(workflow=None) # In Django 1.3 could do ON DELETE set NULL
    workflow.save()
    workflow.delete()


class Workflow(Job):
  """
  http://incubator.apache.org/oozie/docs/3.2.0-incubating/docs/WorkflowFunctionalSpec.html
  """
  is_single = models.BooleanField(default=False)
  start = models.ForeignKey('Start', related_name='start_workflow', blank=True, null=True)
  end  = models.ForeignKey('End', related_name='end_workflow',  blank=True, null=True)
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the configuration element override properties specified in the '
                                          'files specified by any job-xml elements.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('Job configuration properties used by all the actions of the workflow '
                                                 '(e.g. mapred.job.queue.name=production)'))

  objects = WorkflowManager()

  HUE_ID = 'hue-id-w'

  def get_type(self):
    return 'workflow'

  def get_properties(self):
    return json.loads(self.job_properties)

  def add_action(self, action, parent_action_id):
    parent = Node.objects.get(id=parent_action_id).get_full_node()
    error = Kill.objects.get(name='kill', workflow=self)

    if parent.node_type == 'start':
      previous_to = parent.get_child('to')
      to_link = parent.get_link('to')
    elif parent.node_type == 'join':
      previous_to = parent.get_child('to')
      to_link = parent.get_link('to')
    else:
      previous_to = parent.get_child('ok')
      to_link = parent.get_link('ok')

    to_link.child = action
    ok_link = Link(parent=action, child=previous_to, name='ok')
    error_link = Link(parent=action, child=error, name='error')

    to_link.save()
    ok_link.save()
    error_link.save()

  def _add_to_fork(self, action, fork):
    Link.objects.create(parent=fork, child=action, name='start')
    join = fork.get_child_join()

    ok = action.get_link('ok')
    ok.child = join
    ok.save()

  def move_action_up(self, action):
    parent = action.get_parent()
    child = action.get_child('ok')

    # Case add to an already existent fork
    if parent.node_type == 'join':
      # Get fork for parent
      join = parent
      fork = join.get_full_node().get_parent_fork()
      self._add_to_fork(action, fork)
      # Update join
      to = join.get_link('to')
      to.child = child
      to.save()
    # Case leaving a Fork
    elif parent.node_type == 'fork':
      parent_parent = parent.get_parent()
      if parent_parent.node_type == 'start':
        parent_parent_link = parent_parent.get_link('to')
      else:
        parent_parent_link = parent_parent.get_link('ok') # If fork of fork, need to use recursivity

      fork = parent_parent_link.child
      action_below = action.get_child('ok')
      parent_link = action.get_parent_link()

      parent_parent_link.child = action
      parent_parent_link.save()

      if action_below.node_type == 'join':
        parent_link.delete()
      else:
        parent_link.child = action_below
        parent_link.save()

      ok = action.get_link('ok')
      ok.child = fork
      ok.save()

      join = action
    else:
      # Case create a fork
      if parent.node_type == 'fork': # No double forks yet        '
        parent = parent.get_parent()
        parent_parent = parent.get_parent()
        if parent_parent.node_type == 'start':
          parent_parent_link = parent_parent.get_link('to')
        else:
          parent_parent_link = parent_parent.get_link('ok')
      else:
        parent_parent_link = parent.get_parent_link()

      fork = Fork.objects.create(workflow=action.workflow, node_type=Fork.node_type)
      Link.objects.create(parent=fork, child=parent, name='start')
      Link.objects.create(parent=fork, child=action, name='start')

      join = Join.objects.create(workflow=action.workflow, node_type=Join.node_type)
      Link.objects.create(parent=join, child=action.get_child('ok'), name='to')

      Link.objects.create(parent=fork, child=join, name='related')

      parent_parent_link.child = fork
      parent_parent_link.save()

      parent_link = parent.get_link('ok')
      parent_link.child = join
      parent_link.save()
      action_link = action.get_link('ok')
      action_link.child = join
      action_link.save()

    # Case leaving a fork
    if child.node_type == 'join':
      self._remove_fork(child.get_parent_fork())

  def move_action_down(self, action):
    below_action = action.get_child('ok')

    if below_action.node_type == 'join':
      parent_node = action.get_parent()
      self._move_below(action, below_action)
      self._remove_fork(parent_node)
    elif below_action.node_type == 'fork':
      parent_node = action.get_parent()
      self._move_into_fork(action, below_action)
      self._remove_fork(parent_node)
    else:
      self.move_action_up(below_action)

  def delete_action(self, action):
    parent_link = action.get_parent_link()

    if action.get_parent().node_type != 'fork':
      parent_link.child = action.get_child('ok')
      parent_link.save()

    action.delete()
    self._remove_fork(parent_link.parent)

  def _move_below(self, node, below):
    above_link = node.get_parent_link()
    node_link = node.get_child_link('ok')

    if above_link.parent.node_type == 'fork':
      above_link.delete()
    else:
      above_link.child = node.get_child('ok')
      above_link.save()

    below_link = below.get_child_link()
    node_link.child = below_link.child
    below_link.child = node
    below_link.save()

    node_link.save()

  def _move_into_fork(self, node, fork):
    above_link = node.get_parent_link()
    above_link.child = fork
    above_link.save()

    self._add_to_fork(node, fork)

  def _remove_fork(self, node):
    if node.node_type == 'fork':
      fork = node.get_full_node()
      if len(fork.get_children()) <= 1:
        join = fork.get_child_join()

        self._remove_node(fork)
        self._remove_node(join)

  def _remove_node(self, node):
    child = node.get_child()

    for link in node.get_parent_links():
      link.child = child
      link.save()

    node.delete()

  def clone(self, fs, new_owner=None):
    source_deployment_dir = self.deployment_dir # Needed
    nodes = self.node_set.all()
    links = Link.objects.filter(parent__workflow=self)

    copy = self
    copy.pk = None
    copy.id = None
    copy.name += '-copy'
    copy.deployment_dir = ''
    if new_owner is not None:
      copy.owner = new_owner
    copy.save()

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
      msg = _('The copy of the deployment directory failed: %s') % e
      LOG.error(msg)
      raise PopupException(msg)

    return copy


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

    for node in self.node_list:
      if hasattr(node, 'find_parameters'):
        params.update(node.find_parameters())

    return dict([(param, '') for param in list(params)])

  @property
  def actions(self):
    return Action.objects.filter(workflow=self, node_type__in=Action.types)

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
    return reverse('oozie:edit_workflow', kwargs={'workflow': self.id})

  def get_hierarchy(self):
    node = self.start
    return self.get_hierarchy_rec(node) + [[Kill.objects.get(name='kill', workflow=node.workflow)],
                                           [End.objects.get(name='end', workflow=node.workflow)]]

  def get_hierarchy_rec(self, node=None):
    if node is None:
      node = self.start
      if node.id is None:
        return []

    node = node.get_full_node()

    if isinstance(node, End):
      return [] # Not returning the end node
    elif isinstance(node, Fork) and node.has_decisions():
      children = node.get_children('start')
      return [[node] + [[self.get_hierarchy_rec(child) for child in children]]]
    elif isinstance(node, Fork):
      children = node.get_children('start')
      return [[node] + [[self.get_hierarchy_rec(child) for child in children],
                        node.get_child_join()]] + self.get_hierarchy_rec(node.get_child_join().get_child('to'))
    elif isinstance(node, Join):
      return []
    else:
      child = Link.objects.filter(parent=node).exclude(name__in=['related', 'kill'])[0].child
      return [node] + self.get_hierarchy_rec(child)

  def gen_graph(self, forms, template='editor/gen/workflow-graph-editable.xml.mako'):
    index = dict([(form.instance.id, form) for form in forms])
    return django_mako.render_to_string(template, {'nodes': self.get_hierarchy(), 'index': index})

  def gen_status_graph(self, forms, actions):
    template='editor/gen/workflow-graph-status.xml.mako'

    index = dict([(form.instance.id, form) for form in forms])
    actions_index = dict([(action.name, action) for action in actions])

    return django_mako.render_to_string(template, {'nodes': self.get_hierarchy(), 'index': index, 'actions': actions_index})

  def to_xml(self):
    tmpl = 'editor/gen/workflow.xml.mako'
    return re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {'workflow': self}))


class Link(models.Model):
  # Links to exclude when using get_children_link(), get_parent_links() in the API
  META_LINKS = ('related', 'default')

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

  name = models.CharField(max_length=40, validators=[name_validator], verbose_name=_t('Name'),
                          help_text=_t('Name of the action, it must be unique by workflow.'))
  description = models.CharField(max_length=1024, blank=True, default='', verbose_name=_t('Description'),
                                 help_text=_t('What is the purpose of this action.'))
  node_type = models.CharField(max_length=64, blank=False, verbose_name=_t('Type'),
                               help_text=_t('The type of action (e.g. MapReduce, Pig...)'))
  workflow = models.ForeignKey(Workflow)
  children = models.ManyToManyField('self', related_name='parents', symmetrical=False, through=Link)

  unique_together = ('workflow', 'name')

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
    elif self.node_type == Streaming.node_type:
      node = self.streaming
    elif self.node_type == Java.node_type:
      node = self.java
    elif self.node_type == Start.node_type:
      node = self.start
    elif self.node_type == End.node_type:
      node = self.end
    elif self.node_type == Kill.node_type:
      node = self.kill
    elif self.node_type == Fork.node_type:
      node = self.fork
    elif self.node_type == Fork.ACTION_DECISION_TYPE:
      node = self.fork
    elif self.node_type == Join.node_type:
      node = self.join
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

  def to_xml(self):
    node = self.get_full_node()

    data = {
      'node': node,
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
    return self.get_link(name).child.get_full_node()

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

  def get_template_name(self):
    return 'editor/gen/workflow-%s.xml.mako' % self.node_type

  def is_visible(self):
    return True

  def clone(self):
    copy = self
    copy.pk = None
    copy.id = None
    copy.name += '-copy'
    copy.save()
    return copy

  def is_editable(self):
    return False

  def can_move(self):
    return True

  def can_move_up(self):
    parents = self.get_parents()
    for parent in parents:
      if parent.node_type == 'start':
        return False
    return parents and self.can_move()

  def can_move_down(self):
    children = self.get_children()
    for child in children:
      if child.node_type == 'end':
        return False
    return children and self.can_move()


class Action(Node):
  """
  http://incubator.apache.org/oozie/docs/3.2.0-incubating/docs/WorkflowFunctionalSpec.html#a3.2_Workflow_Action_Nodes
  """
  types = ()

  class Meta:
    # Cloning does not work anymore if not abstract
    abstract = True

  def is_editable(self):
    return True

  def get_edit_link(self):
    return reverse('oozie:edit_action', kwargs={'action': self.id})

# The fields with '[]' as default value are JSON dictionaries
# When adding a new action, also update
#  - Action.types below
#  - Node.get_full_node()
#  - forms.py _node_type_TO_FORM_CLS

class Mapreduce(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'jar_path', 'prepares')
  node_type = 'mapreduce'

  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production)'))
  jar_path = models.CharField(max_length=PATH_MAX, verbose_name=_t('Jar name'),
                              help_text=_t('Name or path to the %(program)s jar file on HDFS. e.g. examples.jar') % {'program': 'MapReduce'})
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the configuration element override properties specified in the '
                                          'files specified by any job-xml elements.'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)

  def get_prepares(self):
    return json.loads(self.prepares)


class Streaming(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'mapper', 'reducer')
  node_type = "streaming"

  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production'))
  mapper = models.CharField(max_length=PATH_MAX, blank=False, verbose_name=_t('Mapper'),
                            help_text=_t('The mapper element is used to specify the executable/script to be used as mapper.'))
  reducer = models.CharField(max_length=PATH_MAX, blank=False, verbose_name=_t('Reducer'),
                             help_text=_t('The reducer element is used to specify the executable/script to be used as reducer.'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)


class Java(Action):
  PARAM_FIELDS = ('files', 'archives', 'jar_path', 'main_class', 'args',
                  'java_opts', 'job_properties', 'prepares')
  node_type = "java"

  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  jar_path = models.CharField(max_length=PATH_MAX, blank=False, verbose_name=_t('Jar name'),
                              help_text=_t('Name or path to the %(program)s jar file on HDFS. e.g. examples.jar') % {'program': 'Java'})
  main_class = models.CharField(max_length=256, blank=False, verbose_name=_t('Main class'),
                                help_text=_t('Full name of the Java class. e.g. org.apache.hadoop.examples.Grep'))
  args = models.CharField(max_length=4096, blank=True, verbose_name=_t('Arguments'),
                          help_text=_t('Arguments of the main method. The value of each arg element is considered a single argument '
                                       'and they are passed to the main method in the same order.'))
  java_opts = models.CharField(max_length=256, blank=True, verbose_name=_t('Java options'),
                               help_text=_t('Command line parameters which are to be used to start the JVM that will execute '
                                            'the Java application. Using this element is equivalent to use the mapred.child.java.opts '
                                            'configuration property'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the configuration element override properties specified in the '
                                          'files specified by any job-xml elements.'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)

  def get_prepares(self):
    return json.loads(self.prepares)


class Pig(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'params', 'prepares')
  node_type = 'pig'

  script_path = models.CharField(max_length=256, blank=False, verbose_name=_t('Script name'),
                                 help_text=_t('Script name or path to the Pig script. e.g. my_script.pig'))
  params = models.TextField(default="[]", verbose_name=_t('Parameters'),
                            help_text=_t('The Pig parameters of the script. e.g. "-param", "INPUT=${inputDir}"'))
  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the configuration element override properties specified in the '
                                          'files specified by any job-xml elements.'))

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
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'params', 'prepares')
  node_type = 'hive'

  script_path = models.CharField(max_length=256, blank=False, verbose_name=_t('Script name'),
                                 help_text=_t('Script name or path to the %(type)s script. e.g. my_script.sql') % {'type': node_type.title()})
  params = models.TextField(default="[]", verbose_name=_t('Parameters'),
                            help_text=_t('The %(type)s parameters of the script. e.g. "-param", "INPUT=${inputDir}"')  % {'type': node_type.title()})
  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[{"name":"oozie.hive.defaults","value":"hive-default.xml"}]',
                                    verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the configuration element override properties specified in the '
                                          'files specified by any job-xml elements.'))

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
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'params', 'prepares')
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
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the configuration element override properties specified in the '
                                          'files specified by any job-xml elements.'))

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
  PARAM_FIELDS = ('user', 'host', 'command', 'params')
  node_type = 'ssh'

  user = models.CharField(max_length=64, verbose_name=_t('User'),
                          help_text=_t('User executing the shell command.'))
  host = models.CharField(max_length=256, verbose_name=_t('Host'),
                         help_text=_t('Where the shell will be executed.'))
  command = models.CharField(max_length=256, verbose_name=_t('%(type)s command') % {'type': node_type.title()},
                             help_text=_t('The command that will be executed.'))
  params = models.TextField(default="[]", verbose_name=_t('Arguments'),
                            help_text=_t('The arguments of the %(type)s command')  % {'type': node_type.title()})
  capture_output = models.BooleanField(default=False, verbose_name=_t('Capture output'),
                              help_text=_t('Capture output of the STDOUT of the %(program)s command execution. The %(program)s '
                                           'command output must be in Java Properties file format and it must not exceed 2KB. '
                                           'From within the workflow definition, the output of an %(program)s action node is accessible '
                                           'via the String action:output(String node, String key) function') % {'program': node_type.title()})

  def get_params(self):
    return json.loads(self.params)


class Shell(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'params', 'prepares')
  node_type = 'shell'

  command = models.CharField(max_length=256, blank=False, verbose_name=_t('%(type)s command') % {'type': node_type.title()},
                             help_text=_t('The path of the Shell command to execute'))
  params = models.TextField(default="[]", verbose_name=_t('Arguments'),
                            help_text=_t('The arguments of Shell command can then be specified using one or more argument element.'))
  files = models.TextField(default="[]", verbose_name=_t('Files'),
      help_text=_t('List of names or paths of files to be added to the distributed cache and the task running directory.'))
  archives = models.TextField(default="[]", verbose_name=_t('Archives'),
      help_text=_t('List of names or paths of the archives to be added to the distributed cache.'))
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the configuration element override properties specified in the '
                                          'files specified by any job-xml elements.'))
  capture_output = models.BooleanField(default=False, verbose_name=_t('Capture output'),
                              help_text=_t('Capture output of the STDOUT of the %(program)s command execution. The %(program)s '
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
  PARAM_FIELDS = ('job_properties', 'params', 'prepares')
  node_type = 'distcp'

  params = models.TextField(default="[]", verbose_name=_t('Arguments'),
                            help_text=_t('The arguments of the %(type)s command. Put options first then source paths then destination path.')
                                        % {'type': node_type.title()})
  job_properties = models.TextField(default='[]', verbose_name=_t('Hadoop job properties'),
                                    help_text=_t('For the job configuration (e.g. mapred.job.queue.name=production'))
  prepares = models.TextField(default="[]", verbose_name=_t('Prepares'),
                              help_text=_t('List of absolute paths to delete then to create before starting the application. '
                                           'This should be used exclusively for directory cleanup'))
  job_xml = models.CharField(max_length=PATH_MAX, default='', blank=True, verbose_name=_t('Job XML'),
                             help_text=_t('Refer to a Hadoop JobConf job.xml file bundled in the workflow deployment directory. '
                                          'Properties specified in the configuration element override properties specified in the '
                                          'files specified by any job-xml elements.'))


  def get_properties(self):
    return json.loads(self.job_properties)

  def get_params(self):
    return json.loads(self.params)

  def get_prepares(self):
    return json.loads(self.prepares)


Action.types = (Mapreduce.node_type, Streaming.node_type, Java.node_type, Pig.node_type, Hive.node_type, Sqoop.node_type, Ssh.node_type, Shell.node_type,
                DistCp.node_type)


class ControlFlow(Node):
  """
  http://incubator.apache.org/oozie/docs/3.2.0-incubating/docs/WorkflowFunctionalSpec.html#a3.1_Control_Flow_Nodes
  """
  class Meta:
    abstract = True

  def get_xml(self):
    return django_mako.render_to_string(self.get_template_name(), {})

  def is_visible(self):
    return False

  def can_move(self):
    return False

  def get_edit_link(self):
    return ''


# Could not make this abstract
class Start(ControlFlow):
  node_type = 'start'


class End(ControlFlow):
  node_type = 'end'


class Kill(ControlFlow):
  node_type = 'kill'

  message = models.CharField(max_length=256, blank=False, default='Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]')


class Fork(ControlFlow):
  """
  A Fork can be converted into a Decision node.
  """
  node_type = 'fork'
  ACTION_DECISION_TYPE = 'decision'

  def has_decisions(self):
    return self.get_children_links().exclude(comment='').exists()

  def is_visible(self):
    return True

  def get_child_join(self):
    return Link.objects.get(parent=self, name='related').child.get_full_node()

  def is_editable(self):
    return False

  def get_edit_link(self):
    return reverse('oozie:edit_workflow_fork', kwargs={'action': self.id})

  def convert_to_decision(self):
    self.remove_join()
    self.node_type = Fork.ACTION_DECISION_TYPE
    self.save()

  def update_description(self):
    self.description = ', '.join(self.get_children_links().values_list('comment', flat=True))
    self.save()

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



FREQUENCY_UNITS = (('minutes', _('Minutes')),
                   ('hours', _('Hours')),
                   ('days', _('Days')),
                   ('months', _('Months')))
FREQUENCY_NUMBERS = [(i, i) for i in xrange(1, 61)]
DATASET_FREQUENCY = ['MINUTE', 'HOUR', 'DAY', 'MONTH', 'YEAR']


class Coordinator(Job):
  """
  http://incubator.apache.org/oozie/docs/3.2.0-incubating/docs/CoordinatorFunctionalSpec.html
  """
  frequency_number = models.SmallIntegerField(default=1, choices=FREQUENCY_NUMBERS, verbose_name=_t('Frequency number'),
                                              help_text=_t('It represents the number of units of the rate at which '
                                                           'data is periodically created.'))
  frequency_unit = models.CharField(max_length=20, choices=FREQUENCY_UNITS, default='days', verbose_name=_t('Frequency unit'),
                                    help_text=_t('It represents the unit of the rate at which data is periodically created.'))
  timezone = models.CharField(max_length=24, choices=TIMEZONES, default='America/Los_Angeles', verbose_name=_t('Timezone'),
                              help_text=_t('The timezone of the Coordinator.'))
  start = models.DateTimeField(default=datetime.today(), verbose_name=_t('Start'),
                               help_text=_t('When we need to start the first workflow.'))
  end = models.DateTimeField(default=datetime.today() + timedelta(days=3), verbose_name=_t('End'),
                             help_text=_t('When we need to start the last workflow.'))
  workflow = models.ForeignKey(Workflow, null=True, verbose_name=_t('Workflow'),
                               help_text=_t('The corresponding workflow we want to schedule repeatedly.'))
  timeout = models.SmallIntegerField(null=True, blank=True, verbose_name=_t('Timeout'),
                                     help_text=_t('Timeout for its coordinator actions, in minutes. This is how long '
                                                  'the coordinator action will be in '
                                                  'WAITING or READY status before giving up on its execution.'))
  concurrency = models.PositiveSmallIntegerField(null=True, blank=True, choices=FREQUENCY_NUMBERS, verbose_name=_t('Concurrency'),
                                 help_text=_t('Concurrency for its coordinator actions, this is, how many coordinator actions are '
                                              'allowed to run concurrently ( RUNNING status) before the coordinator engine '
                                              'starts throttling them.'))
  execution = models.CharField(max_length=10, null=True, blank=True, verbose_name=_t('Execution'),
                               choices=(('FIFO', _t('FIFO (oldest first) default')),
                                        ('LIFO', _t('LIFO (newest first)')),
                                        ('LAST_ONLY', _t('LAST_ONLY (discards all older materializations)'))),
                                 help_text=_t('Execution strategy of its coordinator actions when there is backlog of coordinator '
                                              'actions in the coordinator engine. The different execution strategies are \'oldest first\', '
                                              '\'newest first\' and \'last one only\'. A backlog normally happens because of delayed '
                                              'input data, concurrency control or because manual re-runs of coordinator jobs.'))
  throttle = models.PositiveSmallIntegerField(null=True, blank=True, choices=FREQUENCY_NUMBERS, verbose_name=_t('Throttle'),
                                 help_text=_t('The materialization or creation throttle value for its coordinator actions, this is, '
                                              'how many maximum coordinator actions are allowed to be in WAITING state concurrently.'))
  HUE_ID = 'hue-id-c'

  def get_type(self):
    return 'coordinator'

  def to_xml(self):
    tmpl = "editor/gen/coordinator.xml.mako"
    return re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {'coord': self}))

  def clone(self, new_owner=None):
    datasets = Dataset.objects.filter(coordinator=self)
    data_inputs = DataInput.objects.filter(coordinator=self)
    data_outputs = DataOutput.objects.filter(coordinator=self)

    copy = self
    copy.pk = None
    copy.id = None
    copy.name += '-copy'
    copy.deployment_dir = ''
    if new_owner is not None:
      copy.owner = new_owner
    copy.save()

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
    params = self.workflow.find_parameters()

    for dataset in self.dataset_set.all():
      for param in find_parameters(dataset, ['uri']):
        if param not in set(DATASET_FREQUENCY):
          params[param] = ''

    for ds in self.datainput_set.all():
      params.pop(ds.name, None)

    for ds in self.dataoutput_set.all():
      params.pop(ds.name, None)

    return params


def utc_datetime_format(utc_time):
  return utc_time.strftime("%Y-%m-%dT%H:%MZ")


class DatasetManager(models.Manager):
  def is_accessible_or_exception(self, request, dataset_id):
    if dataset_id is None:
      return
    try:
      dataset = Dataset.objects.get(pk=dataset_id)
      if dataset.coordinator.is_accessible(request.user):
        return dataset
      else:
        message = _("Permission denied. %(username)s don't have the permissions to access dataset %(id)s") % \
            {'username': request.user.username, 'id': dataset.id}
        access_warn(request, message)
        request.error(message)
        raise PopupException(message)

    except Dataset.DoesNotExist:
      raise PopupException(_('dataset %(id)s not exist') % {'id': dataset_id})


class Dataset(models.Model):
  name = models.CharField(max_length=40, validators=[name_validator], verbose_name=_t('Name'),
                          help_text=_t('The name of the dataset.)'))
  description = models.CharField(max_length=1024, blank=True, default='', verbose_name=_t('Description'),
                                 help_text=_t('More details about the dataset.'))
  start = models.DateTimeField(default=datetime.today(), verbose_name=_t('Start'),
                               help_text=_t(' The UTC datetime of the initial instance of the dataset. The initial-instance also provides '
                                            'the baseline datetime to compute instances of the dataset using multiples of the frequency.'))
  frequency_number = models.SmallIntegerField(default=1, choices=FREQUENCY_NUMBERS, verbose_name=_t('Frequency number'),
                                              help_text=_t('It represents the number of units of the rate at which '
                                                           'data is periodically created.'))
  frequency_unit = models.CharField(max_length=20, choices=FREQUENCY_UNITS, default='days', verbose_name=_t('Frequency unit'),
                                    help_text=_t('It represents the unit of the rate at which data is periodically created.'))
  uri = models.CharField(max_length=1024, default='/data/${YEAR}${MONTH}${DAY}', verbose_name=_t('URI'),
                         help_text=_t('The URI template that identifies the dataset and can be resolved into concrete URIs to identify a particular '
                                      'dataset instance. The URI consist of constants (e.g. ${YEAR}/${MONTH}) and '
                                      'configuration properties (e.g. Ex: ${YEAR}/${MONTH})'))
  timezone = models.CharField(max_length=24, choices=TIMEZONES, default='America/Los_Angeles', verbose_name=_t('Timezone'),
                              help_text=_t('The timezone of the dataset.'))
  done_flag = models.CharField(max_length=64, blank=True, default='', verbose_name=_t('Done flag'),
                               help_text=_t(' The done file for the data set. If done-flag is not specified, then Oozie '
                                            'configures Hadoop to create a _SUCCESS file in the output directory. If the done '
                                            'flag is set to empty, then Coordinator looks for the existence of the directory itself.'))
  coordinator = models.ForeignKey(Coordinator, verbose_name=_t('Coordinator'),
                                  help_text=_t('The coordinator associated with this data.'))

  objects = DatasetManager()
  unique_together = ('coordinator', 'name')

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


class DataInput(models.Model):
  name = models.CharField(max_length=40, validators=[name_validator], verbose_name=_t('Name of an input variable in the workflow'),
                          help_text=_t('The name of the variable of the workflow to automatically filled up.'))
  dataset = models.OneToOneField(Dataset, verbose_name=_t('Pick the dataset representing format of the data input'),
                                 help_text=_t('The pattern of the input data we want to process.'))
  coordinator = models.ForeignKey(Coordinator)

  unique_together = ('coordinator', 'name')


class DataOutput(models.Model):
  name = models.CharField(max_length=40, validators=[name_validator], verbose_name=_t('Name of an output variable in the workflow'),
                          help_text=_t('The name of the variable of the workflow to automatically filled up.'))
  dataset = models.OneToOneField(Dataset, verbose_name=_t('Pick the dataset representing the format of the data output'),
                                 help_text=_t('The pattern of the output data we want to generate.'))
  coordinator = models.ForeignKey(Coordinator)

  unique_together = ('coordinator', 'name')


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

    return reverse(view, kwargs={'job_id': self.oozie_job_id})

  def get_workflow(self):
    if self.oozie_job_id.endswith('W'):
      return self.job

  def get_coordinator(self):
    if self.oozie_job_id.endswith('C'):
      return self.job

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
  def cross_reference_submission_history(cls, user, oozie_id, coordinator_job_id):
    # Try do get the history
    history = None
    try:
      history = History.objects.get(oozie_job_id=oozie_id)
      if history.job.owner != user:
        history = None
    except History.DoesNotExist:
      pass

    return history

def find_parameters(instance, fields=None):
  """Find parameters in the given fields"""
  if fields is None:
    fields = [field.name for field in instance._meta.fields]

  params = []
  for field in fields:
    data = getattr(instance, field)
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

_STD_PROPERTIES_JSON = json.dumps(_STD_PROPERTIES)

