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

from django.db import models
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.lib import django_mako

from hadoop.fs.hadoopfs import Hdfs
from liboozie.submittion import Submission

from oozie.conf import REMOTE_DATA_DIR
from timezones import TIMEZONES


LOG = logging.getLogger(__name__)


PATH_MAX = 512
name_validator = RegexValidator(regex='[a-zA-Z_][\-_a-zA-Z0-9]{1,39}',
                                message=_('Please enter a valid value: 40 alphanum chars starting by an alpha'))


class Job(models.Model):
  """
  Base class for Workflows and Coordinators.

  http://incubator.apache.org/oozie/docs/3.2.0-incubating/docs/index.html
  """
  owner = models.ForeignKey(User, db_index=True)
  name = models.CharField(max_length=40, blank=False, validators=[name_validator],
      help_text=_('Name of the design, which must be unique per user'))
  description = models.CharField(max_length=1024, blank=True)
  last_modified = models.DateTimeField(auto_now=True, db_index=True)
  schema_version = models.CharField(max_length=128, blank=True, default='')
  deployment_dir = models.CharField(max_length=1024, blank=True, verbose_name=_('HDFS deployment directory'))
  is_shared = models.BooleanField(default=False, db_index=True)

  unique_together = ('owner', 'name')

  def save(self):
    super(Job, self).save()

    if not self.deployment_dir:
      default_dir = Hdfs.join(REMOTE_DATA_DIR.get(), '_%s_-oozie-%s' % (self.owner.username, self.id))
      self.deployment_dir = default_dir
      super(Job, self).save()

  def is_deployed(self, fs):
    return self.deployment_dir != '' and fs.exists(self.deployment_dir)

  def __unicode__(self):
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

  @property
  def status(self):
    if self.is_shared:
      return 'shared'
    else:
      return 'personal'

  def find_parameters(self, fields=None):
    return find_parameters(self, fields)


class WorkflowManager(models.Manager):
  def new_workflow(self, owner):
    workflow = Workflow(owner=owner)

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

    WorkflowManager.create_data_dir(fs)
    Submission(workflow, fs, {})._create_deployment_dir()

    return workflow

  @classmethod
  def create_data_dir(cls, fs):
    # If needed, create the remote home and data directories
    remote_data_dir = REMOTE_DATA_DIR.get()
    user = fs.user

    try:
      fs.setuser(fs.DEFAULT_USER)
      if not fs.exists(remote_data_dir):
        remote_home_dir = Hdfs.join('/user', fs.user)
        if remote_data_dir.startswith(remote_home_dir):
          # Home is 755
          fs.create_home_dir(remote_home_dir)
        # Shared by all the users
        fs.mkdir(remote_data_dir, 01777)
    finally:
      fs.setuser(user)

    return remote_data_dir


class Workflow(Job):
  """
  http://incubator.apache.org/oozie/docs/3.2.0-incubating/docs/WorkflowFunctionalSpec.html
  """
  is_single = models.BooleanField(default=False)
  start = models.ForeignKey('Start', related_name='start_workflow', blank=True, null=True)
  end  = models.ForeignKey('End', related_name='end_workflow',  blank=True, null=True)

  objects = WorkflowManager()

  def get_type(self):
    return 'workflow'

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

  def clone(self, new_owner=None):
    nodes = self.node_set.all()
    links = Link.objects.filter(parent__workflow=self)

    copy = self
    copy.pk = None
    copy.id = None
    copy.name += '-copy'
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

    return copy

  def find_parameters(self):
    params = set()

    for node in self.node_list:
      if hasattr(node, 'find_parameters'):
        params.update(node.find_parameters())

    return list(params)

  @property
  def get_actions(self):
    return Action.objects.filter(workflow=self, node_type__in=Action.types)

  @property
  def node_list(self):
    nodes = []

    for row in self.get_hierarchy():
      if type(row) == list:
        for node in row:
          nodes.append(node)
      else:
        nodes.append(row)

    return nodes

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

  def gen_graph(self, forms, template="editor/gen/workflow-graph-editable.xml.mako"):
    index = dict([(form.instance.id, form) for form in forms])
    return django_mako.render_to_string(template, {'nodes': self.get_hierarchy(), 'index': index})

  def gen_status_graph(self, forms, actions):
    template="editor/gen/workflow-graph-status.xml.mako"

    index = dict([(form.instance.id, form) for form in forms])
    actions_index = dict([(action.name, action) for action in actions])

    return django_mako.render_to_string(template, {'nodes': self.get_hierarchy(), 'index': index, 'actions': actions_index})

  def to_xml(self):
    tmpl = "editor/gen/workflow.xml.mako"
    return re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {'workflow': self}))


class Link(models.Model):
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

  name = models.CharField(max_length=40, validators=[name_validator])
  description = models.CharField(max_length=1024, blank=True, default='')
  node_type = models.CharField(max_length=64, blank=False)
  workflow = models.ForeignKey(Workflow)
  children = models.ManyToManyField('self', related_name='parents', symmetrical=False, through=Link)

  unique_together = ('workflow', 'name')

  def get_full_node(self):
    if self.node_type == Mapreduce.node_type:
      node = self.mapreduce
    elif self.node_type == Pig.node_type:
      node = self.pig
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
      return Link.objects.exclude(name='related').get(parent=self)
    else:
      return Link.objects.exclude(name='related').get(parent=self, name=name)

  def get_child_link(self, name=None):
    return self.get_link(name)

  def get_child(self, name=None):
    return self.get_link(name).child.get_full_node()

  def get_children(self, name=None):
    if name is not None:
      return [link.child for link in Link.objects.exclude(name='related').filter(parent=self, name=name)]
    else:
      return [link.child for link in Link.objects.exclude(name='related').filter(parent=self)]

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
    return Link.objects.filter(child=self)

  def get_children_links(self, name=None):
    if name is None:
      return Link.objects.exclude(name='related').filter(parent=self)
    else:
      return Link.objects.exclude(name='related').filter(parent=self, name=name)

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

  def can_edit(self):
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

  def can_edit(self):
    return True

  def get_edit_link(self):
    return reverse('oozie:edit_action', kwargs={'action': self.id})


# When adding a new action, also update
#  - Action.types below
#  - Node.get_full_node()

class Mapreduce(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'jar_path')
  node_type = 'mapreduce'

  files = models.CharField(max_length=PATH_MAX, default="[]",
      help_text=_t('List of paths to files to be added to the distributed cache'))
  archives = models.CharField(max_length=PATH_MAX, default="[]",
      help_text=_t('List of paths to archives to be added to the distributed cache'))
  job_properties = models.TextField(default='[]', # JSON dict
                                    help_text=_t('For the job configuration (e.g. mapred.mapper.class)'))
  jar_path = models.CharField(max_length=PATH_MAX, help_text=_t('Path to jar files on HDFS'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)


class Streaming(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'mapper', 'reducer')
  node_type = "streaming"

  files = models.CharField(max_length=PATH_MAX, default="[]")
  archives = models.CharField(max_length=PATH_MAX, default="[]")
  job_properties = models.TextField(default='[{"name":"oozie.use.system.libpath","value":"true"}]', # JSON dict
                                    help_text=_t('For the job configuration (e.g. mapred.mapper.class)'))
  mapper = models.CharField(max_length=PATH_MAX, blank=False)
  reducer = models.CharField(max_length=PATH_MAX, blank=False)

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)


class Java(Action):
  PARAM_FIELDS = ('files', 'archives', 'jar_path', 'main_class', 'args',
                  'java_opts', 'job_properties')
  node_type = "java"

  files = models.CharField(max_length=PATH_MAX, default="[]",
      help_text=_t('List of paths to files to be added to the distributed cache'))
  archives = models.CharField(max_length=PATH_MAX, default="[]",
      help_text=_t('List of paths to archives to be added to the distributed cache'))
  jar_path = models.CharField(max_length=PATH_MAX, blank=False)
  main_class = models.CharField(max_length=256, blank=False)
  args = models.CharField(max_length=4096, blank=True)
  java_opts = models.CharField(max_length=256, blank=True)
  job_properties = models.TextField(default='[]', # JSON dict
                                    help_text=_t('For the job configuration (e.g. mapred.mapper.class)'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)


class Pig(Action):
  PARAM_FIELDS = ('files', 'archives', 'job_properties', 'params')
  node_type = 'pig'

  script_path = models.CharField(max_length=256, blank=False, help_text=_t('Local path'))
  params = models.TextField(default="[]")

  files = models.CharField(max_length=PATH_MAX, default="[]",
      help_text=_t('List of paths to files to be added to the distributed cache'))
  archives = models.CharField(max_length=PATH_MAX, default="[]",
      help_text=_t('List of paths to archives to be added to the distributed cache'))
  job_properties = models.TextField(default='[{"name":"oozie.use.system.libpath","value":"true"}]', # JSON dict
                                    help_text=_t('For the job configuration (e.g. mapred.mapper.class)'))

  def get_properties(self):
    return json.loads(self.job_properties)

  def get_files(self):
    return json.loads(self.files)

  def get_archives(self):
    return json.loads(self.archives)

  def get_params(self):
    return json.loads(self.params)


Action.types = (Mapreduce.node_type, Streaming.node_type, Java.node_type, Pig.node_type)


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
    return self.get_children_links().exclude(name='related').exclude(comment='').exists()

  def is_visible(self):
    return True

  def get_child_join(self):
    return Link.objects.get(parent=self, name='related').child.get_full_node()

  def can_edit(self):
    return True

  def get_edit_link(self):
    return reverse('oozie:edit_workflow_fork', kwargs={'action': self.id})

  def convert_to_decision(self):
    self.remove_join()
    self.node_type = Fork.ACTION_DECISION_TYPE
    self.save()

  def update_description(self):
    self.description = ', '.join(self.get_children_links().exclude(name='related').values_list('comment', flat=True))
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
    return [link.parent for link in self.get_parent_links().exclude(name='related')]



FREQUENCY_UNITS = (('minutes', 'Minutes'),
                   ('hours', 'Hours'),
                   ('days', 'Days'),
                   ('months', 'Months'))
FREQUENCY_NUMBERS = [(i, i) for i in xrange(1, 61)]


class Coordinator(Job):
  """
  http://incubator.apache.org/oozie/docs/3.2.0-incubating/docs/CoordinatorFunctionalSpec.html
  """
  frequency_number = models.SmallIntegerField(default=1, choices=FREQUENCY_NUMBERS)
  frequency_unit = models.CharField(max_length=20, choices=FREQUENCY_UNITS, default='days')
  timezone = models.CharField(max_length=24, choices=TIMEZONES, default='America/Los_Angeles')
  start = models.DateTimeField(default=datetime(2012, 07, 01, 0, 0))
  end = models.DateTimeField(default=datetime(2012, 07, 01, 0, 0) + timedelta(days=3))
  workflow = models.ForeignKey(Workflow, null=True)

  def get_type(self):
    return 'coordinator'

  def to_xml(self):
    tmpl = "editor/gen/coordinator.xml.mako"
    return re.sub(re.compile('\s*\n+', re.MULTILINE), '\n', django_mako.render_to_string(tmpl, {'coord': self}))

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
    params = set()

    for dataset in self.dataset_set.all():
      params.update(set(find_parameters(dataset, ['uri'])))

    return list(params - set(['MINUTE', 'DAY', 'MONTH', 'YEAR']))


def utc_date_format(utc_time):
  return utc_time.strftime("%Y-%m-%d")

def utc_datetime_format(utc_time):
  return utc_time.strftime("%Y-%m-%dT%H:%MZ")


class Dataset(models.Model):
  name = models.CharField(max_length=40, validators=[name_validator])
  description = models.CharField(max_length=1024, blank=True, default='')
  start = models.DateTimeField(default=utc_date_format(datetime.today()))
  frequency_number = models.SmallIntegerField(default=1, choices=FREQUENCY_NUMBERS)
  frequency_unit = models.CharField(max_length=20, choices=FREQUENCY_UNITS, default='days')
  uri = models.CharField(max_length=1024, default='/data/${YEAR}${MONTH}${DAY}')
  timezone = models.CharField(max_length=24, choices=TIMEZONES, default='America/Los_Angeles')
  done_flag = models.CharField(max_length=64, blank=True, default='')
  coordinator = models.ForeignKey(Coordinator)

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
  name = models.CharField(max_length=40, validators=[name_validator], verbose_name=_('Name of an input variable in the workflow'))
  dataset = models.OneToOneField(Dataset, verbose_name=_('Pick the dataset representing format of the data input'))
  coordinator = models.ForeignKey(Coordinator)

  unique_together = ('coordinator', 'name')


class DataOutput(models.Model):
  name = models.CharField(max_length=40, validators=[name_validator], verbose_name=_('Name of an output variable in the workflow'))
  dataset = models.OneToOneField(Dataset, verbose_name=_('Pick the dataset representing the format of the data output'))
  coordinator = models.ForeignKey(Coordinator)

  unique_together = ('coordinator', 'name')


class HistoryManager(models.Manager):
  def create_from_submission(self, submission):
    History.objects.create(submitter=submission.job.owner,
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


def find_parameters(instance, fields=None):
  """Find parameters in the given fields"""
  if fields is None:
    fields = [field.name for field in instance._meta.fields]

  params = []
  for field in fields:
    data = getattr(instance, field)
    if isinstance(data, basestring):
      for match in Template.pattern.finditer(data):
        name = match.group('named') or match.group('braced')
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

