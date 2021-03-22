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
#
# Utilities for dealing with file modes.

from past.builtins import basestring
from builtins import object
import bz2
import os
import posixpath
import sys
import tarfile
import tempfile

from desktop.lib.exceptions_renderable import PopupException
from filebrowser.conf import ARCHIVE_UPLOAD_TEMPDIR
from zipfile import ZipFile

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


__all__ = ['archive_factory']


class Archive(object):
  """
  Acrchive interface.
  """
  def extract(self, path):
    """
    Extract an Archive.
    Should return a directory where the extracted contents live.
    """
    raise NotImplemented(_("Must implement 'extract' method."))

  def _create_dirs(self, basepath, dirs=[]):
    """
    Creates all directories passed at the given basepath.
    """
    for directory in dirs:
      # Stops if directory start with '/' or points to a relative path
      if os.path.isabs(directory) or '..' in directory:
        raise IllegalPathException()

      directory = os.path.join(basepath, directory)
      try:
        os.makedirs(directory)
      except OSError:
        pass

class ZipArchive(Archive):
  """
  Acts on a zip file in memory or in a temporary location.
  Python's ZipFile class inherently buffers all reading.
  """

  def __init__(self, file):
    if sys.version_info[0] > 2:
      self.file = isinstance(file, basestring) and file
    else:
      self.file = isinstance(file, basestring) and open(file) or file
    self.zfh = ZipFile(self.file)

  def extract(self):
    """
    Extracts a zip file.
    If a 'file' ends with '/', then it is a directory and we must create it.
    Else, open a file for writing and meta pipe the contents zipfile to the new file.
    """
    # Store all extracted files in a temporary directory.
    if ARCHIVE_UPLOAD_TEMPDIR.get():
      directory = tempfile.mkdtemp(dir=ARCHIVE_UPLOAD_TEMPDIR.get())
    else:
      directory = tempfile.mkdtemp()

    dirs, files = self._filenames()
    self._create_dirs(directory, dirs)
    self._create_files(directory, files)

    return directory

  def _filenames(self):
    """
    List all dirs and files by reading the table of contents of the Zipfile.
    """
    dirs = []
    files = []
    for name in self.zfh.namelist():
      if name.endswith(posixpath.sep):
        dirs.append(name)
      else:
        files.append(name)
        # self.zfh.namelist() sometimes doesn't return all the directories
        # Go up the path one directory at the time
        parent = os.path.dirname(name)
        while parent != '' and parent not in dirs:
          dirs.append(parent)
          parent = os.path.dirname(parent)
    return (dirs, files)

  def _create_files(self, basepath, files=[]):
    """
    Extract files to their rightful place.
    Files are written to a temporary directory immediately after being decompressed.
    """
    for f in files:
      new_path = os.path.join(basepath, f)
      new_file = open(new_path, 'w')
      zdata = self.zfh.read(f)
      if not isinstance(zdata, str):
        zdata = zdata.decode('utf-8')
      new_file.write(zdata)
      new_file.close()


class TarballArchive(Archive):
  """
  Acts on a tarball (tar.gz) file in memory or in a temporary location.
  Python's ZipFile class inherently buffers all reading.
  """
  def __init__(self, file):
    if isinstance(file, basestring):
      self.path = file
    else:
      f = tempfile.NamedTemporaryFile(delete=False)
      f.write(file.read())
      self.path = f.name
      f.close()
    self.fh = tarfile.open(self.path)

  def extract(self):
    """
    Extracts a zip file.
    If a 'file' ends with '/', then it is a directory and we must create it.
    Else, open a file for writing and meta pipe the contents zipfile to the new file.
    """
    # Store all extracted files in a temporary directory.
    directory = tempfile.mkdtemp()

    dirs, files = self._filenames()
    self._create_dirs(directory, dirs)
    self._create_files(directory, files)

    return directory

  def _filenames(self):
    """
    List all dirs and files by reading the table of contents of the Zipfile.
    """
    dirs = []
    files = []
    for tarinfo in self.fh.getmembers():
      if tarinfo.isdir():
        dirs.append(tarinfo.name)
      else:
        files.append(tarinfo.name)
        parent = os.path.dirname(tarinfo.path)
        # getmembers() sometimes doesn't return all the directories
        # Go up the path one directory at the time
        while parent != '' and parent not in dirs:
          dirs.append(parent)
          parent = os.path.dirname(parent)
    return (dirs, files)

  def _create_files(self, basepath, files=[]):
    """
    Extract files to their rightful place.
    Files are written to a temporary directory immediately after being decompressed.
    """
    for f in files:
      new_path = os.path.join(basepath, f)
      new_file = open(new_path, 'w')
      extracted_data = self.fh.extractfile(f).read()
      if not isinstance(extracted_data, str):
        extracted_data = extracted_data.decode('utf-8')
      new_file.write(extracted_data)
      new_file.close()


class BZ2Archive(Archive):
  """
  Acts on a bzip2 file in memory or in a temporary location.
  Python's BZ2File class inherently buffers all reading.
  """

  def __init__(self, file):
    # bzip2 only compresses single files and there is no direct method in the bz2 library to get the file name
    self.name = file.name[:-6] if file.name.lower().endswith('.bzip2') else file.name[:-4]

    if isinstance(file, basestring):
      self.path = file
    else:
      f = tempfile.NamedTemporaryFile(delete=False)
      f.write(file.read())
      self.path = f.name
      f.close()
    self.fh = bz2.BZ2File(self.path)

  def extract(self):
    """
    Extracts a bz2 file.
    Opens the file for writing and meta pipe the contents bz2file to the new file.
    """
    # Store all extracted files in a temporary directory.
    if ARCHIVE_UPLOAD_TEMPDIR.get():
      directory = tempfile.mkdtemp(dir=ARCHIVE_UPLOAD_TEMPDIR.get())
    else:
      directory = tempfile.mkdtemp()

    files = [self.name]
    self._create_files(directory, files)

    return directory

  def _create_files(self, basepath, files=[]):
    """
    Files are written to a temporary directory immediately after being decompressed.
    """
    for f in files:
      new_path = os.path.join(basepath, f)
      new_file = open(new_path, 'w')
      new_file.write(self.fh.read())
      new_file.close()


def archive_factory(path, archive_type='zip'):
  if archive_type == 'zip':
    return ZipArchive(path)
  elif archive_type == 'tarball' or archive_type == 'tar.gz' or archive_type == 'tgz':
    return TarballArchive(path)
  elif archive_type == 'bz2' or archive_type == 'bzip2':
    return BZ2Archive(path)

class IllegalPathException(PopupException):

  def __init__(self):
    super(IllegalPathException, self).__init__('''Archive path cannot be absolute or contain '..' ''')
