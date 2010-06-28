#!/usr/bin/env python
"""
Depender manages packages and components, which may
have dependencies upon each other.

There are historically two ways to specify a package:
  - package.yml specifies a package name and files
    it includes, and then the files have yaml headers
    specifying what they require and provide
  - scripts.json specifies a library (roughly equivalent
    to a package) which has files; the components
    are simply the filenames
The newer package.yml form lets you have multiple components
with the same name, if they're in different packages.

Here is how the classes are structured:

 DependerData:
   Inputs: package.yml files, scripts.json files (legacy)
     package -> PackageData
       metadata
       component -> FileData
         file_name/content
         provides: [(package, component)]
         requires: [(package, component)]
     legacy_component_name -> [packages]
    
 Components tend to be referred by (package, component) tuples.

TODO: Use a ComponentId class instead of a tuple.
"""

import re
import yaml
import os
import simplejson
import logging

# Matches the bit inbetween --- and ...
YAML_SECTION = re.compile(".*^---$(.*)^\.\.\.$.*", re.MULTILINE | re.DOTALL)

LOG = logging.getLogger(__name__)

class DependerData(object):
  """
  Main class that holds all the data.
  """
  def __init__(self, package_ymls=None, script_jsons=None):
    """
    package_ymls is list of filenames; script_jsons
    is list of (library_name, filename) pairs.
    """
    if package_ymls is None:
      package_ymls = []
    if script_jsons is None:
      scripts_json = []

    self.packages = {}
    self.unqualified_components = {}

    self.script_json_packages = []

    package_ymls = package_ymls or []
    self.yaml_packages = [ YamlPackageData(f) for f in package_ymls ]
    self.script_json_packages = [ ScriptsJsonPackage(pkg_name, scripts_json_file) for 
      pkg_name, scripts_json_file in script_jsons ]

    all_packages = self.yaml_packages + self.script_json_packages

    for p in all_packages:
      if p.key in self.packages:
        raise Exception("Duplicate package: " + p.key)
      self.packages[p.key] = p
      for component_name, file_data in p.components.iteritems():
        self.unqualified_components.setdefault(component_name, []).append(file_data)

    # Resolve script_json dependencies
    for p in self.script_json_packages:
      for fd in p.components.itervalues():
        try:
          fd.resolve_dependencies(self)
        except: 
          LOG.exception("Error in %s" % p.scripts_json_filename)
          raise
    try:
      self.self_check()
    except:
      LOG.exception("Depender self check failed.  Continuing with abandon.")

  def resolve_unqualified_component(self, component, preferred_package=None):
    """
    Returns a (package, component) tuple given only a component name.
    This is useful when only the component is known (legacy scripts.json).

    This is only possible when the name is unique or when
    there's a preferred package (because we might prefer
    the "current" package).
    """
    possibilities = self.unqualified_components.get(component, [])
    if len(possibilities) == 0:
      raise Exception("Could not find dependency %r." % component)
    elif len(possibilities) == 1:
      return possibilities[0].package.key, component
    elif len(possibilities) > 1:
      # Prefer dependencies inside the same package
      if preferred_package is not None:
        if component in self.packages[preferred_package].components:
          LOG.warn("Multiple dependencies were possible for component %r" % component)
          return (preferred_package, component)
      else:
        raise Exception("Could not resolve ambiguous dependency %r" % component)

  def self_check(self):
    """
    Checks that no dependencies are unsatisfied.

    TODO: Does not check that there are no cycles
    in the dependency graph.
    """
    out = "Loaded components\n"
    for package_name, package in sorted(self.packages.items()):
      out += "\t%s:\n" % package_name
      for c, fd in sorted(package.components.iteritems()):
        out += "\t\t%s (%s)\n" % (c, fd.filename)

    LOG.info(out)

    for p in self.packages.values():
      for f in p.files:
        for id in f.requires:
          # This throws if it doesn't find something.
          try:
            self.get(id)
          except:
            LOG.exception("Error in: " + f.filename)
            raise
          
  def get(self, id):
    """
    Retrieves a FileData object given (package, component) pair.
    """
    pkg_key, component_key = id
    if pkg_key not in self.packages:
      raise Exception("Package not found while looking for id: %s " % repr(id))
    p = self.packages[pkg_key]
    if component_key not in p.components:
      raise Exception("Component %s not found in package %s." % (component_key, pkg_key))
    return p.components[component_key]

  def get_client_js(self, components, url):
    """
    returns the javascript necessary to integrate with Depender.Client.js

    @param components: Component ids loaded in this pass.
    @param url: the url of the builder view
    """
    out = "\n\n"
    if len(components) > 0:
      out += "Depender.loaded.combine(['"
      out += "','".join([ "/".join(c) for c in components ]) + "']);\n\n"
    out += "Depender.setOptions({\n"
    out += "	builder: '" + url + "'\n"
    out += "});"
    return out;

  def graph(self):
    """
    Returns a pydot.Dot object representing the dependency graph.
    Requires pydot to be available.
    """
    import pydot
    edges = set()
    for p in self.packages.values():
      for f in p.files:
        for id in f.requires:
          f2 = self.get(id)
          edges.add( ("--".join([p.key, f.shortname]), "--".join([f2.package.key, f2.shortname])) )
    return pydot.graph_from_edges(edges, directed=True)

  def _get_transitive_dependencies_helper(self, target, excluded_set, accumulator, depth_limit=30):
    """
    @param target is a single required component id
    @param excluded_set is a list of components already loaded or previously included
    @param accumulator is an ordered list of components to load

    It would be possible to combine excluded_set and accumulator into one
    if python had built-in ordered sets, but note that excluded_set might
    be non empty at the beginning.
    """
    if depth_limit <= 0:
      raise Exception("Dependency depth limit exceeded, resolving: %s" % (str(target),) )
    if target in excluded_set:
      return
    for c in self.get(target).requires:
      if c not in excluded_set:
        self._get_transitive_dependencies_helper(c, excluded_set, accumulator, depth_limit=depth_limit-1)
    accumulator.append(target)
    excluded_set.add(target)

  def get_transitive_dependencies(self, required, excluded=None):
    """
    required and excluded are lists of (package, component) pairs

    Returns an ordered list of (package, component) pairs.
    """
    required = set(required)
    if excluded is None:
      excluded = []
    orig_excluded = excluded
    excluded = set(excluded)
    accumulator = []
    for c in required:
      self._get_transitive_dependencies_helper(c, excluded, accumulator)
    LOG.debug("Calculated dependencies: %s - %s: %s" % (repr(required), repr(orig_excluded), repr(accumulator)))
    return accumulator

  def expand_package(self, pkg):
    """
    Expands a package name into all its components.
    """
    return [ (pkg, c) for c in self.packages[pkg].components ]

  def get_files(self, components, excluded_components=None):
    """
    Retrieves list of DataFile objects given required components.

    Note that we have to expand excluded components into their
    files: Say A depends on B, and (B,C) are colocated in one file.
    If we already have C, we must already have B, even if we
    don't know it.

    TODO: arguably, this is a bug in get_client_js, which
    should expand everything.
    """
    if excluded_components is None:
      excluded_components = []
  
    # List of already processed or excluded
    files_set = set()
    excluded_files_set = set()
    files = []
    
    for c in excluded_components:
      excluded_files_set.add(self.get(c))

    for c in components:
      f = self.get(c)
      if f not in files_set and f not in excluded_files_set:
        files_set.add(f)
        files.append(f)
    return files

def _coerce_string_to_list(potential_string):
  if isinstance(potential_string, basestring):
    return [ potential_string ]
  else:
    return potential_string

class YamlFileData(object):
  """Source file pointed to by a package.yml."""
  def __init__(self, shortname, filename, package, metadata):
    self.shortname = shortname
    self.filename = filename
    self.content = _force_unicode(file(filename).read())
    self.metadata = metadata
    self.package = package
    self.provides = [(package.key, module) for module in _coerce_string_to_list(metadata["provides"])]
    self.requires = []
    self.requires = [ self._parse_component_string(r) for r in _coerce_string_to_list(metadata.get("requires", [])) ]

  def _parse_component_string(self, component):
    """
    Parses package:version/component string into (package, component).
    """
    # In package.yml files, the syntax is "package:version/component",
    # and an empty package:version implies "current package".
    # This code ignores version.
    package_component = component.split("/", 2)
    if len(package_component) == 1:
      package_key = self.package.key
      component = package_component[0]
    else:
      package, component = package_component
      if package is "":
        package_key = self.package.key
      else:
        package_key = package.split(":")[0]
    return package_key, component

class ScriptsJsonFileData(object):
  """Source file pointed to by a scripts.json"""
  def __init__(self, module_name, shortname, filename, package, metadata):
    self.filename = filename
    self.shortname = shortname
    self.content = _force_unicode(file(filename).read())
    self.package = package
    self.metadata = metadata
    self.provides = [ (package.key, module_name) ]

  def resolve_dependencies(self, all_data):
    """
    We resolve dependencies after everything has been loaded, to 
    be able to notice ambiguous dependencies.
    """
    self.requires = []
    for dep in self.metadata["deps"]:
      key = (self.package.key, dep)
      if key in self.provides:
        raise Exception("Package shouldn't depend on itself: %s" % repr(key))
      self.requires.append( all_data.resolve_unqualified_component(dep, self.package.key) )
        
class YamlPackageData(object):
  def __init__(self, package_filename):
    self.components = {}
    self.files = []
    try:
      self.metadata = yaml.load(file(package_filename))
    except:
      LOG.exception("Could not parse: " + package_filename)
      raise
    rootdir = os.path.dirname(package_filename)
    self.key = self.metadata["name"]
    for source_file in self.metadata["sources"]:
      filename = os.path.join(rootdir, source_file)
      metadata = _parse_js_file(filename)
      assert len(metadata["provides"]) > 0
      try:
        fd = YamlFileData(source_file, filename, self, metadata)
      except:
        LOG.exception("Error processing: " + filename)
        raise
      self.files.append(fd)
      for pkg_key, component in fd.provides:
        assert pkg_key == self.key
        if component in self.components:
          raise Exception("Two files provide %s: %s and %s" % (component, self.components[component].filename, fd.filename))
        self.components[component] = fd

class ScriptsJsonPackage(object):
  def __init__(self, package_name, scripts_json_filename):
    self.components = {}
    self.files = []
    self.key = package_name
    self.metadata = simplejson.load(file(scripts_json_filename))
    self.scripts_json_filename = scripts_json_filename
    rootdir = os.path.dirname(scripts_json_filename)
    for category, components in self.metadata.iteritems():
      for component, metadata in components.iteritems():
        filename = os.path.join(rootdir, category, component) + ".js"
        shortname = os.path.join(category, component)
        if not os.path.exists(filename):  
          raise Exception("File not found: " + filename)
        fd = ScriptsJsonFileData(component, shortname, filename, self, metadata)
        if component in self.components:
          raise Exception("Two files provide %s: %s and %s" % (component, self.components[component].filename, fd.filename))
        self.components[component] = fd
        self.files.append(fd)

  def rewrite(self):
    """Edits the scripts to use the new YaML syntax."""
    for f in self.files:
      metadata = dict()
      metadata["description"] = f.metadata.get("desc", "Unknown")
      metadata["script"] = os.path.basename(f.filename)
      metadata["requires"] = []
      for package, component in f.requires:
        if package == self.key:
          metadata["requires"].append("/" + component)
        else:
          metadata["requires"].append(package + "/" + component)
      metadata["provides"] = [ p[1] for p in f.provides ]
      # Resolve symlinks
      real_filename = os.path.realpath(f.filename)
      LOG.info("Editing: " + real_filename)
      new_filename = f.filename + ".new"
      new = file(new_filename, "w")
      new.write("/*\n---\n")
      new.write(yaml.dump(metadata))
      new.write("\n...\n*/\n")
      new.write(file(f.filename).read())
      new.close()
      os.rename(new_filename, real_filename)

    package_data = dict()
    package_data["name"] = self.key
    package_data["sources"] = []
    package_data["version"] = "Unknown"
    package_data["copyright"] = "Unknown"
    package_data["description"] = "Unknown"
    target_dir = os.path.dirname(self.scripts_json_filename)
    # package.yml is typically in the parent of the scripts.json dir
    if os.path.basename(target_dir) == "Source":
      target_dir = os.path.dirname(target_dir)
    target_filename = os.path.join(target_dir, "package.yml")
    for f in self.files:
      common = os.path.commonprefix([target_filename, f.filename])
      source_file = f.filename[len(common):]
      package_data["sources"].append(source_file)
    LOG.info("Writing: " + target_filename)
    out = file(target_filename, "w")
    out.write(yaml.dump(package_data))
    out.close()

def _force_unicode(data):
  """Encodings of the js files are unclear; force things
  into unicode, somewhat hackily."""
  try:
    data = unicode(data, "utf-8")
  except UnicodeDecodeError:
    data = unicode(data, "latin1")
  return data
          
def _parse_js_file(filename):
  """Find yaml section in javascript file."""
  data = _force_unicode(file(filename).read())

  m = YAML_SECTION.match(data)
  if not m:
    raise Exception("Could not succesfully find YAML section in %r." % filename)
    return None
  try:  
    return yaml.load(m.groups(0)[0])    
  except:
    LOG.exception("Could not parse: " + filename)
    raise

#############################################
#
# Below are commands run by the "main", which provide
# some handy utilities.
#
# TODO(philip): Move these into management commands.
def graph(data, args):
  if len(args) != 1:
    LOG.fatal("Expected output filename.")
    return 1
  g = data.graph()
  g.write_png(args[0])
  print "Wrote " + args[0]

def resolve(data, args):
  required = args[0].split(",")
  if len(args) > 1:
    excluded = args[1].split(",")
  else:
    excluded = []
  def make_ids(data):
    return [ tuple(x.split("/", 2)) for x in data ]
  print data.get_transitive_dependencies(make_ids(required), make_ids(excluded))

# TODO: The migration of these commands into Django management commands
# is already in progress!
if __name__ == "__main__":
  LOG.basicConfig(level=logging.INFO)
  import sys
  yamls = []
  scripts_json = []

  paths = sys.argv[1].split(",")
  for path in paths:
    if path.endswith(".yml"):
      yamls.append(path)
    elif path.endswith(".json"):
      scripts_json.append(path.split(":", 2))
    else:
      raise Exception("Unexpected path: " + path)
  data = DependerData(yamls, scripts_json)
  command = sys.argv[2]

  if command == "graph":
    sys.exit(graph(data, sys.argv[3:]) or 0)
  elif command == "resolve":
    sys.exit(resolve(data, sys.argv[3:]) or 0)
  else:
    raise Exception("Unrecognized command: " + command)
