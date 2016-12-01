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

import json
import os
import tempfile
import string

from django.contrib.auth.models import User
from nose.tools import assert_equal, assert_false, assert_true, assert_raises, eq_

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_to_group
from desktop.lib.test_utils import grant_access, add_to_group, add_permission, remove_from_group

from aws.s3 import join, parse_uri
from aws.s3.s3fs import S3FileSystem, S3FileSystemException
from aws.s3.s3test_utils import S3TestBase, generate_id
from aws.s3.upload import DEFAULT_WRITE_SIZE


class S3FSTest(S3TestBase):

  @classmethod
  def setUpClass(cls):
    S3TestBase.setUpClass()
    if not cls.shouldSkip():
      cls.fs = S3FileSystem(cls.s3_connection)

      cls.c = make_logged_in_client(username='test', is_superuser=False)
      grant_access('test', 'test', 'filebrowser')
      add_to_group('test')
      cls.user = User.objects.get(username="test")


  def test_open(self):
    path = self.get_test_path('test_open.txt')

    with self.cleaning(path):
      assert_raises(S3FileSystemException, self.fs.open, path)

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

    assert_true(self.fs.exists('s3a://%s' % self.bucket_name))
    assert_true(self.fs.exists('s3a://'))
    fake_bucket = 'fake%s' % generate_id(8, string.ascii_lowercase + string.digits)
    assert_false(self.fs.exists('s3a://%s' % fake_bucket))


  def test_stats(self):
    assert_raises(ValueError, self.fs.stats, 'ftp://archive')
    not_exists = self.get_test_path('does_not_exist')
    assert_raises(S3FileSystemException, self.fs.stats, not_exists)

    root_stat = self.fs.stats('s3a://')
    eq_(True, root_stat.isDir)
    eq_('s3a://', root_stat.path)

    bucket_stat = self.fs.stats('s3a://%s' % self.bucket_name)
    eq_(True, bucket_stat.isDir)
    eq_('s3a://%s' % self.bucket_name, bucket_stat.path)


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
      assert_raises(S3FileSystemException, self.fs.copy, src_path, dst_file_path, True)


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


  def test_rename_dir(self):
    src_dir = self.get_test_path('test_rename_dir_src')
    dst_dir = self.get_test_path('test_rename_dir_dst')

    with self.cleaning(src_dir, dst_dir):
      self.fs.mkdir(src_dir)
      self.fs.create(join(src_dir, 'file_one.txt'), data='foo')
      self.fs.create(join(src_dir, 'file_two.txt'), data='bar')

      src_ls = self.fs.listdir(src_dir)
      eq_(2, len(src_ls))
      assert_true('file_one.txt' in src_ls)
      assert_true('file_two.txt' in src_ls)

      # Assert that no directories with dst_dir name exist yet
      assert_false(self.fs.exists(dst_dir))

      # Rename src to dst
      self.fs.rename(src_dir, dst_dir)
      assert_true(self.fs.exists(dst_dir))
      assert_false(self.fs.exists(src_dir))

      dst_ls = self.fs.listdir(dst_dir)
      eq_(2, len(dst_ls))
      assert_true('file_one.txt' in dst_ls)
      assert_true('file_two.txt' in dst_ls)

      # Assert that the children files are not duplicated at top-level destination
      bucket_ls = self.bucket.list()
      assert_false('file_one.txt' in bucket_ls)
      assert_false('file_two.txt' in bucket_ls)

      # Assert that only the renamed directory, and not an empty file, exists
      assert_equal(1, len([key for key in bucket_ls if key.name.strip('/') == self.get_key(dst_dir).name.strip('/')]))


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
    buckets = self.fs.listdir('s3a://')
    assert_true(len(buckets) > 0)


  def test_mkdir(self):
    dir_path = self.get_test_path('test_mkdir')
    assert_false(self.fs.exists(dir_path))
    
    self.fs.mkdir(dir_path)
    assert_true(self.fs.exists(dir_path))


  def test_upload_file(self):
    with tempfile.NamedTemporaryFile() as local_file:
      # Make sure we can upload larger than the UPLOAD chunk size
      file_size = DEFAULT_WRITE_SIZE * 2
      local_file.write('0' * file_size)
      local_file.flush()

      dest_dir = self.get_test_path('test_upload')
      local_file = local_file.name
      dest_path = '%s/%s' % (dest_dir, os.path.basename(local_file))

      add_permission(self.user.username, 'has_s3', permname='s3_access', appname='filebrowser')
      try:
        # Just upload the current python file
        resp = self.c.post('/filebrowser/upload/file?dest=%s' % dest_dir, dict(dest=dest_dir, hdfs_file=file(local_file)))
        response = json.loads(resp.content)
      finally:
        remove_from_group(self.user.username, 'has_s3')

      assert_equal(0, response['status'], response)
      stats = self.fs.stats(dest_path)

      f = self.fs.open(dest_path)
      actual = f.read(file_size)
      expected = file(local_file).read()
      assert_equal(actual, expected, 'files do not match: %s != %s' % (len(actual), len(expected)))


  def test_check_access(self):
    dir_path = self.get_test_path('test_check_access')
    self.fs.mkdir(dir_path)

    assert_true(self.fs.check_access(dir_path, permission='WRITE'))
