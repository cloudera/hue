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

"""
The application configuration framework. The user of the framework uses
* Config
  - These correspond to an individual key-value pair in the conf file. For example,
        [ app_name ]
        my_property = "foo"
    is represented by this Config variable:
        MY_PROPERTY = Config(key='my_property', default='my_default', type=str, help='blah')
        val = MY_PROPERTY.get()

* ConfigSection
  - A ConfigSection corresponds to a section in the conf file. For example, in
        [ app_name ]
        [[ section_a ]]
        a_property = "bar"
    both "app_name" and "section_a" are ConfigSection's. A section in which all children
    are known beforehand can be represented by:
        SECTION_A = ConfigSection(
                          key='section_a',
                          help='blah',
                          members=dict(a_prop=Config(key='a_property', required=True)))
        a_val = SECTION_A.a_prop.get()

* UnspecifiedConfigSection
  - An UnspecifiedConfigSection corresponds to a section that has the same type of children.
    But its exact members are not know beforehand. For example,
        [[ filesystems ]]
        [[[ cluster_1 ]]]
        namenode_host = localhost
        # User may define more:
        # [[[ cluster_2 ]]]
        # namenode_host = 10.0.0.1
    would be represented by:
        FS = UnspecifiedConfigSection(
                          key='filesystems',
                          each=ConfigSection(members=dict(
                              nn_host=Config(key='namenode_host', required=True))
        all_clusters = FS.keys()
        for x in all_clusters:
            val = FS['x'].nn_host.get()

You _MUST_ define all Config, ConfigSection and UnspecifiedConfigSection objects in your
application's conf.py. During startup, Desktop binds configuration files to your config
variables.
"""

# The Config object unfortunately has a kwarg called "type", and everybody is
# using it. So instead of breaking compatibility, we make a "pytype" alias.
pytype = type

from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

from desktop.lib.paths import get_desktop_root, get_build_dir

from configobj import ConfigObj, ConfigObjError
import json
import logging
import os
import textwrap
import re
import subprocess
import sys

try:
  from collections import OrderedDict
except ImportError:
  from ordereddict import OrderedDict # Python 2.6


# Magical object for use as a "symbol"
_ANONYMOUS = ("_ANONYMOUS")

# Supported thrift transports
SUPPORTED_THRIFT_TRANSPORTS = ('buffered', 'framed')

# a BoundContainer(BoundConfig) object which has all of the application's configs as members
GLOBAL_CONFIG = None

LOG = logging.getLogger(__name__)

__all__ = ["UnspecifiedConfigSection", "ConfigSection", "Config", "load_confs", "coerce_bool", "coerce_csv", "coerce_json_dict"]

class BoundConfig(object):
  def __init__(self, config, bind_to, grab_key=_ANONYMOUS, prefix=''):
    """
    A Config object that has been bound to specific data.

    @param config   The config that is bound - must handle get_value
    @param bind_to  The data it is bound to - must support subscripting
    @param grab_key The key in bind_to in which to expect this configuration
    @param prefix   The prefix in the config tree leading to this configuration
    """
    self.config = config
    self.bind_to = bind_to
    self.grab_key = grab_key

    # The prefix of a config is the path leading to the config, including section and subsections
    # along the way, e.g. hadoop.filesystems.cluster_1.
    #
    # The prefix is recorded in BoundConfig only, because section names can change dynamically for
    # UnspecifiedConfigSection's, which have children with _ANONYMOUS keys. If our config is
    # _ANONYMOUS, this `prefix' includes the prefix plus the actual key name.
    self.prefix = prefix

  def get_fully_qualifying_key(self):
    """Returns the full key name, in the form of section[.subsection[...]].key"""
    res = self.prefix
    if self.config.key is not _ANONYMOUS:
      res += self.prefix and '.' + self.config.key or self.config.key
    return res

  def _get_data_and_presence(self):
    """
    Returns a tuple (data, present).

    'present' is whether the data was found in self.bind_to
    'data' is the data itself, or None whenever present is False
    """
    try:
      if self.grab_key is not _ANONYMOUS:
        present = self.grab_key in self.bind_to
        data = self.bind_to.get(self.grab_key)
      else:
        present = True
        data = self.bind_to
    except AttributeError:
      LOG.exception("Error value of key '%s' in configuration." % self.grab_key)
      data = _("Possible misconfiguration")
      present = True

    return data, present

  def get(self):
    """Get the data, or its default value."""
    data, present = self._get_data_and_presence()
    return self.config.get_value(data, present=present, prefix=self.prefix, coerce_type=True)

  def get_raw(self):
    """Get raw config value. This maybe a non-string or non-iterable object."""
    data, present = self._get_data_and_presence()
    return self.config.get_value(data, present=present, prefix=self.prefix, coerce_type=False)

  def set_for_testing(self, data=None, present=True):
    """
    This temporarily sets this configuration's value to data
    (or, if present=False, to the default value).  This
    returns a lambda which should be executed
    when the testing phase is done.

    Note that self is a new object at every access,
    but self.bind_to is shared, so we can modify that.
    """
    def set_data_presence(data, presence):
      self.bind_to[self.grab_key] = data
      if not presence:
        del self.bind_to[self.grab_key]
    assert self.grab_key is not _ANONYMOUS # TODO(todd) really?
    old_data = self.bind_to.get(self.grab_key)
    old_presence = self.grab_key in self.bind_to

    set_data_presence(data, present)
    return (lambda: set_data_presence(old_data, old_presence))

  def validate(self):
    self.config.validate(self.bind_to)

  def print_help(self, *args, **kwargs):
    self.config.print_help(*args, **kwargs)

  def __repr__(self):
    return repr("%s(config=%s, bind_to=%s, grab_key=%s)" %
                (str(self.__class__),
                 repr(self.config), repr(self.bind_to), repr(self.grab_key)))


class Config(object):
  def __init__(self, key=_ANONYMOUS, default=None, dynamic_default=None,
               required=False, help=None, type=str, private=False):
    """
    Initialize a new Configurable variable.

    @param key      the configuration key (eg "filebrowser.foo")
    @param default  the default value
    @param dynamic_default a lambda to use to calculate the default
    @param required whether this must be set
    @param help     some text to print out for help
    @param type     a callable that coerces a string into the expected type.
                    str is the default. Should raise an exception in the case
                    that it cannot be coerced.
    @param private  if True, does not emit help text
    """
    if not callable(type):
      raise ValueError("%s: The type argument '%s()' is not callable" % (key, type))

    if default is not None and dynamic_default is not None:
      raise ValueError("Cannot specify both dynamic_default and default for key %s" % key)

    if dynamic_default is not None and not dynamic_default.__doc__ and not private:
      raise ValueError("Dynamic default '%s' must have __doc__ defined!" % (key,))

    if pytype(default) in (int, long, float, complex, bool) and \
          not isinstance(type(default), pytype(default)):
      raise ValueError("%s: '%s' does not match that of the default value %r (%s)"
                      % (key, type, default, pytype(default)))

    if type == bool:
      LOG.warn("%s is of type bool. Resetting it as type 'coerce_bool'."
               " Please fix it permanently" % (key,))
      type = coerce_bool

    self.key = key
    self.default_value = default
    self.dynamic_default = dynamic_default
    self.required = required
    self.help = help
    self.type = type
    self.private = private

    # It makes no sense to be required if you have a default,
    # since you'll never throw the "not set" error.
    assert not (self.required and self.default), \
           "Config cannot be required if it has a default."

  def bind(self, conf, prefix):
    """Rather than doing the lookup now and assigning self.value or something,
    this binding creates a new object. This is because, for a given Config
    object, it might need to be bound to different parts of a configuration
    tree.

    For example, if a "host" Config object is under an UnspecifiedConfigSection
    it will be end up applying to each subsection. We therefore bind it
    multiple times, once to each subsection.
    """
    return BoundConfig(config=self, bind_to=conf, grab_key=self.key, prefix=prefix)

  def get_value(self, val, present, prefix=None, coerce_type=True):
    """
    Return the value for this configuration variable from the
    currently loaded configuration.

    @throws KeyError if it is required but not set.
    @throws ValueError if it does not validate correctly.
    """
    if self.required and not present:
      raise KeyError("Configuration key %s not in configuration!" % self.key)
    if present:
      raw_val = val
    else:
      raw_val = self.default

    if coerce_type:
      return self._coerce_type(raw_val, prefix)
    else:
      return raw_val

  def validate(self, source):
    """
    Raise an exception if this configuration value is missing but required,
    or of the incorrect type.
    """
    # Getting the value will raise an exception if it's in bad form.
    val = source.get(self.key, None)
    present = val is not None
    _ = self.get_value(val, present)

  def _coerce_type(self, raw, _):
    """
    Coerces the value in 'raw' to the correct type, based on self.type
    """
    if raw is None:
      return raw
    return self.type(raw)

  def print_help(self, out=sys.stdout, indent=0):
    """
    Print out a help string for this configuration object
    to the specified output stream.

    @param indent   the number of spaces to indent all text by
    """
    if self.private:
      return

    indent_str = indent * " "
    if self.required:
      req_kw = "required"
    else:
      req_kw = "optional"
    print >>out, indent_str + "Key: %s (%s)" % (self.get_presentable_key(), req_kw)
    if self.default_value:
      print >>out, indent_str + "  Default: %s" % repr(self.default)
    elif self.dynamic_default:
      print >>out, indent_str + "  Dynamic default: %s" % self.dynamic_default.__doc__.strip()

    print >>out, self.get_presentable_help_text(indent=indent)
    print >>out

  def get_presentable_help_text(self, indent=0):
    indent_str = " " * indent
    help = self.help or "[no help text provided]"
    help = textwrap.fill(help,
                         initial_indent=(indent_str + "  "),
                         subsequent_indent=(indent_str + "    "))
    return help

  def get_presentable_key(self):
    if self.key is _ANONYMOUS:
      return "<user specified name>" # TODO(todd) add "metavar" like optparse
    else:
      return self.key

  @property
  def default(self):
    if self.dynamic_default is not None:
      return self.dynamic_default()
    return self.default_value

class BoundContainer(BoundConfig):
  """Binds a ConfigSection to actual data."""

  def __contains__(self, item):
    return self.get().__contains__(item)

  def __iter__(self):
    return self.get().__iter__()

  def __len__(self):
    return len(self.get())

  def get_data_dict(self):
    data, present = self._get_data_and_presence()
    if present:
      return data
    else:
      assert self.grab_key is not _ANONYMOUS
      return self.bind_to.setdefault(self.grab_key, {})

  def keys(self):
    return self.get_data_dict().keys()

class BoundContainerWithGetAttr(BoundContainer):
  """
  A configuration bound to a data container where we expect
  the user to use getattr syntax (container.FOO) to access
  the members.

  This is used by ConfigSection
  """
  def __getattr__(self, attr):
    return self.config.get_member(self.get_data_dict(), attr, self.prefix)

class BoundContainerWithGetItem(BoundContainer):
  """
  A configuration bound to a data container where we expect
  the user to use [...] syntax to access the members.

  This is used for UnspecifiedConfigSection
  """
  def __getitem__(self, attr):
    if attr in self.__dict__:
      return self.__dict__[attr]
    return self.config.get_member(self.get_data_dict(), attr, self.prefix)


class ConfigSection(Config):
  """
  A section of configuration variables whose names are known
  a priori. For example, this can be used to group configuration
  for a cluster.
  """
  def __init__(self, key=_ANONYMOUS, members=None, **kwargs):
    """Initializes a ConfigSection

    @param members a dictionary whose keys are the attributes by which
                   the members are accessed. For example:
                     members=dict(FOO=Config(...))
                   means that you will access this configuration as
                   section.FOO.get()
    """
    super(ConfigSection, self).__init__(key, default={}, **kwargs)
    self.members = members or {}
    for member in members.itervalues():
      assert member.key is not _ANONYMOUS


  def update_members(self, new_members, overwrite=True):
    """
    Add the new_members to this ConfigSection.

    @param new_members  A dictionary of {key=Config(...), key2=Config(...)}.
    @param overwrite  Whether to overwrite the current member on key conflict.
    """
    for member in new_members.itervalues():
      assert member.key is not _ANONYMOUS
    if not overwrite:
      new_members = new_members.copy()
      for k in self.members.iterkeys():
        if new_members.has_key(k):
          del new_members[k]
    self.members.update(new_members)


  def bind(self, config, prefix):
    return BoundContainerWithGetAttr(self, bind_to=config, grab_key=self.key, prefix=prefix)

  def _coerce_type(self, raw, prefix=''):
    """
    Materialize this section as a dictionary.

    The keys are those specified in the members dict, and the values
    are bound configuration parameters.
    """
    return dict([(key, self.get_member(raw, key, prefix))
                 for key in self.members.iterkeys()])

  def get_member(self, data, attr, prefix):
    if self.key is not _ANONYMOUS:
      prefix += prefix and '.' + self.key or self.key
    return self.members[attr].bind(data, prefix)

  def print_help(self, out=sys.stdout, indent=0, skip_header=False):
    if self.private:
      return
    if not skip_header:
      print >>out, (" " * indent) + "[%s]" % self.get_presentable_key()
      print >>out, self.get_presentable_help_text(indent=indent)
      print >>out
      new_indent = indent + 2
    else:
      new_indent = indent

    # We sort the configuration for canonicalization.
    for programmer_key, config in sorted(self.members.iteritems(), key=lambda x: x[1].key):
      config.print_help(out=out, indent=new_indent)

class UnspecifiedConfigSection(Config):
  """
  A special Config that maps a section name to a list of anonymous subsections.
  The subsections are anonymous in the sense that their names are unknown beforehand,
  but all have the same structure.

  For example, this can be used for a [clusters] section which
  expects some number of [[cluster]] sections underneath it.

  This class is NOT a ConfigSection, although it supports get_member(). The key
  difference is that its get_member() returns a BoundConfig with:
  (1) an anonymous ConfigSection,
  (2) an anonymous grab_key, and
  (3) a `prefix' containing the prefix plus the actual key name.
  """
  def __init__(self, key=_ANONYMOUS, each=None, **kwargs):
    super(UnspecifiedConfigSection, self).__init__(key, default={}, **kwargs)
    assert each.key is _ANONYMOUS
    self.each = each    # `each' is a ConfigSection

  def bind(self, config, prefix):
    return BoundContainerWithGetItem(self, bind_to=config, grab_key=self.key, prefix=prefix)

  def _coerce_type(self, raw, prefix=''):
    """
    Materialize this section as a dictionary.

    The keys are the keys specified by the user in the config file.
    """
    return OrderedDict([(key, self.get_member(raw, key, prefix))
                 for key in raw.iterkeys()])

  def get_member(self, data, attr, prefix=''):
    tail = self.key + '.' + attr
    child_prefix = prefix
    child_prefix += prefix and '.' + tail or tail
    return self.each.bind(data[attr], child_prefix)

  def print_help(self, out=sys.stdout, indent=0):
    indent_str = " " * indent

    print >>out, indent_str + "[%s]" % self.get_presentable_key()
    print >>out, self.get_presentable_help_text(indent=indent)
    print >>out
    print >>out, indent_str + "  Consists of some number of sections like:"
    self.each.print_help(out=out, indent=indent+2)

def _configs_from_dir(conf_dir):
  """
  Generator to load configurations from a directory. This will
  only load files that end in .ini
  """
  for filename in sorted(os.listdir(conf_dir)):
    if filename.startswith(".") or not filename.endswith('.ini'):
      continue
    LOG.debug("Loading configuration from: %s" % filename)
    try:
      conf = ConfigObj(os.path.join(conf_dir, filename))
    except ConfigObjError, ex:
      LOG.error("Error in configuration file '%s': %s" % (os.path.join(conf_dir, filename), ex))
      raise
    conf['DEFAULT'] = dict(desktop_root=get_desktop_root(), build_dir=get_build_dir())
    yield conf

def load_confs(conf_source=None):
  """Loads and merges all of the configurations passed in,
  returning a ConfigObj for the result.

  @param conf_source if not specified, reads conf/ from
                     desktop/conf/. Otherwise should be a generator
                     of ConfigObjs
  """
  if conf_source is None:
    conf_source = _configs_from_dir(get_desktop_root("conf"))

  conf = ConfigObj()
  for in_conf in conf_source:
    conf.merge(in_conf)
  return conf

def _bind_module_members(module, data, section):
  """
  Bind all Config instances found inside the given module
  to the given data.

  Returns the dict of unbound configs.
  """
  members = {}
  for key, val in module.__dict__.iteritems():
    if not isinstance(val, Config):
      continue

    members[key] = val
    module.__dict__[key] = val.bind(data, prefix=section)
  return members


def bind_module_config(mod, conf_data, config_key):
  """Binds the configuration for the module to the given data.

  conf_data is a dict-like structure in which the configuration data
  has been loaded. The configuration for this module should be
  inside a section which is named as follows:
    - if the name of the module is foo.conf, it should be a section [foo]
    - if the name of the module is bar, it should be a section [bar]
    - if the module has a CONFIGURATION_SECTION attribute, that attribute
      should be a string, and determines the section name.

  config_key is the key that should map to the configuration.
  It's used to allow renaming of configurations.

  For example, for the module "hello.world.conf", type(conf_data['hello.world'])
  should be dict-like and contain the configuration for the hello.world
  module.

  Note that this mutates the contents of the module - any Config instances
  will be changed into BoundConfig instances such that you can call
  .get() on them.
  """
  if hasattr(mod, "CONFIGURATION_SECTION"):
    section = mod.CONFIGURATION_SECTION
  elif mod.__name__.endswith(".conf"):
    section = mod.__name__[:-len(".conf")]
  else:
    section = mod.__name__

  if config_key is None:
    bind_data = conf_data.get(section, {})
  else:
    section = config_key
    bind_data = conf_data.get(config_key, {})

  members = _bind_module_members(mod, bind_data, section)
  return ConfigSection(section, members=members, help=mod.__doc__)

def initialize(modules, config_dir):
  """
  Set up the GLOBAL_CONFIG variable by loading all configuration
  variables from the given module list.

  Repeated initialization updates GLOBAL_CONFIG with the configuration from the new module list.
  """
  global GLOBAL_CONFIG
  # Import confs
  conf_data = load_confs(_configs_from_dir(config_dir))
  sections = {}
  for module in modules:
    section = bind_module_config(module['module'], conf_data, module['config_key'])
    sections[section.key] = section

  GLOBAL_HELP = "(root of all configuration)"
  if GLOBAL_CONFIG is None:
    GLOBAL_CONFIG = ConfigSection(members=sections, help=GLOBAL_HELP).bind(conf_data, prefix='')
  else:
    new_config = ConfigSection(members=sections, help=GLOBAL_HELP)
    new_config.update_members(GLOBAL_CONFIG.config.members, overwrite=False)
    conf_data.merge(GLOBAL_CONFIG.bind_to)
    GLOBAL_CONFIG = new_config.bind(conf_data, prefix='')
  return

def is_anonymous(key):
  return key == _ANONYMOUS


def coerce_str_lowercase(value):
  return smart_str(value).lower()


def coerce_bool(value):
  if isinstance(value, bool):
    return value

  if isinstance(value, basestring):
    upper = value.upper()
  else:
    upper = value

  if upper in ("FALSE", "0", "NO", "OFF", "NAY", "", None):
    return False
  if upper in ("TRUE", "1", "YES", "ON", "YEA"):
    return True
  raise Exception("Could not coerce %r to boolean value" % (value,))

def coerce_string(value):
  if type(value) == list:
    return ','.join(value)
  else:
    return value

def coerce_csv(value):
  if isinstance(value, str):
    return value.split(',')
  elif isinstance(value, list):
    return value
  raise Exception("Could not coerce %r to csv array." % value)

def coerce_json_dict(value):
  if isinstance(value, basestring):
    return json.loads(value)
  elif isinstance(value, dict):
    return value
  raise Exception("Could not coerce %r to json dictionary." % value)

def list_of_compiled_res(skip_empty=False):
  def fn(list_of_strings):
    if isinstance(list_of_strings, basestring):
      list_of_strings = list_of_strings.split(',')
    list_of_strings = filter(lambda string: string if skip_empty else True, list_of_strings)
    return list(re.compile(x) for x in list_of_strings)
  return fn

def validate_path(confvar, is_dir=None, fs=os.path, message='Path does not exist on the filesystem.'):
  """
  Validate that the value of confvar is an existent path.

  @param confvar  The configuration variable.
  @param is_dir  True/False would verify that the path is/isn't a directory.
                 None to disable check.
  @return [(confvar, error_msg)] or []
  """
  path = confvar.get()
  if path is None or not fs.exists(path):
    return [(confvar, message)]
  if is_dir is not None:
    if is_dir:
      if not fs.isdir(path):
        return [(confvar, 'Not a directory.')]
    elif not fs.isfile(path):
      return [(confvar, 'Not a file.')]
  return [ ]

def validate_port(confvar):
  """
  Validate that the value of confvar is between [0, 65535].
  Returns [(confvar, error_msg)] or []
  """
  port_val = confvar.get()
  error_res = [(confvar, 'Port should be an integer between 0 and 65535 (inclusive).')]
  try:
    port = int(port_val)
    if port < 0 or port > 65535:
      return error_res
  except ValueError:
    return error_res
  return [ ]

def validate_thrift_transport(confvar):
  """
  Validate that the provided thrift transport is supported.
  Returns [(confvar, error_msg)] or []
  """
  transport = confvar.get()
  error_res = [(confvar, 'Thrift transport %s not supported. Please choose a supported transport: %s' % (transport, ', '.join(SUPPORTED_THRIFT_TRANSPORTS)))]

  if transport not in SUPPORTED_THRIFT_TRANSPORTS:
    return error_res

  return []

def coerce_password_from_script(script):
  p = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE)
  stdout, stderr = p.communicate()

  if p.returncode != 0:
    if stderr:
      LOG.error("Failed to read password from script:\n%s" % stderr)
    if os.environ.get('HUE_IGNORE_PASSWORD_SCRIPT_ERRORS') is None:
      raise subprocess.CalledProcessError(p.returncode, script)
    else:
      return None

  # whitespace may be significant in the password, but most files have a
  # trailing newline.
  return stdout.strip('\n')
