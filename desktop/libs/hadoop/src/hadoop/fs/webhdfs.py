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
Interfaces for Hadoop filesystem access via HttpFs/WebHDFS
"""

import errno
import logging
import posixpath
import stat
import threading
import time

from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from desktop.lib.rest import http_client, resource
from hadoop.fs import normpath, SEEK_SET, SEEK_CUR, SEEK_END
from hadoop.fs.hadoopfs import Hdfs
from hadoop.fs.exceptions import WebHdfsException
from hadoop.fs.webhdfs_types import WebHdfsStat, WebHdfsContentSummary
from hadoop.conf import UPLOAD_CHUNK_SIZE

import hadoop.conf


DEFAULT_HDFS_SUPERUSER = 'hdfs'

# The number of bytes to read if not specified
DEFAULT_READ_SIZE = 1024*1024 # 1MB

LOG = logging.getLogger(__name__)


class WebHdfs(Hdfs):
  """
  WebHdfs implements the filesystem interface via the WebHDFS rest protocol.
  """
  DEFAULT_USER = 'hue'        # This should be the user running Hue
  TRASH_CURRENT = 'Current'

  def __init__(self, url,
               fs_defaultfs,
               logical_name=None,
               hdfs_superuser=None,
               security_enabled=False,
               temp_dir="/tmp"):
    self._url = url
    self._superuser = hdfs_superuser
    self._security_enabled = security_enabled
    self._temp_dir = temp_dir
    self._fs_defaultfs = fs_defaultfs
    self._logical_name = logical_name

    self._client = self._make_client(url, security_enabled)
    self._root = resource.Resource(self._client)

    # To store user info
    self._thread_local = threading.local()

    LOG.debug("Initializing Hadoop WebHdfs: %s (security: %s, superuser: %s)" %
              (self._url, self._security_enabled, self._superuser))

  @classmethod
  def from_config(cls, hdfs_config):
    fs_defaultfs = hdfs_config.FS_DEFAULTFS.get()
    return cls(url=_get_service_url(hdfs_config),
               fs_defaultfs=fs_defaultfs,
               logical_name=hdfs_config.LOGICAL_NAME.get(),
               security_enabled=hdfs_config.SECURITY_ENABLED.get(),
               temp_dir=hdfs_config.TEMP_DIR.get())

  def __str__(self):
    return "WebHdfs at %s" % self._url

  def _make_client(self, url, security_enabled):
    client = http_client.HttpClient(
        url, exc_class=WebHdfsException, logger=LOG)
    if security_enabled:
      client.set_kerberos_auth()
    return client

  @property
  def uri(self):
    return self._url

  @property
  def logical_name(self):
    return self._logical_name

  @property
  def fs_defaultfs(self):
    return self._fs_defaultfs

  @property
  def security_enabled(self):
    return self._security_enabled

  @property
  def superuser(self):
    if self._superuser is None:
      try:
        # The owner of '/' is usually the superuser
        sb = self.stats('/')
        self._superuser = sb.user
      except Exception, ex:
        LOG.exception('Failed to determine superuser of %s: %s' % (self, ex))
        self._superuser = DEFAULT_HDFS_SUPERUSER

    return self._superuser

  @property
  def user(self):
    try:
      return self._thread_local.user
    except AttributeError:
      return WebHdfs.DEFAULT_USER

  @property
  def trash_path(self):
    return self.join(self.get_home_dir(), '.Trash')

  @property
  def current_trash_path(self):
    return self.join(self.trash_path, self.TRASH_CURRENT)

  def _getparams(self):
    return {
      "user.name" : WebHdfs.DEFAULT_USER,
      "doas" : self.user
    }

  def setuser(self, user):
    """Set a new user. Return the current user."""
    curr = self.user
    self._thread_local.user = user
    return curr

  def listdir_stats(self, path, glob=None):
    """
    listdir_stats(path, glob=None) -> [ WebHdfsStat ]

    Get directory listing with stats.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    if glob is not None:
      params['filter'] = glob
    params['op'] = 'LISTSTATUS'
    json = self._root.get(path, params)
    filestatus_list = json['FileStatuses']['FileStatus']
    return [ WebHdfsStat(st, path) for st in filestatus_list ]

  def listdir(self, path, glob=None):
    """
    listdir(path, glob=None) -> [ entry names ]

    Get directory entry names without stats.
    """
    dirents = self.listdir_stats(path, glob)
    return [Hdfs.basename(x.path) for x in dirents]

  def get_content_summary(self, path):
    """
    get_content_summary(path) -> WebHdfsContentSummary
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'GETCONTENTSUMMARY'
    json = self._root.get(path, params)
    return WebHdfsContentSummary(json['ContentSummary'])


  def _stats(self, path):
    """This version of stats returns None if the entry is not found"""
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'GETFILESTATUS'
    try:
      json = self._root.get(path, params)
      return WebHdfsStat(json['FileStatus'], path)
    except WebHdfsException, ex:
      if ex.server_exc == 'FileNotFoundException' or ex.code == 404:
        return None
      raise ex

  def stats(self, path):
    """
    stats(path) -> WebHdfsStat
    """
    res = self._stats(path)
    if res is not None:
      return res
    raise IOError(errno.ENOENT, _("File %s not found") % path)

  def exists(self, path):
    return self._stats(path) is not None

  def isdir(self, path):
    sb = self._stats(path)
    if sb is None:
      return False
    return sb.isDir

  def isfile(self, path):
    sb = self._stats(path)
    if sb is None:
      return False
    return not sb.isDir

  def _ensure_current_trash_directory(self):
    """Create trash directory for a user if it doesn't exist."""
    if self.exists(self.current_trash_path):
      self.mkdir(self.current_trash_path)
    return self.current_trash_path

  def _trash(self, path, recursive=False):
    """
    _trash(path, recursive=False)

    Move a file or directory to trash.
    Will create a timestamped directory underneath /user/<username>/.Trash.

    Trash must be enabled for this to work.
    """
    if not self.exists(path):
      raise IOError(errno.ENOENT, _("File %s not found") % path)

    if not recursive and self.isdir(path):
      raise IOError(errno.EISDIR, _("File %s is a directory") % path)

    if path.startswith(self.trash_path):
      raise IOError(errno.EPERM, _("File %s is already trashed") % path)

    # Make path (with timestamp suffix if necessary)
    base_trash_path = self.join(self._ensure_current_trash_directory(), path[1:])
    trash_path = base_trash_path
    while self.exists(trash_path):
      trash_path = base_trash_path + str(time.time())

    # Move path to trash path
    self.mkdir(self.dirname(trash_path))
    self.rename(path, trash_path)


  def _delete(self, path, recursive=False):
    """
    _delete(path, recursive=False)

    Delete a file or directory.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'DELETE'
    params['recursive'] = recursive and 'true' or 'false'
    result = self._root.delete(path, params)
    # This part of the API is nonsense.
    # The lack of exception should indicate success.
    if not result['boolean']:
      raise IOError(_('Delete failed: %s') % path)

  def remove(self, path, skip_trash=False):
    """Delete a file."""
    if skip_trash:
      self._delete(path, recursive=False)
    else:
      self._trash(path, recursive=False)

  def rmdir(self, path, skip_trash=False):
    """Delete a directory."""
    self.remove(path, skip_trash)

  def rmtree(self, path, skip_trash=False):
    """Delete a tree recursively."""
    if skip_trash:
      self._delete(path, recursive=True)
    else:
      self._trash(path, recursive=True)

  def restore(self, path):
    """
    restore(path)

    The root of ``path`` will be /users/<current user>/.Trash/<timestamp>.
    Removing the root from ``path`` will provide the original path.
    Ensure parent directories exist and rename path.
    """
    if not path.startswith(self.trash_path):
      raise IOError(errno.EPERM, _("File %s is not in trash") % path)

    # Build original path
    original_path = []
    split_path = self.split(path)
    while split_path[0] != self.trash_path:
      original_path.append(split_path[1])
      split_path = self.split(split_path[0])
    original_path.reverse()
    original_path = self.join(posixpath.sep, *original_path)

    # move to original path
    # the path could have been expunged.
    if self.exists(original_path):
      raise IOError(errno.EEXIST, _("Path %s already exists.") % str(smart_str(original_path)))
    self.rename(path, original_path)

  def purge_trash(self):
    """
    purge_trash()

    Purge all trash in users ``trash_path``
    """
    for timestamped_directory in self.listdir(self.trash_path):
      self.rmtree(self.join(self.trash_path, timestamped_directory), True)

  def mkdir(self, path, mode=None):
    """
    mkdir(path, mode=None)

    Creates a directory and any parent directory if necessary.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'MKDIRS'
    if mode is not None:
      params['permission'] = safe_octal(mode)
    success = self._root.put(path, params)
    if not success:
      raise IOError(_("Mkdir failed: %s") % path)

  def rename(self, old, new):
    """rename(old, new)"""
    old = Hdfs.normpath(old)
    if not new.startswith('/'):
      new = Hdfs.join(Hdfs.dirname(old), new)
    new = Hdfs.normpath(new)
    params = self._getparams()
    params['op'] = 'RENAME'
    # Encode `new' because it's in the params
    params['destination'] = smart_str(new)
    result = self._root.put(old, params)
    if not result['boolean']:
      raise IOError(_("Rename failed: %s -> %s") %
                    (str(smart_str(old)), str(smart_str(new))))

  def rename_star(self, old_dir, new_dir):
    """Equivalent to `mv old_dir/* new"""
    if not self.isdir(old_dir):
      raise IOError(errno.ENOTDIR, _("'%s' is not a directory") % old_dir)
    if not self.exists(new_dir):
      self.mkdir(new_dir)
    elif not self.isdir(new_dir):
      raise IOError(errno.ENOTDIR, _("'%s' is not a directory") % new_dir)
    ls = self.listdir(old_dir)
    for dirent in ls:
      self.rename(Hdfs.join(old_dir, dirent), Hdfs.join(new_dir, dirent))

  def chown(self, path, user=None, group=None, recursive=False):
    """chown(path, user=None, group=None, recursive=False)"""
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'SETOWNER'
    if user is not None:
      params['owner'] = user
    if group is not None:
      params['group'] = group
    if recursive:
      for xpath in self.listdir_recursive(path):
        self._root.put(xpath, params)
    else:
      self._root.put(path, params)


  def chmod(self, path, mode, recursive=False):
    """
    chmod(path, mode, recursive=False)

    `mode' should be an octal integer or string.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'SETPERMISSION'
    params['permission'] = safe_octal(mode)
    if recursive:
      for xpath in self.listdir_recursive(path):
        self._root.put(xpath, params)
    else:
      self._root.put(path, params)

  def get_home_dir(self):
    """get_home_dir() -> Home directory for the current user"""
    params = self._getparams()
    params['op'] = 'GETHOMEDIRECTORY'
    res = self._root.get(params=params)
    return res['Path']


  def read(self, path, offset, length, bufsize=None):
    """
    read(path, offset, length[, bufsize]) -> data

    Read data from a file.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'OPEN'
    params['offset'] = long(offset)
    params['length'] = long(length)
    if bufsize is not None:
      params['bufsize'] = bufsize
    try:
      return self._root.get(path, params)
    except WebHdfsException, ex:
      if "out of the range" in ex.message:
        return ""
      raise ex


  def open(self, path, mode='r'):
    """
    DEPRECATED!
    open(path, mode='r') -> File object

    This exists for legacy support and backwards compatibility only.
    Please use read().
    """
    return File(self, path, mode)


  def create(self, path, overwrite=False, blocksize=None,
             replication=None, permission=None, data=None):
    """
    create(path, overwrite=False, blocksize=None, replication=None, permission=None)

    Creates a file with the specified parameters.
    `permission' should be an octal integer or string.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'CREATE'
    params['overwrite'] = overwrite and 'true' or 'false'
    if blocksize is not None:
      params['blocksize'] = long(blocksize)
    if replication is not None:
      params['replication'] = int(replication)
    if permission is not None:
      params['permission'] = safe_octal(permission)

    self._invoke_with_redirect('PUT', path, params, data)


  def append(self, path, data):
    """
    append(path, data)

    Append data to a given file.
    """
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'APPEND'
    self._invoke_with_redirect('POST', path, params, data)


  # e.g. ACLSPEC = user:joe:rwx,user::rw-
  def modify_acl_entries(self, path, aclspec):
    path = Hdfs.normpath(path)
    params = self._getparams()
    params['op'] = 'MODIFYACLENTRIES'
    params['aclspec'] = aclspec
    self._invoke_with_redirect('PUT', path, params)


  def remove_acl_entries(self, path, aclspec):
      path = Hdfs.normpath(path)
      params = self._getparams()
      params['op'] = 'REMOVEACLENTRIES'
      params['aclspec'] = aclspec
      self._invoke_with_redirect('PUT', path, params)


  def remove_default_acl(self, path):
      path = Hdfs.normpath(path)
      params = self._getparams()
      params['op'] = 'REMOVEDEFAULTACL'
      self._invoke_with_redirect('PUT', path, params)


  def remove_acl(self, path):
      path = Hdfs.normpath(path)
      params = self._getparams()
      params['op'] = 'REMOVEACL'
      self._invoke_with_redirect('PUT', path, params)


  def set_acl(self, path, aclspec):
      path = Hdfs.normpath(path)
      params = self._getparams()
      params['op'] = 'REMOVEACL'
      params['aclspec'] = aclspec
      self._invoke_with_redirect('PUT', path, params)


  def get_acl_status(self, path):
      path = Hdfs.normpath(path)
      params = self._getparams()
      params['op'] = 'GETACLSTATUS'
      self._invoke_with_redirect('PUT', path, params)


  def copyfile(self, src, dst, skip_header=False):
    sb = self._stats(src)
    if sb is None:
      raise IOError(errno.ENOENT, _("Copy src '%s' does not exist") % src)
    if sb.isDir:
      raise IOError(errno.INVAL, _("Copy src '%s' is a directory") % src)
    if self.isdir(dst):
      raise IOError(errno.INVAL, _("Copy dst '%s' is a directory") % dst)

    offset = 0

    while True:
      data = self.read(src, offset, UPLOAD_CHUNK_SIZE.get())
      if offset == 0:
        if skip_header:
          n = data.index('\n')
          if n > 0:
            data = data[n + 1:]
        self.create(dst,
                    overwrite=True,
                    blocksize=sb.blockSize,
                    replication=sb.replication,
                    permission=oct(stat.S_IMODE(sb.mode)),
                    data=data)

      if offset != 0:
        self.append(dst, data)

      cnt = len(data)
      if cnt < UPLOAD_CHUNK_SIZE.get():
        break

      offset += cnt


  def copy_remote_dir(self, source, destination, dir_mode=0755, owner=None):
    if owner is None:
      owner = self.DEFAULT_USER
    self.do_as_user(owner, self.mkdir, destination, mode=dir_mode)
    self.do_as_user(owner, self.chmod, destination, mode=dir_mode) # To remove after HDFS-3491

    for stat in self.listdir_stats(source):
      source_file = stat.path
      destination_file = posixpath.join(destination, stat.name)
      if stat.isDir:
        self.copy_remote_dir(source_file, destination_file, dir_mode, owner)
      else:
        self.do_as_user(owner, self.copyfile, source_file, destination_file)
        self.do_as_superuser(self.chown, destination_file, owner, owner)


  def copy(self, src, dest, recursive=False, dir_mode=0755, owner=None):
    """
    Copy file, or directory, in HDFS to another location in HDFS.

    ``src`` -- The directory, or file, to copy from.
    ``dest`` -- the directory, or file, to copy to.
            If 'dest' is a directory that exists, copy 'src' into dest.
            If 'dest' is a file that exists and 'src' is a file, overwrite dest.
            If 'dest' does not exist, create 'src' as 'dest'.
    ``recursive`` -- Recursively copy contents of 'src' to 'dest'.
                 This is required for directories.
    ``dir_mode`` and ``owner`` are used to define permissions on the newly
    copied files and directories.

    This method will overwrite any pre-existing files that collide with what is being copied.
    Copying a directory to a file is not allowed.
    """
    if owner is None:
      owner = self.user

    src = self.abspath(src)
    dest = self.abspath(dest)

    if not self.exists(src):
      raise IOError(errno.ENOENT, _("File not found: %s") % src)

    if self.isdir(src):
      # 'src' is directory.
      # Skip if not recursive copy and 'src' is directory.
      if not recursive:
        LOG.debug("Skipping contents of %s" % src)
        return None

      # If 'dest' is a directory change 'dest'
      # to include 'src' basename.
      # create 'dest' if it doesn't already exist.
      if self.exists(dest):
        if self.isdir(dest):
          dest = self.join(dest, self.basename(src))
        else:
          raise IOError(errno.EEXIST, _("Destination file %s exists and is not a directory.") % dest)
      self.do_as_user(owner, self.mkdir, dest)
      self.do_as_user(owner, self.chmod, dest, mode=dir_mode)

      # Copy files in 'src' directory to 'dest'.
      self.copy_remote_dir(src, dest, dir_mode, owner)
    else:
      # 'src' is a file.
      # If 'dest' is a directory, then copy 'src' into that directory.
      # Other wise, copy to 'dest'.
      if self.exists(dest) and self.isdir(dest):
        self.copyfile(src, self.join(dest, self.basename(src)))
      else:
        self.copyfile(src, dest)


  @staticmethod
  def urlsplit(url):
    return Hdfs.urlsplit(url)


  def get_hdfs_path(self, path):
    return posixpath.join(self.fs_defaultfs, path.lstrip('/'))


  def _invoke_with_redirect(self, method, path, params=None, data=None):
    """
    Issue a request, and expect a redirect, and then submit the data to
    the redirected location. This is used for create, write, etc.

    Returns the response from the redirected request.
    """
    next_url = None
    try:
      # Do not pass data in the first leg.
      self._root.invoke(method, path, params)
    except WebHdfsException, ex:
      # This is expected. We get a 307 redirect.
      # The following call may throw.
      next_url = self._get_redirect_url(ex)

    if next_url is None:
      raise WebHdfsException(
        _("Failed to create '%s'. HDFS did not return a redirect") % path)

    # Now talk to the real thing. The redirect url already includes the params.
    client = self._make_client(next_url, self.security_enabled)
    headers = {'Content-Type': 'application/octet-stream'}
    return resource.Resource(client).invoke(method, data=data, headers=headers)


  def _get_redirect_url(self, webhdfs_ex):
    """Retrieve the redirect url from an exception object"""
    try:
      # The actual HttpError (307) is wrapped inside
      http_error = webhdfs_ex.get_parent_ex()
      if http_error is None:
        raise webhdfs_ex

      if http_error.response.status_code not in (301, 302, 303, 307):
        LOG.error("Response is not a redirect: %s" % webhdfs_ex)
        raise webhdfs_ex
      return http_error.response.headers['location']
    except Exception, ex:
      LOG.error("Failed to read redirect from response: %s (%s)" %
                (webhdfs_ex, ex))
      raise webhdfs_ex

  def get_delegation_token(self, renewer):
    """get_delegation_token(user) -> Delegation token"""
    # Workaround for HDFS-3988
    if self._security_enabled:
      self.get_home_dir()

    params = self._getparams()
    params['op'] = 'GETDELEGATIONTOKEN'
    params['renewer'] = renewer
    res = self._root.get(params=params)
    return res['Token']['urlString']


  def do_as_user(self, username, fn, *args, **kwargs):
    prev_user = self.user
    try:
      self.setuser(username)
      return fn(*args, **kwargs)
    finally:
      self.setuser(prev_user)


  def do_as_superuser(self, fn, *args, **kwargs):
    return self.do_as_user(self.superuser, fn, *args, **kwargs)


class File(object):
  """
  DEPRECATED!

  Represent an open file on HDFS. This exists to mirror the old thriftfs
  interface, for backwards compatibility only.
  """
  def __init__(self, fs, path, mode='r'):
    self._fs = fs
    self._path = normpath(path)
    self._pos = 0
    self._mode = mode

    try:
      self._stat = fs.stats(path)
      if self._stat.isDir:
        raise IOError(errno.EISDIR, _("Is a directory: '%s'") % path)
    except IOError, ex:
      if ex.errno == errno.ENOENT and 'w' in self._mode:
        self._fs.create(self._path)
        self.stat()
      else:
        raise ex

  def seek(self, offset, whence=0):
    """Set the file pointer to the given spot. @see file.seek"""
    if whence == SEEK_SET:
      self._pos = offset
    elif whence == SEEK_CUR:
      self._pos += offset
    elif whence == SEEK_END:
      self.stat()
      self._pos = self._fs.stats(self._path).size + offset
    else:
      raise IOError(errno.EINVAL, _("Invalid argument to seek for whence"))

  def stat(self):
    self._stat = self._fs.stats(self._path)
    return self._stat

  def tell(self):
    return self._pos

  def read(self, length=DEFAULT_READ_SIZE):
    data = self._fs.read(self._path, self._pos, length)
    self._pos += len(data)
    return data

  def write(self, data):
    """Append the data to the end of the file"""
    self.append(data)

  def append(self, data):
    if 'w' not in self._mode:
      raise IOError(errno.EINVAL, _("File not open for writing"))
    self._fs.append(self._path, data=data)

  def flush(self):
    pass

  def close(self):
    pass


def safe_octal(octal_value):
  """
  safe_octal(octal_value) -> octal value in string

  This correctly handles octal values specified as a string or as a numeric.
  """
  try:
    return oct(octal_value)
  except TypeError:
    return str(octal_value)


def _get_service_url(hdfs_config):
  override = hdfs_config.WEBHDFS_URL.get()
  if override:
    return override

  fs_defaultfs = hdfs_config.FS_DEFAULTFS.get()
  netloc = Hdfs.urlsplit(fs_defaultfs)[1]
  host = netloc.split(':')[0]
  port = hadoop.conf.DEFAULT_NN_HTTP_PORT
  return "http://%s:%s/webhdfs/v1" % (host, port)


def test_fs_configuration(fs_config):
  """
  This is a config validation method. Returns a list of
    [ (config_variable, error_message) ]
  """
  fs = WebHdfs.from_config(fs_config)
  fs.setuser(fs.superuser)

  # Access root
  try:
    statbuf = fs.stats('/')
    if statbuf.user != DEFAULT_HDFS_SUPERUSER:
      return [(fs_config.WEBHDFS_URL, _("Filesystem root '/' should be owned by 'hdfs'"))]
  except Exception, ex:
    LOG.info("%s -- Validation error: %s" % (fs, ex))
    return [(fs_config.WEBHDFS_URL, _('Failed to access filesystem root'))]

  # Write a file
  tmpname = fs.mktemp(prefix='hue_config_validation')
  try:
    fs.create(tmpname)
  except Exception, ex:
    LOG.info("%s -- Validation error: %s" % (fs, ex))
    return [(fs_config.WEBHDFS_URL,
            _('Failed to create temporary file "%s"') % tmpname)]

  # Check superuser has super power
  try:
    try:
      fs.chown(tmpname, fs.superuser)
    except Exception, ex:
      LOG.info("%s -- Validation error: %s" % (fs, ex))
      return [(fs_config.WEBHDFS_URL,
              'Failed to chown file. Please make sure that the filesystem root '
              'is owned by the cluster superuser ("hdfs" in most cases).')]
  finally:
    try:
      fs.remove(tmpname)
    except Exception, ex:
      LOG.error("Failed to remove '%s': %s" % (tmpname, ex))
      return [(fs_config.WEBHDFS_URL,
              _('Failed to remove temporary file "%s"') % tmpname)]

  return [ ]
