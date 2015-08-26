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
from __future__ import absolute_import

import os
import tempfile
import string

from nose.tools import assert_true, assert_false, assert_raises, eq_

from aws.s3 import join, parse_uri
from aws.s3.s3fs import S3FileSystem
from aws.s3.s3test_utils import S3TestBase, generate_id


class S3FSTest(S3TestBase):
  @classmethod
  def setUpClass(cls):
    S3TestBase.setUpClass()
    if not cls.shouldSkip():
      cls.fs = S3FileSystem(cls.s3_connection)

  def test_open(self):
    path = self.get_test_path('test_open.txt')

    with self.cleaning(path):
      assert_raises(IOError, self.fs.open, path)

      key = self.get_key(path)
      key.set_contents_from_string('Hello')

      fh1 = self.fs.open(path)
      eq_('He', fh1.read(length=2))

      fh2 = self.fs.open(path, mode='r')
      eq_('Hello', fh2.read())

      eq_('llo', fh1.read())

      assert_raises(Exception, self.fs.open, path, mode='w')
      assert_raises(Exception, self.fs.open, path, mode='?r')

  def test_read(self):
    path = self.get_test_path('test_read.txt')
    with self.cleaning(path):
      key = self.get_key(path)
      key.set_contents_from_string('Hello')

      eq_('Hel', self.fs.read(path, 0, 3))
      eq_('ell', self.fs.read(path, 1, 3))

  def test_isfile(self):
    pass

  def test_isdir(self):
    pass

  def test_exists(self):
    dir_path = self.get_test_path('test_exists')
    file_path = join(dir_path, 'file')

    assert_false(self.fs.exists(dir_path))
    assert_false(self.fs.exists(file_path))

    self.fs.create(file_path)

    assert_true(self.fs.exists(dir_path))
    assert_true(self.fs.exists(file_path))

    assert_true(self.fs.exists('s3://%s' % self.bucket_name))
    assert_true(self.fs.exists('s3://'))
    fake_bucket = 'fake%s' % generate_id(8, string.ascii_lowercase + string.digits)
    assert_false(self.fs.exists('s3://%s' % fake_bucket))

  def test_stats(self):
    assert_raises(ValueError, self.fs.stats, 'ftp://archive')
    not_exists = self.get_test_path('does_not_exist')
    assert_raises(IOError, self.fs.stats, not_exists)

    root_stat = self.fs.stats('s3://')
    eq_(True, root_stat.isDir)
    eq_('s3://', root_stat.path)

    bucket_stat = self.fs.stats('s3://%s' % self.bucket_name)
    eq_(True, bucket_stat.isDir)
    eq_('s3://%s' % self.bucket_name, bucket_stat.path)
    
  def test_copyfile(self):
    src_path = self.get_test_path('test_copy_file_src')
    dst_path = self.get_test_path('test_copy_file_dst')
    with self.cleaning(src_path, dst_path):
      data = "To boldly go where no one has gone before\n" * 2000
      self.fs.create(src_path, data=data)
      self.fs.create(dst_path, data="some initial data")

      self.fs.copyfile(src_path, dst_path)
      actual = self.fs.read(dst_path, 0, len(data) + 100)
      eq_(data, actual)

  def test_full_copy(self):
    src_path = self.get_test_path('test_full_copy_src')
    dst_path = self.get_test_path('test_full_copy_dst')

    src_file_path = join(src_path, 'file.txt')
    dst_file_path = join(dst_path, 'file.txt')

    with self.cleaning(src_path, dst_path):
      self.fs.mkdir(src_path)
      self.fs.mkdir(dst_path)

      data = "To boldly go where no one has gone before\n" * 2000
      self.fs.create(src_file_path, data=data)

      # File to directory copy.
      self.fs.copy(src_file_path, dst_path)
      assert_true(self.fs.exists(dst_file_path))

      # Directory to directory copy.
      self.fs.copy(src_path, dst_path, True)
      base_name = parse_uri(src_path)[2]
      dst_folder_path = join(dst_path, base_name)
      assert_true(self.fs.exists(dst_folder_path))
      assert_true(self.fs.exists(join(dst_folder_path, 'file.txt')))

      # Copy directory to file should fail.
      assert_raises(IOError, self.fs.copy, src_path, dst_file_path, True)

  def test_copy_remote_dir(self):
    src_dir = self.get_test_path('test_copy_remote_dir_src')
    dst_dir = self.get_test_path('test_copy_remote_dir_dst')

    with self.cleaning(src_dir, dst_dir):
      self.fs.mkdir(src_dir)

      self.fs.create(join(src_dir, 'file_one.txt'), data='foo')
      self.fs.create(join(src_dir, 'file_two.txt'), data='bar')

      self.fs.mkdir(dst_dir)
      self.fs.copy_remote_dir(src_dir, dst_dir)

      src_stat = self.fs.listdir_stats(src_dir)
      dst_stat = self.fs.listdir_stats(dst_dir)

      src_names = set([stat.name for stat in src_stat])
      dst_names = set([stat.name for stat in dst_stat])
      assert_true(src_names)
      eq_(src_names, dst_names)

  def test_copy_from_local(self):
    src_name = 'test_copy_from_local_src'
    src_path = os.path.join(tempfile.gettempdir(), src_name)
    dst_path = self.get_test_path('test_copy_from_local_dst')

    data = "To boldly go where no one has gone before\n" * 2000
    f = open(src_path, 'w')
    f.write(data)
    f.close()

    with self.cleaning(dst_path):
      self.fs.copyFromLocal(src_path, dst_path)
      actual = self.fs.read(dst_path, 0, len(data) + 100)
      eq_(data, actual)

  def test_rename_star(self):
    src_dir = self.get_test_path('test_rename_star_src')
    dst_dir = self.get_test_path('test_rename_star_dst')

    with self.cleaning(src_dir, dst_dir):
      self.fs.mkdir(src_dir)
      self.fs.create(join(src_dir, 'file_one.txt'), data='foo')
      self.fs.create(join(src_dir, 'file_two.txt'), data='bar')

      src_ls = self.fs.listdir(src_dir)
      eq_(2, len(src_ls))
      assert_true('file_one.txt' in src_ls)
      assert_true('file_two.txt' in src_ls)

      src_stat = self.fs.listdir_stats(src_dir)

      self.fs.mkdir(dst_dir)
      self.fs.rename_star(src_dir, dst_dir)

      dst_stat = self.fs.listdir_stats(dst_dir)

      src_names = set([stat.name for stat in src_stat])
      dst_names = set([stat.name for stat in dst_stat])
      assert_true(src_names)
      eq_(src_names, dst_names)

  def test_rmtree(self):
    assert_raises(NotImplementedError, self.fs.rmtree, 'universe', skipTrash=False)

    directory = self.get_test_path('test_rmtree')
    with self.cleaning(directory):
      self.fs.mkdir(directory)
      nested_dir = join(directory, 'nested_dir')
      self.fs.mkdir(nested_dir)
      file_path = join(nested_dir, 'file')
      key = self.get_key(file_path)
      key.set_contents_from_string('Some content')

      self.fs.rmtree(directory, skipTrash=True)

      assert_false(self.fs.exists(file_path))
      assert_false(self.fs.exists(nested_dir))
      assert_false(self.fs.exists(directory))

  def test_listing_buckets(self):
    buckets = self.fs.listdir('s3://')
    assert_true(len(buckets) > 0)






