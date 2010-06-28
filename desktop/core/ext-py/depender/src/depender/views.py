#!/usr/bin/env python
#
# JavaScript depender.  Loads and concatenates necessary
# JavaScript files.

import logging

from django.http import HttpResponse
from django.conf import settings
from django.core import urlresolvers

from depender.core import DependerData

LOG = logging.getLogger(__name__)

def make_depender():
  try:
    return DependerData(settings.DEPENDER_PACKAGE_YMLS, settings.DEPENDER_SCRIPTS_JSON)
  except:
    logging.exception("Could not build JavaScript dependency map.")
    return None

depender = make_depender()

def get_depender(reset):
  global depender
  if settings.DEPENDER_DEBUG:
    return make_depender()
  else:
    if reset == "true":
      depender = make_depender()
    return depender

def massage(depender, components, packages):
  """
  @param depender: A DependerData object
  @param components: Component names, in either package/component format, or just
    "naked" (hopefully unique) components.
  @param packages: Package names, which expand into their constituent components.
  @return A set of all components specified.
  """
  ret = set()
  for package in packages:
    ret.update(depender.expand_package(package))
  for component in components:
    if "/" in component:
      ret.add( tuple(component.split("/", 2)) )
    else:
      ret.add( depender.resolve_unqualified_component(component) )
  return ret

def build(request):
  """
    builds a library given required scripts to includes and other arguments
    accepted URL arguments:

    all - if set to "true", returns all the javascript, except as specified by exclude.  require and requireLibs are ignored.
    require - a comma separated list of *files*(components) to require; can also be specified in the php style as "require[]=foo&require[]=bar"
    requireLibs - a comma separated list of *libraries*(packages) to require - these are the names defined in our *congfig.json* in the *libs* section. So, for example, *requireLibs=mootools-core,mootools-more* using the default config would include both the complete inventories of MooTools Core and More. This can also be specified as a comma separated list or the php style (*requireLibs[]=mootools-core&requireLibs[]=mootools-more*).
    exclude - exactly like the *require* value, except it's a list of files to exclude. This is useful if you have already loaded some scripts and now you require another. You can specify the scripts you already have and the one you now need, and the library will return only those you do not have.
    excludeLibs - just like the *exclude* option but instead you can specify entire libraries.
    NOT IMPLEMENTED: cache - if set to *true* you'll be returned a cached version of the script even if the server is set to *false* and vice versa.
    compression - you'll be returned the compression type you specify regardless of the server default. Note that if you specify a compression type that the server does not allow, you'll be returned which ever one it does. If it does not support compression at all, you will not be returned a compressed file. You can also specify "none" which is useful for development and debugging.
  """
  def get(name):
    return request.GET.get(name)
  def get_arr(name):
    val = get(name)
    if val:
      return val.split(",")
    else:
      return []

  all = get("all")
  require = get_arr("require")
  exclude = get_arr("exclude")
  excludeLibs = get_arr("excludeLibs")
  requireLibs = get_arr("requireLibs")
  download = get("download")
  reset = get("reset")
  client = get("client")
  compression = get("compression")

  dpdr = get_depender(reset)
  if dpdr is None:
    return HttpResponse("alert('Javascript dependency loader unavailable. Contact your administrator to check server logs for details.')")
    
  if compression is None:
    compression = "none"
    # TODO: implement compression
    # compression = dpdr.default_compression
  if settings.DEPENDER_DEBUG:
    compression = "none"

  if client == "true" and "Depender.Client" not in require:
    require.append("Depender.Client")

  if all == "true":
    require = []
    requireLibs = depender.packages.keys()

  required = massage(depender, require, requireLibs)
  excluded = massage(depender, exclude, excludeLibs)

  deps = dpdr.get_transitive_dependencies(required, excluded)
  files = dpdr.get_files(deps, excluded)
  output = "//No files included for build"

  if len(files) > 0:
    #TODO: add copyrights
    #TODO: add link to download link
    #TODO: add download file stuff
    output = u""
    output += "\n//This library: " + request.build_absolute_uri(request.get_full_path())
    output += "\n//Contents: "
    output += ", ".join([ i.package.key + ":" + i.shortname for i in files ])
    output += "\n\n"
  
    for f in files:
      output += "// Begin: " + f.shortname + "\n"
      output += f.content + u"\n\n"

  if client == "true":
    url = request.build_absolute_uri(
      urlresolvers.reverse("depender.views.build"))
    output += dpdr.get_client_js(deps, url)

  response = HttpResponse(output, content_type="application/x-javascript")
  if download == "true":
    response['Content-Disposition'] = 'attachment; filename=built.js'
  return response
build.login_notrequired = True

def test(request):
  #this seems silly
  import os
  p = os.path.join(os.path.dirname(__file__), "static", "test.html")
  f = file(p)
  return HttpResponse(f.read())
