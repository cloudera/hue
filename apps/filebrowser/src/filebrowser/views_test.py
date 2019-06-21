# -*- coding: utf-8 -*-
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
#!/usr/bin/env python

import json
import logging
import os
import re
import tempfile
import urllib
import urlparse
from avro import schema, datafile, io

from aws.s3.s3fs import S3FileSystemException
from aws.s3.s3test_utils import get_test_bucket
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.encoding import smart_str
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal, assert_raises

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_to_group, add_permission, remove_from_group
from hadoop import pseudo_hdfs4
from hadoop.conf import UPLOAD_CHUNK_SIZE
from filebrowser.conf import ENABLE_EXTRACT_UPLOADED_ARCHIVE
from desktop.lib.view_util import location_to_url

from conf import MAX_SNAPPY_DECOMPRESSION_SIZE
from lib.rwx import expand_mode
from views import snappy_installed


LOG = logging.getLogger(__name__)


def cleanup_tree(cluster, path):
  try:
    cluster.fs.rmtree(path)
  except:
    # Don't let cleanup errors mask earlier failures
    LOG.exception('failed to cleanup %s' % path)

def cleanup_file(cluster, path):
  try:
    cluster.fs.remove(path)
  except:
    # Don't let cleanup errors mask earlier failures
    LOG.exception('failed to cleanup %s' % path)


class TestFileBrowserWithHadoop(object):
  requires_hadoop = True
  integration = True

  def setUp(self):
    self.c = make_logged_in_client(username='test', is_superuser=False)
    grant_access('test', 'test', 'filebrowser')
    add_to_group('test')
    self.user = User.objects.get(username='test')

    self.cluster = pseudo_hdfs4.shared_cluster()
    self.cluster.fs.setuser('test')
    self.prefix = self.cluster.fs_prefix + '/filebrowser'
    self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/test')

  def tearDown(self):
    cleanup_tree(self.cluster, self.prefix)
    assert_false(self.cluster.fs.exists(self.prefix))
    self.cluster.fs.setuser('test')

  def test_remove(self):
    prefix = self.prefix + '/test-delete'

    PATH_1 = '%s/1' % prefix
    PATH_2 = '%s/2' % prefix
    PATH_3 = '%s/3' % prefix
    self.cluster.fs.mkdir(prefix)
    self.cluster.fs.mkdir(PATH_1)
    self.cluster.fs.mkdir(PATH_2)
    self.cluster.fs.mkdir(PATH_3)

    assert_true(self.cluster.fs.exists(PATH_1))
    assert_true(self.cluster.fs.exists(PATH_2))
    assert_true(self.cluster.fs.exists(PATH_3))

    self.c.post('/filebrowser/rmtree', dict(path=[PATH_1]))
    assert_false(self.cluster.fs.exists(PATH_1))
    assert_true(self.cluster.fs.exists(PATH_2))
    assert_true(self.cluster.fs.exists(PATH_3))

    self.c.post('/filebrowser/rmtree', dict(path=[PATH_2, PATH_3]))
    assert_false(self.cluster.fs.exists(PATH_1))
    assert_false(self.cluster.fs.exists(PATH_2))
    assert_false(self.cluster.fs.exists(PATH_3))


  def test_move(self):
    prefix = self.cluster.fs_prefix + '/test-move'

    PATH_1 = '%s/1' % prefix
    PATH_2 = '%s/2' % prefix
    SUB_PATH1_1 = '%s/1' % PATH_1
    SUB_PATH1_2 = '%s/2' % PATH_1
    SUB_PATH1_3 = '%s/3' % PATH_1
    SUB_PATH2_1 = '%s/1' % PATH_2
    SUB_PATH2_2 = '%s/2' % PATH_2
    SUB_PATH2_3 = '%s/3' % PATH_2
    self.cluster.fs.mkdir(prefix)
    self.cluster.fs.mkdir(PATH_1)
    self.cluster.fs.mkdir(PATH_2)
    self.cluster.fs.mkdir(SUB_PATH1_1)
    self.cluster.fs.mkdir(SUB_PATH1_2)
    self.cluster.fs.mkdir(SUB_PATH1_3)

    assert_true(self.cluster.fs.exists(SUB_PATH1_1))
    assert_true(self.cluster.fs.exists(SUB_PATH1_2))
    assert_true(self.cluster.fs.exists(SUB_PATH1_3))
    assert_false(self.cluster.fs.exists(SUB_PATH2_1))
    assert_false(self.cluster.fs.exists(SUB_PATH2_2))
    assert_false(self.cluster.fs.exists(SUB_PATH2_3))

    self.c.post('/filebrowser/move', dict(src_path=[SUB_PATH1_1], dest_path=PATH_2))
    assert_false(self.cluster.fs.exists(SUB_PATH1_1))
    assert_true(self.cluster.fs.exists(SUB_PATH1_2))
    assert_true(self.cluster.fs.exists(SUB_PATH1_3))
    assert_true(self.cluster.fs.exists(SUB_PATH2_1))
    assert_false(self.cluster.fs.exists(SUB_PATH2_2))
    assert_false(self.cluster.fs.exists(SUB_PATH2_3))

    self.c.post('/filebrowser/move', dict(src_path=[SUB_PATH1_2, SUB_PATH1_3], dest_path=PATH_2))
    assert_false(self.cluster.fs.exists(SUB_PATH1_1))
    assert_false(self.cluster.fs.exists(SUB_PATH1_2))
    assert_false(self.cluster.fs.exists(SUB_PATH1_3))
    assert_true(self.cluster.fs.exists(SUB_PATH2_1))
    assert_true(self.cluster.fs.exists(SUB_PATH2_2))
    assert_true(self.cluster.fs.exists(SUB_PATH2_3))

    response = self.c.post('/filebrowser/move', dict(src_path=[SUB_PATH1_2, SUB_PATH1_3], dest_path=SUB_PATH1_2))
    assert_equal(500, response.status_code)

  def test_copy(self):
    prefix = self.cluster.fs_prefix + '/test-copy'

    PATH_1 = '%s/1' % prefix
    PATH_2 = '%s/2' % prefix
    SUB_PATH1_1 = '%s/1' % PATH_1
    SUB_PATH1_2 = '%s/2' % PATH_1
    SUB_PATH1_3 = '%s/3' % PATH_1
    SUB_PATH2_1 = '%s/1' % PATH_2
    SUB_PATH2_2 = '%s/2' % PATH_2
    SUB_PATH2_3 = '%s/3' % PATH_2
    self.cluster.fs.mkdir(prefix)
    self.cluster.fs.mkdir(PATH_1)
    self.cluster.fs.mkdir(PATH_2)
    self.cluster.fs.mkdir(SUB_PATH1_1)
    self.cluster.fs.mkdir(SUB_PATH1_2)
    self.cluster.fs.mkdir(SUB_PATH1_3)

    assert_true(self.cluster.fs.exists(SUB_PATH1_1))
    assert_true(self.cluster.fs.exists(SUB_PATH1_2))
    assert_true(self.cluster.fs.exists(SUB_PATH1_3))
    assert_false(self.cluster.fs.exists(SUB_PATH2_1))
    assert_false(self.cluster.fs.exists(SUB_PATH2_2))
    assert_false(self.cluster.fs.exists(SUB_PATH2_3))

    self.c.post('/filebrowser/copy', dict(src_path=[SUB_PATH1_1], dest_path=PATH_2))
    assert_true(self.cluster.fs.exists(SUB_PATH1_1))
    assert_true(self.cluster.fs.exists(SUB_PATH1_2))
    assert_true(self.cluster.fs.exists(SUB_PATH1_3))
    assert_true(self.cluster.fs.exists(SUB_PATH2_1))
    assert_false(self.cluster.fs.exists(SUB_PATH2_2))
    assert_false(self.cluster.fs.exists(SUB_PATH2_3))

    self.c.post('/filebrowser/copy', dict(src_path=[SUB_PATH1_2, SUB_PATH1_3], dest_path=PATH_2))
    assert_true(self.cluster.fs.exists(SUB_PATH1_1))
    assert_true(self.cluster.fs.exists(SUB_PATH1_2))
    assert_true(self.cluster.fs.exists(SUB_PATH1_3))
    assert_true(self.cluster.fs.exists(SUB_PATH2_1))
    assert_true(self.cluster.fs.exists(SUB_PATH2_2))
    assert_true(self.cluster.fs.exists(SUB_PATH2_3))


  def test_mkdir_singledir(self):
    prefix = self.cluster.fs_prefix + '/test-filebrowser-mkdir'

    # We test that mkdir fails when a non-relative path is provided and a multi-level path is provided.
    success_path = 'mkdir_singledir'
    path_absolute = '/mkdir_singledir'
    path_fail = 'fail/foo'
    path_other_failure = 'fail#bar'

    # Two of the following post requests should throw exceptions.
    # See https://issues.cloudera.org/browse/HUE-793.
    self.c.post('/filebrowser/mkdir', dict(path=prefix, name=path_fail))
    self.c.post('/filebrowser/mkdir', dict(path=prefix, name=path_other_failure))
    self.c.post('/filebrowser/mkdir', dict(path=prefix, name=path_absolute))
    self.c.post('/filebrowser/mkdir', dict(path=prefix, name=success_path))

    # Read the parent dir and make sure we created 'success_path' only.
    response = self.c.get('/filebrowser/view=' + prefix)
    dir_listing = response.context[0]['files']
    assert_equal(3, len(dir_listing))
    assert_equal(dir_listing[2]['name'], success_path)


  def test_touch(self):
    prefix = self.cluster.fs_prefix + '/test-filebrowser-touch'

    success_path = 'touch_file'
    path_absolute = '/touch_file'
    path_fail = 'touch_fail/file'

    self.cluster.fs.mkdir(prefix)

    resp = self.c.post('/filebrowser/touch', dict(path=prefix, name=path_fail))
    assert_equal(500, resp.status_code)
    resp = self.c.post('/filebrowser/touch', dict(path=prefix, name=path_absolute))
    assert_equal(500, resp.status_code)
    resp = self.c.post('/filebrowser/touch', dict(path=prefix, name=success_path))
    assert_equal(200, resp.status_code)

    # Read the parent dir and make sure we created 'success_path' only.
    response = self.c.get('/filebrowser/view=' + prefix)
    file_listing = response.context[0]['files']
    assert_equal(3, len(file_listing))
    assert_equal(file_listing[2]['name'], success_path)


  def test_chmod(self):
    prefix = self.cluster.fs_prefix + '/test_chmod'

    PATH = "%s/chmod_test" % prefix
    SUBPATH = PATH + '/test'
    self.cluster.fs.mkdir(SUBPATH)

    permissions = ('user_read', 'user_write', 'user_execute',
        'group_read', 'group_write', 'group_execute',
        'other_read', 'other_write', 'other_execute',
        'sticky') # Order matters!

    # Get current mode, change mode, check mode
    # Start with checking current mode
    assert_not_equal(041777, int(self.cluster.fs.stats(PATH)["mode"]))

    # Setup post data
    permissions_dict = dict( zip(permissions, [True]*len(permissions)) )
    kwargs = {'path': [PATH]}
    kwargs.update(permissions_dict)

    # Set 1777, then check permissions of dirs
    response = self.c.post("/filebrowser/chmod", kwargs)
    assert_equal(041777, int(self.cluster.fs.stats(PATH)["mode"]))

    # Now do the above recursively
    assert_not_equal(041777, int(self.cluster.fs.stats(SUBPATH)["mode"]))
    kwargs['recursive'] = True
    response = self.c.post("/filebrowser/chmod", kwargs)
    assert_equal(041777, int(self.cluster.fs.stats(SUBPATH)["mode"]))

    # Test bulk chmod
    PATH_2 = "%s/test-chmod2" % prefix
    PATH_3 = "%s/test-chown3" % prefix
    self.cluster.fs.mkdir(PATH_2)
    self.cluster.fs.mkdir(PATH_3)
    kwargs['path'] = [PATH_2, PATH_3]
    assert_not_equal(041777, int(self.cluster.fs.stats(PATH_2)["mode"]))
    assert_not_equal(041777, int(self.cluster.fs.stats(PATH_3)["mode"]))
    self.c.post("/filebrowser/chmod", kwargs)
    assert_equal(041777, int(self.cluster.fs.stats(PATH_2)["mode"]))
    assert_equal(041777, int(self.cluster.fs.stats(PATH_3)["mode"]))


  def test_chmod_sticky(self):
    prefix = self.cluster.fs_prefix + '/test_chmod_sticky'

    PATH = "%s/chmod_test" % prefix
    self.cluster.fs.mkdir(PATH)

    # Get current mode and make sure sticky bit is off
    mode = expand_mode( int(self.cluster.fs.stats(PATH)["mode"]) )
    assert_equal(False, mode[-1])

    # Setup post data
    permissions = ('user_read', 'user_write', 'user_execute',
        'group_read', 'group_write', 'group_execute',
        'other_read', 'other_write', 'other_execute',
        'sticky') # Order matters!
    permissions_dict = dict(filter(lambda x: x[1], zip(permissions, mode)))
    permissions_dict['sticky'] = True
    kwargs = {'path': [PATH]}
    kwargs.update(permissions_dict)

    # Set sticky bit, then check sticky bit is on in hdfs
    response = self.c.post("/filebrowser/chmod", kwargs)
    mode = expand_mode( int(self.cluster.fs.stats(PATH)["mode"]) )
    assert_equal(True, mode[-1])

    # Unset sticky bit, then check sticky bit is off in hdfs
    del kwargs['sticky']
    response = self.c.post("/filebrowser/chmod", kwargs)
    mode = expand_mode( int(self.cluster.fs.stats(PATH)["mode"]) )
    assert_equal(False, mode[-1])


  def test_chown(self):
    prefix = self.cluster.fs_prefix + '/test_chown'
    self.cluster.fs.mkdir(prefix)

    # Login as Non Hadoop superuser
    response = self.c.post(reverse('index'))
    assert_false('Change owner' in response.content)

    # Only the Hadoop superuser really has carte blanche here
    c2 = make_logged_in_client(self.cluster.superuser)
    self.cluster.fs.setuser(self.cluster.superuser)

    PATH = u"%s/test-chown-en-Español" % prefix
    self.cluster.fs.mkdir(PATH)
    c2.post("/filebrowser/chown", dict(path=[PATH], user="x", group="y"))
    assert_equal("x", self.cluster.fs.stats(PATH)["user"])
    assert_equal("y", self.cluster.fs.stats(PATH)["group"])
    c2.post("/filebrowser/chown", dict(path=[PATH], user="__other__", user_other="z", group="y"))
    assert_equal("z", self.cluster.fs.stats(PATH)["user"])

    # Now check recursive
    SUBPATH = PATH + '/test'
    self.cluster.fs.mkdir(SUBPATH)
    c2.post("/filebrowser/chown", dict(path=[PATH], user="x", group="y", recursive=True))
    assert_equal("x", self.cluster.fs.stats(SUBPATH)["user"])
    assert_equal("y", self.cluster.fs.stats(SUBPATH)["group"])
    c2.post("/filebrowser/chown", dict(path=[PATH], user="__other__", user_other="z", group="y", recursive=True))
    assert_equal("z", self.cluster.fs.stats(SUBPATH)["user"])

    # Test bulk chown
    PATH_2 = u"/test-chown-en-Español2"
    PATH_3 = u"/test-chown-en-Español2"
    self.cluster.fs.mkdir(PATH_2)
    self.cluster.fs.mkdir(PATH_3)
    c2.post("/filebrowser/chown", dict(path=[PATH_2, PATH_3], user="x", group="y", recursive=True))
    assert_equal("x", self.cluster.fs.stats(PATH_2)["user"])
    assert_equal("y", self.cluster.fs.stats(PATH_2)["group"])
    assert_equal("x", self.cluster.fs.stats(PATH_3)["user"])
    assert_equal("y", self.cluster.fs.stats(PATH_3)["group"])


  def test_rename(self):
    prefix = self.cluster.fs_prefix + '/test_rename'
    self.cluster.fs.mkdir(prefix)

    PREFIX = u"%s/test-rename/" % prefix
    NAME = u"test-rename-before"
    NEW_NAME = u"test-rename-after"
    self.cluster.fs.mkdir(PREFIX + NAME)
    op = "rename"
    # test for full path rename
    self.c.post("/filebrowser/rename", dict(src_path=PREFIX + NAME, dest_path=PREFIX + NEW_NAME))
    assert_true(self.cluster.fs.exists(PREFIX + NEW_NAME))
    # test for smart rename
    self.c.post("/filebrowser/rename", dict(src_path=PREFIX + NAME, dest_path=NEW_NAME))
    assert_true(self.cluster.fs.exists(PREFIX + NEW_NAME))


  def test_listdir(self):
    # Delete user's home if there's already something there
    home = self.cluster.fs.do_as_user('test', self.cluster.fs.get_home_dir)
    if self.cluster.fs.exists(home):
      self.cluster.fs.do_as_superuser(self.cluster.fs.rmtree, home)

    response = self.c.get('/filebrowser/')
    # Since we deleted the home directory... home_directory context should be None.
    assert_false(response.context[0]['home_directory'], response.context[0]['home_directory'])

    self.cluster.fs.do_as_superuser(self.cluster.fs.mkdir, home)
    self.cluster.fs.do_as_superuser(self.cluster.fs.chown, home, 'test', 'test')

    # These paths contain non-ascii characters. Your editor will need the
    # corresponding font library to display them correctly.
    #
    # We test that mkdir can handle unicode strings as well as byte strings.
    # And even when the byte string can't be decoded properly (big5), the listdir
    # still succeeds.
    orig_paths = [
      u'greek-Ελληνικά',
      u'chinese-漢語',
    ]

    prefix = home + '/test-filebrowser/'
    for path in orig_paths:
      self.c.post('/filebrowser/mkdir', dict(path=prefix, name=path))

    # Read the parent dir
    response = self.c.get('/filebrowser/view=' + prefix)

    dir_listing = response.context[0]['files']
    assert_equal(len(orig_paths) + 2, len(dir_listing))

    for dirent in dir_listing:
      path = dirent['name']
      if path in ('.', '..'):
        continue

      assert_true(path in orig_paths)

      # Drill down into the subdirectory
      url = urlparse.urlsplit(dirent['url'])[2]
      resp = self.c.get(url)

      # We are actually reading a directory
      assert_equal('.', resp.context[0]['files'][1]['name'])
      assert_equal('..', resp.context[0]['files'][0]['name'])

    # Test's home directory now exists. Should be returned.
    response = self.c.get('/filebrowser/view=' + prefix)
    assert_equal(response.context[0]['home_directory'], home)

    # Test URL conflicts with filenames
    stat_dir = '%sstat/dir' % prefix
    self.cluster.fs.do_as_user('test', self.cluster.fs.mkdir, stat_dir)
    response = self.c.get('/filebrowser/view=%s' % stat_dir)
    assert_equal(stat_dir, response.context[0]['path'])

    response = self.c.get('/filebrowser/view=/test-filebrowser/?default_to_home')
    assert_true(re.search('%s$' % home, urllib.unquote(response['Location'])))

    # Test path relative to home directory
    self.cluster.fs.do_as_user('test', self.cluster.fs.mkdir, '%s/test_dir' % home)
    response = self.c.get('/filebrowser/home_relative_view=/test_dir')
    assert_equal('%s/test_dir' % home, response.context[0]['path'])


  def test_listdir_sort_and_filter(self):
    prefix = self.cluster.fs_prefix + '/test_rename'
    self.cluster.fs.mkdir(prefix)

    BASE = '%s/test_sort_and_filter' % prefix
    FUNNY_NAME = u'greek-Ελληνικά'

    self.cluster.fs.mkdir(BASE)
    # Create 10 files
    for i in range(1, 11):
      self.cluster.fs.create(self.cluster.fs.join(BASE, str(i)), data="foo" * i)

    # Create 1 funny name directory
    self.cluster.fs.mkdir(self.cluster.fs.join(BASE, FUNNY_NAME))

    # All 12 of the entries
    expect = [ '..', '.', FUNNY_NAME] + [ str(i) for i in range(1, 11) ]

    # Check pagination
    listing = self.c.get('/filebrowser/view=' + BASE + '?pagesize=20').context[0]['files']
    assert_equal(len(expect), len(listing))

    listing = self.c.get('/filebrowser/view=' + BASE + '?pagesize=10').context[0]['files']
    assert_equal(12, len(listing))

    listing = self.c.get('/filebrowser/view=' + BASE + '?pagesize=10&pagenum=1').context[0]['files']
    assert_equal(12, len(listing))

    listing = self.c.get('/filebrowser/view=' + BASE + '?pagesize=10&pagenum=2').context[0]['files']
    assert_equal(3, len(listing))

    # Check sorting (name)
    listing = self.c.get('/filebrowser/view=' + BASE + '?sortby=name').context[0]['files']
    assert_equal(sorted(expect[2:]), [ f['name'] for f in listing ][2:])

    listing = self.c.get('/filebrowser/view=' + BASE + '?sortby=name&descending=false').context[0]['files']
    assert_equal(sorted(expect[2:]), [ f['name'] for f in listing ][2:])

    listing = self.c.get('/filebrowser/view=' + BASE + '?sortby=name&descending=true').context[0]['files']
    assert_equal(".", listing[1]['name'])
    assert_equal("..", listing[0]['name'])
    assert_equal(FUNNY_NAME, listing[2]['name'])

    # Check sorting (size)
    listing = self.c.get('/filebrowser/view=' + BASE + '?sortby=size').context[0]['files']
    assert_equal(expect, [ f['name'] for f in listing ])

    # Check sorting (mtime)
    listing = self.c.get('/filebrowser/view=' + BASE + '?sortby=mtime').context[0]['files']
    assert_equal(".", listing[1]['name'])
    assert_equal("..", listing[0]['name'])
    assert_equal(FUNNY_NAME, listing[-1]['name'])

    # Check filter
    listing = self.c.get('/filebrowser/view=' + BASE + '?filter=1').context[0]['files']
    assert_equal(['..', '.', '1', '10'], [ f['name'] for f in listing ])

    listing = self.c.get('/filebrowser/view=' + BASE + '?filter=' + FUNNY_NAME).context[0]['files']
    assert_equal(['..', '.', FUNNY_NAME], [ f['name'] for f in listing ])

    # Check filter + sorting
    listing = self.c.get('/filebrowser/view=' + BASE + '?filter=1&sortby=name&descending=true').context[0]['files']
    assert_equal(['..', '.', '10', '1'], [ f['name'] for f in listing ])

    # Check filter + sorting + pagination
    listing = self.c.get('/filebrowser/view=' + BASE + '?filter=1&sortby=name&descending=true&pagesize=1&pagenum=2').context[0]['files']
    assert_equal(['..', '.', '1'], [ f['name'] for f in listing ])

    # Check filter with empty results
    resp = self.c.get('/filebrowser/view=' + BASE + '?filter=empty&sortby=name&descending=true&pagesize=1&pagenum=2')
    listing = resp.context[0]['files']
    assert_equal([], listing)
    page = resp.context[0]['page']
    assert_equal({}, page)


  def test_view_snappy_compressed(self):
    if not snappy_installed():
      raise SkipTest
    import snappy

    cluster = pseudo_hdfs4.shared_cluster()
    finish = []
    try:
      prefix = self.cluster.fs_prefix + '/test_view_snappy_compressed'
      self.cluster.fs.mkdir(prefix)

      f = cluster.fs.open(prefix + '/test-view.snappy', "w")
      f.write(snappy.compress('This is a test of the emergency broadcasting system.'))
      f.close()

      f = cluster.fs.open(prefix + '/test-view.stillsnappy', "w")
      f.write(snappy.compress('The broadcasters of your area in voluntary cooperation with the FCC and other authorities.'))
      f.close()

      f = cluster.fs.open(prefix + '/test-view.notsnappy', "w")
      f.write('foobar')
      f.close()

      # Snappy compressed fail
      response = self.c.get('/filebrowser/view=%s/test-view.notsnappy?compression=snappy' % prefix)
      assert_true('Failed to decompress' in response.context[0]['message'], response)

      # Snappy compressed succeed
      response = self.c.get('/filebrowser/view=%s/test-view.snappy' % prefix)
      assert_equal('snappy', response.context[0]['view']['compression'])
      assert_equal(response.context[0]['view']['contents'], 'This is a test of the emergency broadcasting system.', response)

      # Snappy compressed succeed
      response = self.c.get('/filebrowser/view=%s/test-view.stillsnappy' % prefix)
      assert_equal('snappy', response.context[0]['view']['compression'])
      assert_equal(response.context[0]['view']['contents'], 'The broadcasters of your area in voluntary cooperation with the FCC and other authorities.', response)

      # Largest snappy compressed file
      finish.append( MAX_SNAPPY_DECOMPRESSION_SIZE.set_for_testing(1) )
      response = self.c.get('/filebrowser/view=%s/test-view.stillsnappy?compression=snappy' % prefix)
      assert_true('File size is greater than allowed max snappy decompression size of 1' in response.context[0]['message'], response)

    finally:
      for done in finish:
        done()


  def test_view_snappy_compressed_avro(self):
    if not snappy_installed():
      raise SkipTest
    import snappy

    finish = []
    try:
      prefix = self.cluster.fs_prefix + '/test-snappy-avro-filebrowser'
      self.cluster.fs.mkdir(prefix)

      test_schema = schema.parse("""
        {
          "name": "test",
          "type": "record",
          "fields": [
            { "name": "name", "type": "string" },
            { "name": "integer", "type": "int" }
          ]
        }
      """)

      # Cannot use StringIO with datafile writer!
      f = self.cluster.fs.open(prefix +'/test-view.compressed.avro', "w")
      data_file_writer = datafile.DataFileWriter(f, io.DatumWriter(),
                                                  writers_schema=test_schema,
                                                  codec='snappy')
      dummy_datum = {
        'name': 'Test',
        'integer': 10,
      }
      data_file_writer.append(dummy_datum)
      data_file_writer.close()
      f.close()

      # Check to see if snappy is the codec
      f = self.cluster.fs.open(prefix + '/test-view.compressed.avro', "r")
      assert_true('snappy' in f.read())
      f.close()

      # Snappy compressed succeed
      response = self.c.get('/filebrowser/view=%s/test-view.compressed.avro' % prefix)
      assert_equal('avro', response.context[0]['view']['compression'])
      assert_equal(eval(response.context[0]['view']['contents']), dummy_datum, response)

    finally:
      for done in finish:
        done()


  def test_view_avro(self):
    prefix = self.cluster.fs_prefix + '/test_view_avro'
    self.cluster.fs.mkdir(prefix)

    test_schema = schema.parse("""
      {
        "name": "test",
        "type": "record",
        "fields": [
          { "name": "name", "type": "string" },
          { "name": "integer", "type": "int" }
        ]
      }
    """)

    f = self.cluster.fs.open(prefix + '/test-view.avro', "w")
    data_file_writer = datafile.DataFileWriter(f, io.DatumWriter(),
                                                writers_schema=test_schema,
                                                codec='deflate')
    dummy_datum = {
      'name': 'Test',
      'integer': 10,
    }
    data_file_writer.append(dummy_datum)
    data_file_writer.close()

    # autodetect
    response = self.c.get('/filebrowser/view=%s/test-view.avro' % prefix)
    # (Note: we use eval here cause of an incompatibility issue between
    # the representation string of JSON dicts in simplejson vs. json)
    assert_equal(eval(response.context[0]['view']['contents']), dummy_datum)

    # offsetting should work as well
    response = self.c.get('/filebrowser/view=%s/test-view.avro?offset=1' % prefix)
    assert_equal('avro', response.context[0]['view']['compression'])

    f = self.cluster.fs.open(prefix + '/test-view2.avro', "w")
    f.write("hello")
    f.close()

    # we shouldn't autodetect non avro files
    response = self.c.get('/filebrowser/view=%s/test-view2.avro' % prefix)
    assert_equal(response.context[0]['view']['contents'], "hello")

    # we should fail to do a bad thing if they specify compression when it's not set.
    response = self.c.get('/filebrowser/view=%s/test-view2.avro?compression=gzip' % prefix)
    assert_true('Failed to decompress' in response.context[0]['message'])


  def test_view_parquet(self):
    prefix = self.cluster.fs_prefix + '/test_view_parquet'
    self.cluster.fs.mkdir(prefix)

    # Parquet file encoded as hex.
    test_data = "50415231150015d40115d4012c15321500150615080000020000003201000000000100000002000000030000000400000005000000060000000700000008000000090000000a0000000b0000000c0000000d0000000e0000000f000000100000001100000012000000130000001400000015000000160000001700000018000000150015b60415b6042c1532150015061508000002000000320107000000414c474552494109000000415247454e54494e41060000004252415a494c0600000043414e41444105000000454759505408000000455448494f504941060000004652414e4345070000004745524d414e5905000000494e44494109000000494e444f4e45534941040000004952414e0400000049524151050000004a4150414e060000004a4f5244414e050000004b454e5941070000004d4f524f43434f0a0000004d4f5a414d42495155450400000050455255050000004348494e4107000000524f4d414e49410c00000053415544492041524142494107000000564945544e414d060000005255535349410e000000554e49544544204b494e47444f4d0d000000554e4954454420535441544553150015d40115d4012c1532150015061508000002000000320100000000010000000100000001000000040000000000000003000000030000000200000002000000040000000400000002000000040000000000000000000000000000000100000002000000030000000400000002000000030000000300000001000000150015d61e15d61e2c153215001506150800000200000032013300000020686167676c652e206361726566756c6c792066696e616c206465706f736974732064657465637420736c796c7920616761694c000000616c20666f7865732070726f6d69736520736c796c79206163636f7264696e6720746f2074686520726567756c6172206163636f756e74732e20626f6c6420726571756573747320616c6f6e6b0000007920616c6f6e6773696465206f66207468652070656e64696e67206465706f736974732e206361726566756c6c79207370656369616c207061636b61676573206172652061626f7574207468652069726f6e696320666f726765732e20736c796c79207370656369616c20650000006561732068616e672069726f6e69632c2073696c656e74207061636b616765732e20736c796c7920726567756c6172207061636b616765732061726520667572696f75736c79206f76657220746865207469746865732e20666c756666696c7920626f6c6463000000792061626f766520746865206361726566756c6c7920756e757375616c207468656f646f6c697465732e2066696e616c206475676f7574732061726520717569636b6c79206163726f73732074686520667572696f75736c7920726567756c617220641f00000076656e207061636b616765732077616b6520717569636b6c792e207265677526000000726566756c6c792066696e616c2072657175657374732e20726567756c61722c2069726f6e693a0000006c20706c6174656c6574732e20726567756c6172206163636f756e747320782d7261793a20756e757375616c2c20726567756c6172206163636f41000000737320657863757365732063616a6f6c6520736c796c79206163726f737320746865207061636b616765732e206465706f73697473207072696e742061726f756e7200000020736c796c792065787072657373206173796d70746f7465732e20726567756c6172206465706f7369747320686167676c6520736c796c792e206361726566756c6c792069726f6e696320686f636b657920706c617965727320736c65657020626c697468656c792e206361726566756c6c320000006566756c6c7920616c6f6e6773696465206f662074686520736c796c792066696e616c20646570656e64656e636965732e20420000006e6963206465706f7369747320626f6f73742061746f702074686520717569636b6c792066696e616c2072657175657374733f20717569636b6c7920726567756c61240000006f75736c792e2066696e616c2c20657870726573732067696674732063616a6f6c652061370000006963206465706f736974732061726520626c697468656c792061626f757420746865206361726566756c6c7920726567756c61722070615d0000002070656e64696e67206578637573657320686167676c6520667572696f75736c79206465706f736974732e2070656e64696e672c20657870726573732070696e746f206265616e732077616b6520666c756666696c79207061737420745a000000726e732e20626c697468656c7920626f6c6420636f7572747320616d6f6e672074686520636c6f73656c7920726567756c6172207061636b616765732075736520667572696f75736c7920626f6c6420706c6174656c6574733f2d000000732e2069726f6e69632c20756e757375616c206173796d70746f7465732077616b6520626c697468656c7920726a000000706c6174656c6574732e20626c697468656c792070656e64696e6720646570656e64656e636965732075736520666c756666696c79206163726f737320746865206576656e2070696e746f206265616e732e206361726566756c6c792073696c656e74206163636f756e5b0000006320646570656e64656e636965732e20667572696f75736c792065787072657373206e6f746f726e697320736c65657020736c796c7920726567756c6172206163636f756e74732e20696465617320736c6565702e206465706f736f000000756c6172206173796d70746f746573206172652061626f75742074686520667572696f7573206d756c7469706c696572732e206578707265737320646570656e64656e63696573206e61672061626f7665207468652069726f6e6963616c6c792069726f6e6963206163636f756e744e00000074732e2073696c656e7420726571756573747320686167676c652e20636c6f73656c792065787072657373207061636b6167657320736c656570206163726f73732074686520626c697468656c792e00000068656c7920656e746963696e676c792065787072657373206163636f756e74732e206576656e2c2066696e616c204f00000020726571756573747320616761696e73742074686520706c6174656c65747320757365206e65766572206163636f7264696e6720746f2074686520717569636b6c7920726567756c61722070696e743d00000065616e7320626f6f7374206361726566756c6c79207370656369616c2072657175657374732e206163636f756e7473206172652e206361726566756c6c6e000000792066696e616c207061636b616765732e20736c6f7720666f7865732063616a6f6c6520717569636b6c792e20717569636b6c792073696c656e7420706c6174656c657473206272656163682069726f6e6963206163636f756e74732e20756e757375616c2070696e746f2062651502195c48016d15080015022502180a6e6174696f6e5f6b657900150c250218046e616d650015022502180a726567696f6e5f6b657900150c2502180b636f6d6d656e745f636f6c001632191c194c26081c1502190519180a6e6174696f6e5f6b65791500163216fa0116fa01260800002682021c150c19051918046e616d651500163216dc0416dc04268202000026de061c1502190519180a726567696f6e5f6b65791500163216fa0116fa0126de06000026d8081c150c190519180b636f6d6d656e745f636f6c1500163216fc1e16fc1e26d80800001600163200280a706172717565742d6d7200ea00000050415231"

    f = self.cluster.fs.open(prefix + '/test-parquet.parquet', "w")
    f.write(test_data.decode('hex'))

    # autodetect
    response = self.c.get('/filebrowser/view=%s/test-parquet.parquet' % prefix)

    assert_true('FRANCE' in response.context[0]['view']['contents'])


  def test_view_parquet_snappy(self):
    if not snappy_installed():
      raise SkipTest

    prefix = self.cluster.fs_prefix + '/test_view_parquet_snappy'
    self.cluster.fs.mkdir(prefix)

    with open('apps/filebrowser/src/filebrowser/test_data/parquet-snappy.parquet') as f:
      hdfs = self.cluster.fs.open(prefix + '/test-parquet-snappy.parquet', "w")
      hdfs.write(f.read())

    # autodetect
    response = self.c.get('/filebrowser/view=%s/test-parquet-snappy.parquet' % prefix)

    assert_true('SR3_ndw_otlt_cmf_xref_INA' in response.context[0]['view']['contents'], response.context[0]['view']['contents'])


  def test_view_bz2(self):
    prefix = self.cluster.fs_prefix + '/test_view_bz2'
    self.cluster.fs.mkdir(prefix)

    # Bz2 file encoded as hex.
    test_data = "425a6839314159265359338bcfac000001018002000c00200021981984185dc914e14240ce2f3eb0"

    f = self.cluster.fs.open(prefix + '/test-view.bz2', "w")
    f.write(test_data.decode('hex'))

    # autodetect
    response = self.c.get('/filebrowser/view=%s/test-view.bz2?compression=bz2' % prefix)
    assert_true('test' in response.context[0]['view']['contents'])

    response = self.c.get('/filebrowser/view=%s/test-view.bz2' % prefix)
    assert_true('test' in response.context[0]['view']['contents'])


  def test_view_gz(self):
    prefix = self.cluster.fs_prefix + '/test_view_gz'
    self.cluster.fs.mkdir(prefix)

    f = self.cluster.fs.open(prefix + '/test-view.gz', "w")
    sdf_string = '\x1f\x8b\x08\x082r\xf4K\x00\x03f\x00+NI\xe3\x02\x00\xad\x96b\xc4\x04\x00\x00\x00'
    f.write(sdf_string)
    f.close()

    response = self.c.get('/filebrowser/view=%s/test-view.gz?compression=gzip' % prefix)
    assert_equal(response.context[0]['view']['contents'], "sdf\n")

    # autodetect
    response = self.c.get('/filebrowser/view=%s/test-view.gz' % prefix)
    assert_equal(response.context[0]['view']['contents'], "sdf\n")

    # ensure compression note is rendered
    assert_equal(response.context[0]['view']['compression'], "gzip")
    assert_true('Output rendered from compressed' in response.content, response.content)

    # offset should do nothing
    response = self.c.get('/filebrowser/view=%s/test-view.gz?compression=gzip&offset=1' % prefix)
    assert_true("Offsets are not supported" in response.context[0]['message'], response.context[0]['message'])

    f = self.cluster.fs.open(prefix + '/test-view2.gz', "w")
    f.write("hello")
    f.close()

    # we shouldn't autodetect non gzip files
    response = self.c.get('/filebrowser/view=%s/test-view2.gz' % prefix)
    assert_equal(response.context[0]['view']['contents'], "hello")

    # we should fail to do a bad thing if they specify compression when it's not set.
    response = self.c.get('/filebrowser/view=%s/test-view2.gz?compression=gzip' % prefix)
    assert_true("Failed to decompress" in response.context[0]['message'])


  def test_view_i18n(self):
    # Test viewing files in different encodings
    content = u'pt-Olá en-hello ch-你好 ko-안녕 ru-Здравствуйте'
    view_i18n_helper(self.c, self.cluster, 'utf-8', content)
    view_i18n_helper(self.c, self.cluster, 'utf-16', content)

    content = u'你好-big5'
    view_i18n_helper(self.c, self.cluster, 'big5', content)

    content = u'こんにちは-shift-jis'
    view_i18n_helper(self.c, self.cluster, 'shift_jis', content)

    content = u'안녕하세요-johab'
    view_i18n_helper(self.c, self.cluster, 'johab', content)

    # Test that the default view is home
    response = self.c.get('/filebrowser/view=/')
    assert_equal(response.context[0]['path'], '/')
    response = self.c.get('/filebrowser/view=/?default_to_home=1')
    assert_equal("/filebrowser/view=/user/test", urllib.unquote(response["location"]))


  def test_view_access(self):
    prefix = self.cluster.fs_prefix
    NO_PERM_DIR = prefix + '/test-no-perm'

    self.cluster.fs.mkdir(NO_PERM_DIR, mode='700')

    c_no_perm = make_logged_in_client(username='no_home')
    response = c_no_perm.get('/filebrowser/view=%s' % NO_PERM_DIR)
    assert_true('Cannot access' in response.context[0]['message'])

    response = self.c.get('/filebrowser/view=/test-does-not-exist')
    assert_true('Cannot access' in response.context[0]['message'])


  def test_index(self):
    HOME_DIR = '/user/test'
    NO_HOME_DIR = '/user/no_home'

    c_no_home = make_logged_in_client(username='no_home')

    if not self.cluster.fs.exists(HOME_DIR):
      self.cluster.fs.create_home_dir(HOME_DIR)
    assert_false(self.cluster.fs.exists(NO_HOME_DIR))

    response = self.c.get('/filebrowser', follow=True)
    assert_equal(HOME_DIR, response.context[0]['path'])
    assert_equal(HOME_DIR, response.context[0]['home_directory'])

    response = c_no_home.get('/filebrowser', follow=True)
    assert_equal('/', response.context[0]['path'])
    assert_equal(None, response.context[0]['home_directory'])


  def test_download(self):
    prefix = self.cluster.fs_prefix + '/test_download'
    self.cluster.fs.mkdir(prefix)

    f = self.cluster.fs.open(prefix + '/xss', "w")
    sdf_string = '''<html>
<head>
<title>Hello</title>
<script>
alert("XSS")
</script>
</head>
<body>
<h1>I am evil</h1>
</body>
</html>'''
    f.write(sdf_string)
    f.close()

    response = self.c.get('/filebrowser/download=%s/xss?disposition=inline' % prefix, follow=False) # The client does not support redirecting to another host. follow=False
    if response.status_code == 302: # Redirects to webhdfs
      assert_true(response.url.find('webhdfs') >= 0)
    else:
      assert_equal(200, response.status_code)
      assert_equal('attachment', response['Content-Disposition'])

    # Download fails and displays exception because of missing permissions
    self.cluster.fs.chmod(prefix + '/xss', 0700)

    not_me = make_logged_in_client("not_me", is_superuser=False)
    grant_access("not_me", "not_me", "filebrowser")
    response = not_me.get('/filebrowser/download=%s/xss?disposition=inline' % prefix, follow=True)
    assert_true('User not_me is not authorized to download' in response.context[0]['message'], response.context[0]['message'])


  def test_edit_i18n(self):
    prefix = self.cluster.fs_prefix + '/test_view_gz'
    self.cluster.fs.mkdir(prefix)

    # Test utf-8
    pass_1 = u'en-hello pt-Olá ch-你好 ko-안녕 ru-Здравствуйте'
    pass_2 = pass_1 + u'yi-העלא'
    edit_i18n_helper(self.c, self.cluster, 'utf-8', pass_1, pass_2)

    # Test utf-16
    edit_i18n_helper(self.c, self.cluster, 'utf-16', pass_1, pass_2)

    # Test cjk
    pass_1 = u'big5-你好'
    pass_2 = pass_1 + u'世界'
    edit_i18n_helper(self.c, self.cluster, 'big5', pass_1, pass_2)

    pass_1 = u'shift_jis-こんにちは'
    pass_2 = pass_1 + u'世界'
    edit_i18n_helper(self.c, self.cluster, 'shift_jis', pass_1, pass_2)

    pass_1 = u'johab-안녕하세요'
    pass_2 = pass_1 + u'세상'
    edit_i18n_helper(self.c, self.cluster, 'johab', pass_1, pass_2)


  def test_upload_file(self):
    with tempfile.NamedTemporaryFile() as local_file:
      # Make sure we can upload larger than the UPLOAD chunk size
      file_size = UPLOAD_CHUNK_SIZE.get() * 2
      local_file.write('0' * file_size)
      local_file.flush()

      prefix = self.cluster.fs_prefix + '/test_upload_file'
      self.cluster.fs.mkdir(prefix)

      USER_NAME = 'test'
      HDFS_DEST_DIR = prefix + "/tmp/fb-upload-test"
      LOCAL_FILE = local_file.name
      HDFS_FILE = HDFS_DEST_DIR + '/' + os.path.basename(LOCAL_FILE)

      self.cluster.fs.do_as_superuser(self.cluster.fs.mkdir, HDFS_DEST_DIR)
      self.cluster.fs.do_as_superuser(self.cluster.fs.chown, HDFS_DEST_DIR, USER_NAME, USER_NAME)
      self.cluster.fs.do_as_superuser(self.cluster.fs.chmod, HDFS_DEST_DIR, 0700)

      stats = self.cluster.fs.stats(HDFS_DEST_DIR)
      assert_equal(stats['user'], USER_NAME)
      assert_equal(stats['group'], USER_NAME)

      # Just upload the current python file
      resp = self.c.post('/filebrowser/upload/file?dest=%s' % HDFS_DEST_DIR, # GET param avoids infinite looping
                         dict(dest=HDFS_DEST_DIR, hdfs_file=file(LOCAL_FILE)))
      response = json.loads(resp.content)

      assert_equal(0, response['status'], response)
      stats = self.cluster.fs.stats(HDFS_FILE)
      assert_equal(stats['user'], USER_NAME)
      assert_equal(stats['group'], USER_NAME)

      f = self.cluster.fs.open(HDFS_FILE)
      actual = f.read(file_size)
      expected = file(LOCAL_FILE).read()
      assert_equal(actual, expected, 'files do not match: %s != %s' % (len(actual), len(expected)))

      # Upload again and so fails because file already exits
      resp = self.c.post('/filebrowser/upload/file?dest=%s' % HDFS_DEST_DIR,
                         dict(dest=HDFS_DEST_DIR, hdfs_file=file(LOCAL_FILE)))
      response = json.loads(resp.content)
      assert_equal(-1, response['status'], response)
      assert_true('already exists' in response['data'], response)

      # Upload in / and fails because of missing permissions
      not_me = make_logged_in_client("not_me", is_superuser=False)
      grant_access("not_me", "not_me", "filebrowser")
      try:
        resp = not_me.post('/filebrowser/upload/file?dest=%s' % HDFS_DEST_DIR,
                           dict(dest=HDFS_DEST_DIR, hdfs_file=file(LOCAL_FILE)))
        response = json.loads(resp.content)
        assert_equal(-1, response['status'], response)
        assert_true('User not_me does not have permissions' in response['data'], response)
      except AttributeError:
        # Seems like a Django bug.
        # StopFutureHandlers() does not seem to work in test mode as it continues to MemoryFileUploadHandler after perm issue and so fails.
        pass

  def test_extract_zip(self):
    ENABLE_EXTRACT_UPLOADED_ARCHIVE.set_for_testing(True)
    prefix = self.cluster.fs_prefix + '/test_upload_zip'
    self.cluster.fs.mkdir(prefix)

    USER_NAME = 'test'
    HDFS_DEST_DIR = prefix + "/tmp/fb-upload-test"
    ZIP_FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/te st.zip')
    HDFS_ZIP_FILE = HDFS_DEST_DIR + '/te st.zip'
    try:
      self.cluster.fs.mkdir(HDFS_DEST_DIR)
      self.cluster.fs.chown(HDFS_DEST_DIR, USER_NAME)
      self.cluster.fs.chmod(HDFS_DEST_DIR, 0700)

      # Upload archive
      resp = self.c.post('/filebrowser/upload/file?dest=%s' % HDFS_DEST_DIR,
                         dict(dest=HDFS_DEST_DIR, hdfs_file=file(ZIP_FILE)))
      response = json.loads(resp.content)
      assert_equal(0, response['status'], response)
      assert_true(self.cluster.fs.exists(HDFS_ZIP_FILE))

      resp = self.c.post('/filebrowser/extract_archive',
                         dict(upload_path=HDFS_DEST_DIR, archive_name='te st.zip'))
      response = json.loads(resp.content)
      assert_equal(0, response['status'], response)
      assert_true('handle' in response and response['handle']['id'], response)

    finally:
      cleanup_file(self.cluster, HDFS_ZIP_FILE)

  def test_compress_hdfs_files(self):
    ENABLE_EXTRACT_UPLOADED_ARCHIVE.set_for_testing(True)
    prefix = self.cluster.fs_prefix + '/test_compress_files'
    self.cluster.fs.mkdir(prefix)

    test_dir1 = prefix + '/test_dir1'
    self.cluster.fs.mkdir(test_dir1)
    self.cluster.fs.chown(test_dir1, 'test')
    self.cluster.fs.chmod(test_dir1, 0700)

    test_dir2 = prefix + '/test_dir2'
    self.cluster.fs.mkdir(test_dir2)
    self.cluster.fs.chown(test_dir2, 'test')
    self.cluster.fs.chmod(test_dir2, 0700)

    try:
      resp = self.c.post('/filebrowser/compress_files', {'upload_path': prefix, 'files[]': ['test_dir1','test_dir2'], 'archive_name': 'test_compress.zip'})
      response = json.loads(resp.content)
      assert_equal(0, response['status'], response)
      assert_true('handle' in response and response['handle']['id'], response)
    finally:
      ENABLE_EXTRACT_UPLOADED_ARCHIVE.set_for_testing(False)
      cleanup_tree(self.cluster, prefix)


  def test_extract_tgz(self):
    ENABLE_EXTRACT_UPLOADED_ARCHIVE.set_for_testing(True)
    prefix = self.cluster.fs_prefix + '/test_upload_tgz'
    self.cluster.fs.mkdir(prefix)

    USER_NAME = 'test'
    HDFS_DEST_DIR = prefix + "/fb-upload-test"
    TGZ_FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/test.tar.gz')
    HDFS_TGZ_FILE = HDFS_DEST_DIR + '/test.tar.gz'

    self.cluster.fs.mkdir(HDFS_DEST_DIR)
    self.cluster.fs.chown(HDFS_DEST_DIR, USER_NAME)
    self.cluster.fs.chmod(HDFS_DEST_DIR, 0700)

    try:
      # Upload archive
      resp = self.c.post('/filebrowser/upload/file?dest=%s' % HDFS_DEST_DIR,
                         dict(dest=HDFS_DEST_DIR, hdfs_file=file(TGZ_FILE)))
      response = json.loads(resp.content)
      assert_equal(0, response['status'], response)
      assert_true(self.cluster.fs.exists(HDFS_TGZ_FILE))

      resp = self.c.post('/filebrowser/extract_archive',
                         dict(upload_path=HDFS_DEST_DIR, archive_name='test.tar.gz'))
      response = json.loads(resp.content)
      assert_equal(0, response['status'], response)
      assert_true('handle' in response and response['handle']['id'], response)

    finally:
      cleanup_file(self.cluster, HDFS_TGZ_FILE)


  def test_extract_bz2(self):
    ENABLE_EXTRACT_UPLOADED_ARCHIVE.set_for_testing(True)
    prefix = self.cluster.fs_prefix + '/test_upload_bz2'

    HDFS_DEST_DIR = prefix + "/fb-upload-test"
    BZ2_FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/test.txt.bz2')
    HDFS_BZ2_FILE = HDFS_DEST_DIR + '/test.txt.bz2'

    self.cluster.fs.mkdir(HDFS_DEST_DIR)

    try:
      # Upload archive
      resp = self.c.post('/filebrowser/upload/file?dest=%s' % HDFS_DEST_DIR,
                         dict(dest=HDFS_DEST_DIR, hdfs_file=file(BZ2_FILE)))
      response = json.loads(resp.content)
      assert_equal(0, response['status'], response)
      assert_true(self.cluster.fs.exists(HDFS_BZ2_FILE))

      resp = self.c.post('/filebrowser/extract_archive',
                         dict(upload_path=HDFS_DEST_DIR, archive_name='test.txt.bz2'))
      response = json.loads(resp.content)
      assert_equal(0, response['status'], response)
      assert_true('handle' in response and response['handle']['id'], response)

    finally:
      cleanup_file(self.cluster, HDFS_BZ2_FILE)


  def test_trash(self):
    prefix = self.cluster.fs_prefix + '/test_trash'
    self.cluster.fs.mkdir(prefix)

    USERNAME = 'test'
    HOME_TRASH_DIR = '/user/%s/.Trash/Current/user/%s' % (USERNAME, USERNAME)
    HOME_TRASH_DIR2 = '/user/%s/.Trash' % USERNAME
    PATH_1 = '%s/1' % prefix
    self.cluster.fs.mkdir(PATH_1)

    self.c.post('/filebrowser/rmtree?skip_trash=true', dict(path=[HOME_TRASH_DIR]))
    self.c.post('/filebrowser/rmtree?skip_trash=true', dict(path=[HOME_TRASH_DIR2]))

    # No trash folder
    response = self.c.get('/filebrowser/view=/user/test?default_to_trash', follow=True)

    assert_equal([], response.redirect_chain)

    self.c.post('/filebrowser/rmtree', dict(path=[PATH_1]))

    # We have a trash folder so a redirect (Current not always there)
    response = self.c.get('/filebrowser/view=/user/test?default_to_trash', follow=True)
    assert_true(any(['.Trash' in page for page, code in response.redirect_chain]), response.redirect_chain)

    self.c.post('/filebrowser/rmtree?skip_trash=true', dict(path=[HOME_TRASH_DIR]))

    # No home trash, just regular root trash
    response = self.c.get('/filebrowser/view=/user/test?default_to_trash', follow=True)
    assert_true(any(['.Trash' in page for page, code in response.redirect_chain]), response.redirect_chain)

def view_i18n_helper(c, cluster, encoding, content):
  """
  Write the content in the given encoding directly into the filesystem.
  Then try to view it and make sure the data is correct.
  """
  prefix = cluster.fs_prefix + '/test_view_i18n'
  filename = prefix + u'/test-view-carácter-internacional'
  bytestring = content.encode(encoding)

  try:
    f = cluster.fs.open(filename, "w")
    f.write(bytestring)
    f.close()

    response = c.get('/filebrowser/view=%s?encoding=%s' % (filename, encoding))
    assert_equal(response.context[0]['view']['contents'], content)

    response = c.get('/filebrowser/view=%s?encoding=%s&end=8&begin=1' % (filename, encoding))
    assert_equal(response.context[0]['view']['contents'],
                 unicode(bytestring[0:8], encoding, errors='replace'))
  finally:
    cleanup_file(cluster, filename)

def edit_i18n_helper(c, cluster, encoding, contents_pass_1, contents_pass_2):
  """
  Put the content into the file with a specific encoding.
  """
  prefix = cluster.fs_prefix + '/test_edit_i18n'
  # This path is non-normalized to test normalization too
  filename = prefix + u'//test-filebrowser//./test-edit-carácter-internacional with space and () en-hello pt-Olá ch-你好 ko-안녕 ru-Здравствуйте'

  # File doesn't exist - should be empty
  edit_url = '/filebrowser/edit=' + filename
  response = c.get(edit_url)
  assert_equal(response.context[0]['form'].data['path'], filename)
  assert_equal(response.context[0]['form'].data['contents'], "")

  # Just going to the edit page and not hitting save should not
  # create the file
  assert_false(cluster.fs.exists(filename))

  try:
    # Put some data in there and post
    response = c.post("/filebrowser/save", dict(
        path=filename,
        contents=contents_pass_1,
        encoding=encoding), follow=True)
    assert_equal(response.context[0]['form'].data['path'], filename)
    assert_equal(response.context[0]['form'].data['contents'], contents_pass_1)

    # File should now exist
    assert_true(cluster.fs.exists(filename))
    # And its contents should be what we expect
    f = cluster.fs.open(filename)
    assert_equal(f.read(), contents_pass_1.encode(encoding))
    assert_false('\r\n' in f.read()) # No CRLF line terminators
    f.close()

    # We should be able to overwrite the file with another save
    response = c.post("/filebrowser/save", dict(
        path=filename,
        contents=contents_pass_2,
        encoding=encoding), follow=True)
    assert_equal(response.context[0]['form'].data['path'], filename)
    assert_equal(response.context[0]['form'].data['contents'], contents_pass_2)
    f = cluster.fs.open(filename)
    assert_equal(f.read(), contents_pass_2.encode(encoding))
    assert_false('\r\n' in f.read()) # No CRLF line terminators
    f.close()

    # TODO(todd) add test for maintaining ownership/permissions
  finally:
    cleanup_file(cluster, filename)


def test_location_to_url():
  prefix = '/filebrowser/view='
  assert_equal(prefix + '/var/lib/hadoop-hdfs', location_to_url('/var/lib/hadoop-hdfs', False))
  assert_equal(prefix + '/var/lib/hadoop-hdfs', location_to_url('hdfs://localhost:8020/var/lib/hadoop-hdfs'))
  assert_equal('/hue' + prefix + '/var/lib/hadoop-hdfs', location_to_url('hdfs://localhost:8020/var/lib/hadoop-hdfs', False, True))
  assert_equal(prefix + '/', location_to_url('hdfs://localhost:8020'))
  assert_equal(prefix + 's3a://bucket/key', location_to_url('s3a://bucket/key'))


class TestS3AccessPermissions(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    grant_access('test', 'test', 'filebrowser')
    add_to_group('test')

    self.user = User.objects.get(username="test")

  def test_no_default_permissions(self):
    response = self.client.get('/filebrowser/view=S3A://')
    assert_equal(500, response.status_code)

    response = self.client.get('/filebrowser/view=S3A://bucket')
    assert_equal(500, response.status_code)

    response = self.client.get('/filebrowser/view=s3a://bucket')
    assert_equal(500, response.status_code)

    response = self.client.get('/filebrowser/view=S3A://bucket/hue')
    assert_equal(500, response.status_code)

    response = self.client.post('/filebrowser/rmtree', dict(path=['S3A://bucket/hue']))
    assert_equal(500, response.status_code)

    # 500 for real currently
    assert_raises(IOError, self.client.get, '/filebrowser/edit=S3A://bucket/hue')

    # 500 for real currently
#     with tempfile.NamedTemporaryFile() as local_file: # Flaky
#       DEST_DIR = 'S3A://bucket/hue'
#       LOCAL_FILE = local_file.name
#       assert_raises(S3FileSystemException, self.client.post, '/filebrowser/upload/file?dest=%s' % DEST_DIR, dict(dest=DEST_DIR, hdfs_file=file(LOCAL_FILE)))

  def test_has_default_permissions(self):
    if not get_test_bucket():
      raise SkipTest

    add_permission(self.user.username, 'has_s3', permname='s3_access', appname='filebrowser')

    try:
      response = self.client.get('/filebrowser/view=S3A://')
      assert_equal(200, response.status_code)
    finally:
      remove_from_group(self.user.username, 'has_s3')
