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
import urlparse
from avro import schema, datafile, io

from django.utils.encoding import smart_str
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from hadoop import pseudo_hdfs4
from filebrowser.views import location_to_url

from conf import MAX_SNAPPY_DECOMPRESSION_SIZE
from lib.rwx import expand_mode
from views import snappy_installed


LOG = logging.getLogger(__name__)


@attr('requires_hadoop')
def test_remove():
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    c = make_logged_in_client(cluster.superuser)
    cluster.fs.setuser(cluster.superuser)

    prefix = '/test-delete'
    PATH_1 = '/%s/1' % prefix
    PATH_2 = '/%s/2' % prefix
    PATH_3 = '/%s/3' % prefix
    cluster.fs.mkdir(prefix)
    cluster.fs.mkdir(PATH_1)
    cluster.fs.mkdir(PATH_2)
    cluster.fs.mkdir(PATH_3)

    assert_true(cluster.fs.exists(PATH_1))
    assert_true(cluster.fs.exists(PATH_2))
    assert_true(cluster.fs.exists(PATH_3))

    c.post('/filebrowser/rmtree', dict(path=[PATH_1]))
    assert_false(cluster.fs.exists(PATH_1))
    assert_true(cluster.fs.exists(PATH_2))
    assert_true(cluster.fs.exists(PATH_3))

    c.post('/filebrowser/rmtree', dict(path=[PATH_2, PATH_3]))
    assert_false(cluster.fs.exists(PATH_1))
    assert_false(cluster.fs.exists(PATH_2))
    assert_false(cluster.fs.exists(PATH_3))

  finally:
    try:
      cluster.fs.rmtree(prefix)     # Clean up
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_move():
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    c = make_logged_in_client(cluster.superuser)
    cluster.fs.setuser(cluster.superuser)

    prefix = '/test-move'
    PATH_1 = '%s/1' % prefix
    PATH_2 = '%s/2' % prefix
    SUB_PATH1_1 = '%s/1' % PATH_1
    SUB_PATH1_2 = '%s/2' % PATH_1
    SUB_PATH1_3 = '%s/3' % PATH_1
    SUB_PATH2_1 = '%s/1' % PATH_2
    SUB_PATH2_2 = '%s/2' % PATH_2
    SUB_PATH2_3 = '%s/3' % PATH_2
    cluster.fs.mkdir(prefix)
    cluster.fs.mkdir(PATH_1)
    cluster.fs.mkdir(PATH_2)
    cluster.fs.mkdir(SUB_PATH1_1)
    cluster.fs.mkdir(SUB_PATH1_2)
    cluster.fs.mkdir(SUB_PATH1_3)

    assert_true(cluster.fs.exists(SUB_PATH1_1))
    assert_true(cluster.fs.exists(SUB_PATH1_2))
    assert_true(cluster.fs.exists(SUB_PATH1_3))
    assert_false(cluster.fs.exists(SUB_PATH2_1))
    assert_false(cluster.fs.exists(SUB_PATH2_2))
    assert_false(cluster.fs.exists(SUB_PATH2_3))

    c.post('/filebrowser/move', dict(src_path=[SUB_PATH1_1], dest_path=PATH_2))
    assert_false(cluster.fs.exists(SUB_PATH1_1))
    assert_true(cluster.fs.exists(SUB_PATH1_2))
    assert_true(cluster.fs.exists(SUB_PATH1_3))
    assert_true(cluster.fs.exists(SUB_PATH2_1))
    assert_false(cluster.fs.exists(SUB_PATH2_2))
    assert_false(cluster.fs.exists(SUB_PATH2_3))

    c.post('/filebrowser/move', dict(src_path=[SUB_PATH1_2, SUB_PATH1_3], dest_path=PATH_2))
    assert_false(cluster.fs.exists(SUB_PATH1_1))
    assert_false(cluster.fs.exists(SUB_PATH1_2))
    assert_false(cluster.fs.exists(SUB_PATH1_3))
    assert_true(cluster.fs.exists(SUB_PATH2_1))
    assert_true(cluster.fs.exists(SUB_PATH2_2))
    assert_true(cluster.fs.exists(SUB_PATH2_3))

  finally:
    try:
      cluster.fs.rmtree(prefix)     # Clean up
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_copy():
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    c = make_logged_in_client(cluster.superuser)
    cluster.fs.setuser(cluster.superuser)

    prefix = '/test-copy'
    PATH_1 = '%s/1' % prefix
    PATH_2 = '%s/2' % prefix
    SUB_PATH1_1 = '%s/1' % PATH_1
    SUB_PATH1_2 = '%s/2' % PATH_1
    SUB_PATH1_3 = '%s/3' % PATH_1
    SUB_PATH2_1 = '%s/1' % PATH_2
    SUB_PATH2_2 = '%s/2' % PATH_2
    SUB_PATH2_3 = '%s/3' % PATH_2
    cluster.fs.mkdir(prefix)
    cluster.fs.mkdir(PATH_1)
    cluster.fs.mkdir(PATH_2)
    cluster.fs.mkdir(SUB_PATH1_1)
    cluster.fs.mkdir(SUB_PATH1_2)
    cluster.fs.mkdir(SUB_PATH1_3)

    assert_true(cluster.fs.exists(SUB_PATH1_1))
    assert_true(cluster.fs.exists(SUB_PATH1_2))
    assert_true(cluster.fs.exists(SUB_PATH1_3))
    assert_false(cluster.fs.exists(SUB_PATH2_1))
    assert_false(cluster.fs.exists(SUB_PATH2_2))
    assert_false(cluster.fs.exists(SUB_PATH2_3))

    c.post('/filebrowser/copy', dict(src_path=[SUB_PATH1_1], dest_path=PATH_2))
    assert_true(cluster.fs.exists(SUB_PATH1_1))
    assert_true(cluster.fs.exists(SUB_PATH1_2))
    assert_true(cluster.fs.exists(SUB_PATH1_3))
    assert_true(cluster.fs.exists(SUB_PATH2_1))
    assert_false(cluster.fs.exists(SUB_PATH2_2))
    assert_false(cluster.fs.exists(SUB_PATH2_3))

    c.post('/filebrowser/copy', dict(src_path=[SUB_PATH1_2, SUB_PATH1_3], dest_path=PATH_2))
    assert_true(cluster.fs.exists(SUB_PATH1_1))
    assert_true(cluster.fs.exists(SUB_PATH1_2))
    assert_true(cluster.fs.exists(SUB_PATH1_3))
    assert_true(cluster.fs.exists(SUB_PATH2_1))
    assert_true(cluster.fs.exists(SUB_PATH2_2))
    assert_true(cluster.fs.exists(SUB_PATH2_3))

  finally:
    try:
      cluster.fs.rmtree(prefix)     # Clean up
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_mkdir_singledir():
  cluster = pseudo_hdfs4.shared_cluster()
  cluster.fs.setuser('test')
  c = make_logged_in_client()

  try:
    # We test that mkdir fails when a non-relative path is provided and a multi-level path is provided.
    success_path = 'mkdir_singledir'
    path_absolute = '/mkdir_singledir'
    path_fail = 'fail/foo'
    path_other_failure = 'fail#bar'
    prefix = '/tmp/test-filebrowser/'
    # Two of the following post requests should throw exceptions.
    # See https://issues.cloudera.org/browse/HUE-793.
    c.post('/filebrowser/mkdir', dict(path=prefix, name=path_fail))
    c.post('/filebrowser/mkdir', dict(path=prefix, name=path_other_failure))
    c.post('/filebrowser/mkdir', dict(path=prefix, name=path_absolute))
    c.post('/filebrowser/mkdir', dict(path=prefix, name=success_path))

    # Read the parent dir and make sure we created 'success_path' only.
    response = c.get('/filebrowser/view' + prefix)
    dir_listing = response.context['files']
    assert_equal(3, len(dir_listing))
    assert_equal(dir_listing[2]['name'], success_path)

  finally:
    try:
      cluster.fs.rmtree(prefix)     # Clean up
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_touch():
  cluster = pseudo_hdfs4.shared_cluster()
  cluster.fs.setuser('test')
  c = make_logged_in_client()

  try:
    success_path = 'touch_file'
    path_absolute = '/touch_file'
    path_fail = 'touch_fail/file'
    prefix = '/tmp/test-filebrowser-touch/'

    cluster.fs.mkdir(prefix)

    resp = c.post('/filebrowser/touch', dict(path=prefix, name=path_fail))
    assert_equal(500, resp.status_code)
    resp = c.post('/filebrowser/touch', dict(path=prefix, name=path_absolute))
    assert_equal(500, resp.status_code)
    resp = c.post('/filebrowser/touch', dict(path=prefix, name=success_path))
    assert_equal(200, resp.status_code)

    # Read the parent dir and make sure we created 'success_path' only.
    response = c.get('/filebrowser/view' + prefix)
    file_listing = response.context['files']
    assert_equal(3, len(file_listing))
    assert_equal(file_listing[2]['name'], success_path)

  finally:
    try:
      cluster.fs.rmtree(prefix)
    except:
      pass


@attr('requires_hadoop')
def test_chmod():
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    c = make_logged_in_client(cluster.superuser)
    cluster.fs.setuser(cluster.superuser)

    PATH = "/chmod_test"
    SUBPATH = PATH + '/test'
    cluster.fs.mkdir(SUBPATH)

    permissions = ('user_read', 'user_write', 'user_execute',
        'group_read', 'group_write', 'group_execute',
        'other_read', 'other_write', 'other_execute',
        'sticky') # Order matters!

    # Get current mode, change mode, check mode
    # Start with checking current mode
    assert_not_equal(041777, int(cluster.fs.stats(PATH)["mode"]))

    # Setup post data
    permissions_dict = dict( zip(permissions, [True]*len(permissions)) )
    kwargs = {'path': [PATH]}
    kwargs.update(permissions_dict)

    # Set 1777, then check permissions of dirs
    response = c.post("/filebrowser/chmod", kwargs)
    assert_equal(041777, int(cluster.fs.stats(PATH)["mode"]))

    # Now do the above recursively
    assert_not_equal(041777, int(cluster.fs.stats(SUBPATH)["mode"]))
    kwargs['recursive'] = True
    response = c.post("/filebrowser/chmod", kwargs)
    assert_equal(041777, int(cluster.fs.stats(SUBPATH)["mode"]))

    # Test bulk chmod
    PATH_2 = u"/test-chmod2"
    PATH_3 = u"/test-chown3"
    cluster.fs.mkdir(PATH_2)
    cluster.fs.mkdir(PATH_3)
    kwargs['path'] = [PATH_2, PATH_3]
    assert_not_equal(041777, int(cluster.fs.stats(PATH_2)["mode"]))
    assert_not_equal(041777, int(cluster.fs.stats(PATH_3)["mode"]))
    c.post("/filebrowser/chmod", kwargs)
    assert_equal(041777, int(cluster.fs.stats(PATH_2)["mode"]))
    assert_equal(041777, int(cluster.fs.stats(PATH_3)["mode"]))

  finally:
    try:
      cluster.fs.rmtree(PATH)     # Clean up
      cluster.fs.rmtree(PATH_2)     # Clean up
      cluster.fs.rmtree(PATH_3)     # Clean up
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_chmod_sticky():
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    c = make_logged_in_client(cluster.superuser)
    cluster.fs.setuser(cluster.superuser)

    PATH = "/chmod_test"
    cluster.fs.mkdir(PATH)

    # Get current mode and make sure sticky bit is off
    mode = expand_mode( int(cluster.fs.stats(PATH)["mode"]) )
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
    response = c.post("/filebrowser/chmod", kwargs)
    mode = expand_mode( int(cluster.fs.stats(PATH)["mode"]) )
    assert_equal(True, mode[-1])

    # Unset sticky bit, then check sticky bit is off in hdfs
    del kwargs['sticky']
    response = c.post("/filebrowser/chmod", kwargs)
    mode = expand_mode( int(cluster.fs.stats(PATH)["mode"]) )
    assert_equal(False, mode[-1])

  finally:
    try:
      cluster.fs.rmtree(PATH)     # Clean up
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_chown():
  cluster = pseudo_hdfs4.shared_cluster()

  # Only the Hadoop superuser really has carte blanche here
  c = make_logged_in_client(cluster.superuser)
  cluster.fs.setuser(cluster.superuser)

  PATH = u"/test-chown-en-Español"
  cluster.fs.mkdir(PATH)
  c.post("/filebrowser/chown", dict(path=[PATH], user="x", group="y"))
  assert_equal("x", cluster.fs.stats(PATH)["user"])
  assert_equal("y", cluster.fs.stats(PATH)["group"])
  c.post("/filebrowser/chown", dict(path=[PATH], user="__other__", user_other="z", group="y"))
  assert_equal("z", cluster.fs.stats(PATH)["user"])

  # Now check recursive
  SUBPATH = PATH + '/test'
  cluster.fs.mkdir(SUBPATH)
  c.post("/filebrowser/chown", dict(path=[PATH], user="x", group="y", recursive=True))
  assert_equal("x", cluster.fs.stats(SUBPATH)["user"])
  assert_equal("y", cluster.fs.stats(SUBPATH)["group"])
  c.post("/filebrowser/chown", dict(path=[PATH], user="__other__", user_other="z", group="y", recursive=True))
  assert_equal("z", cluster.fs.stats(SUBPATH)["user"])

  # Test bulk chown
  PATH_2 = u"/test-chown-en-Español2"
  PATH_3 = u"/test-chown-en-Español2"
  cluster.fs.mkdir(PATH_2)
  cluster.fs.mkdir(PATH_3)
  c.post("/filebrowser/chown", dict(path=[PATH_2, PATH_3], user="x", group="y", recursive=True))
  assert_equal("x", cluster.fs.stats(PATH_2)["user"])
  assert_equal("y", cluster.fs.stats(PATH_2)["group"])
  assert_equal("x", cluster.fs.stats(PATH_3)["user"])
  assert_equal("y", cluster.fs.stats(PATH_3)["group"])


@attr('requires_hadoop')
def test_rename():
  cluster = pseudo_hdfs4.shared_cluster()

  c = make_logged_in_client(cluster.superuser)
  cluster.fs.setuser(cluster.superuser)

  PREFIX = u"/test-rename/"
  NAME = u"test-rename-before"
  NEW_NAME = u"test-rename-after"
  cluster.fs.mkdir(PREFIX + NAME)
  op = "rename"
  # test for full path rename
  c.post("/filebrowser/rename", dict(src_path=PREFIX + NAME, dest_path=PREFIX + NEW_NAME))
  assert_true(cluster.fs.exists(PREFIX + NEW_NAME))
  # test for smart rename
  c.post("/filebrowser/rename", dict(src_path=PREFIX + NAME, dest_path=NEW_NAME))
  assert_true(cluster.fs.exists(PREFIX + NEW_NAME))


@attr('requires_hadoop')
def test_listdir():
  cluster = pseudo_hdfs4.shared_cluster()
  try:
    c = make_logged_in_client('test')

    # Delete user's home if there's already something there
    home = cluster.fs.do_as_user('test', cluster.fs.get_home_dir)
    if cluster.fs.exists(home):
      cluster.fs.do_as_superuser(cluster.fs.rmtree, home)

    response = c.get('/filebrowser/')
    # Since we deleted the home directory... home_directory context should be None.
    assert_false(response.context['home_directory'], response.context['home_directory'])

    cluster.fs.do_as_superuser(cluster.fs.mkdir, home)
    cluster.fs.do_as_superuser(cluster.fs.chown, home, 'test', 'test')

    # These paths contain non-ascii characters. Your editor will need the
    # corresponding font library to display them correctly.
    #
    # We test that mkdir can handle unicode strings as well as byte strings.
    # And even when the byte string can't be decoded properly (big5), the listdir
    # still succeeds.
    orig_paths = [
      u'greek-Ελληνικά',
      u'chinese-漢語',
      'listdir%20.,<>~`!@$%^&()_-+="',
    ]

    prefix = home + '/test-filebrowser/'
    for path in orig_paths:
      c.post('/filebrowser/mkdir', dict(path=prefix, name=path))

    # Read the parent dir
    response = c.get('/filebrowser/view' + prefix)

    dir_listing = response.context['files']
    assert_equal(len(orig_paths) + 2, len(dir_listing))

    for dirent in dir_listing:
      path = dirent['name']
      if path in ('.', '..'):
        continue

      assert_true(path in orig_paths)

      # Drill down into the subdirectory
      url = urlparse.urlsplit(dirent['url'])[2]
      resp = c.get(url)

      # We are actually reading a directory
      assert_equal('.', resp.context['files'][1]['name'])
      assert_equal('..', resp.context['files'][0]['name'])

    # Test's home directory now exists. Should be returned.
    c = make_logged_in_client()
    response = c.get('/filebrowser/view' + prefix)
    assert_equal(response.context['home_directory'], home)

    # Test URL conflicts with filenames
    stat_dir = '%sstat/dir' % prefix
    cluster.fs.do_as_user('test', cluster.fs.mkdir, stat_dir)
    response = c.get('/filebrowser/view%s' % stat_dir)
    assert_equal(stat_dir, response.context['path'])

    response = c.get('/filebrowser/view/test-filebrowser/?default_to_home')
    assert_true(re.search('%s$' % home, response['Location']))

    # Test path relative to home directory
    cluster.fs.do_as_user('test', cluster.fs.mkdir, '%s/test_dir' % home)
    response = c.get('/filebrowser/home_relative_view/test_dir')
    assert_equal('%s/test_dir' % home, response.context['path'])

  finally:
    try:
      cluster.fs.do_as_superuser(cluster.fs.rmtree, prefix)
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_listdir_sort_and_filter():
  cluster = pseudo_hdfs4.shared_cluster()
  c = make_logged_in_client(cluster.superuser)
  cluster.fs.setuser(cluster.superuser)

  BASE = '/test_sort_and_filter'
  FUNNY_NAME = u'greek-Ελληνικά'
  try:
    cluster.fs.mkdir(BASE)
    # Create 10 files
    for i in range(1, 11):
      cluster.fs.create(cluster.fs.join(BASE, str(i)), data="foo" * i)

    # Create 1 funny name directory
    cluster.fs.mkdir(cluster.fs.join(BASE, FUNNY_NAME))

    # All 12 of the entries
    expect = [ '..', '.', FUNNY_NAME] + [ str(i) for i in range(1, 11) ]

    # Check pagination
    listing = c.get('/filebrowser/view' + BASE + '?pagesize=20').context['files']
    assert_equal(len(expect), len(listing))

    listing = c.get('/filebrowser/view' + BASE + '?pagesize=10').context['files']
    assert_equal(12, len(listing))

    listing = c.get('/filebrowser/view' + BASE + '?pagesize=10&pagenum=1').context['files']
    assert_equal(12, len(listing))

    listing = c.get('/filebrowser/view' + BASE + '?pagesize=10&pagenum=2').context['files']
    assert_equal(3, len(listing))

    # Check sorting (name)
    listing = c.get('/filebrowser/view' + BASE + '?sortby=name').context['files']
    assert_equal(sorted(expect[2:]), [ f['name'] for f in listing ][2:])

    listing = c.get('/filebrowser/view' + BASE + '?sortby=name&descending=false').context['files']
    assert_equal(sorted(expect[2:]), [ f['name'] for f in listing ][2:])

    listing = c.get('/filebrowser/view' + BASE + '?sortby=name&descending=true').context['files']
    assert_equal(".", listing[1]['name'])
    assert_equal("..", listing[0]['name'])
    assert_equal(FUNNY_NAME, listing[2]['name'])

    # Check sorting (size)
    listing = c.get('/filebrowser/view' + BASE + '?sortby=size').context['files']
    assert_equal(expect, [ f['name'] for f in listing ])

    # Check sorting (mtime)
    listing = c.get('/filebrowser/view' + BASE + '?sortby=mtime').context['files']
    assert_equal(".", listing[1]['name'])
    assert_equal("..", listing[0]['name'])
    assert_equal(FUNNY_NAME, listing[-1]['name'])

    # Check filter
    listing = c.get('/filebrowser/view' + BASE + '?filter=1').context['files']
    assert_equal(['..', '.', '1', '10'], [ f['name'] for f in listing ])

    listing = c.get('/filebrowser/view' + BASE + '?filter=' + FUNNY_NAME).context['files']
    assert_equal(['..', '.', FUNNY_NAME], [ f['name'] for f in listing ])

    # Check filter + sorting
    listing = c.get('/filebrowser/view' + BASE + '?filter=1&sortby=name&descending=true').context['files']
    assert_equal(['..', '.', '10', '1'], [ f['name'] for f in listing ])

    # Check filter + sorting + pagination
    listing = c.get('/filebrowser/view' + BASE + '?filter=1&sortby=name&descending=true&pagesize=1&pagenum=2').context['files']
    assert_equal(['..', '.', '1'], [ f['name'] for f in listing ])
  finally:
    try:
      cluster.fs.rmtree(BASE)
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_chooser():
  cluster = pseudo_hdfs4.shared_cluster()
  c = make_logged_in_client()

  # Note that the trailing slash is important. We ask for the root dir.
  resp = c.get('/filebrowser/chooser/?format=json')
  # We should get a json response
  dic = json.loads(resp.content)
  assert_equal('/', dic['current_dir_path'])
  assert_equal('/', dic['path'])


@attr('requires_hadoop')
def test_view_snappy_compressed():
  if not snappy_installed():
    raise SkipTest
  import snappy

  cluster = pseudo_hdfs4.shared_cluster()
  finish = []
  try:
    c = make_logged_in_client()
    cluster.fs.setuser(cluster.superuser)
    if cluster.fs.isdir('/tmp/test-snappy-filebrowser'):
      cluster.fs.rmtree('/tmp/test-snappy-filebrowser')

    cluster.fs.mkdir('/tmp/test-snappy-avro-filebrowser/')

    f = cluster.fs.open('/tmp/test-snappy-filebrowser/test-view.snappy', "w")
    f.write(snappy.compress('This is a test of the emergency broadcasting system.'))
    f.close()

    f = cluster.fs.open('/tmp/test-snappy-filebrowser/test-view.stillsnappy', "w")
    f.write(snappy.compress('The broadcasters of your area in voluntary cooperation with the FCC and other authorities.'))
    f.close()

    f = cluster.fs.open('/tmp/test-snappy-filebrowser/test-view.notsnappy', "w")
    f.write('foobar')
    f.close()

    # Snappy compressed fail
    response = c.get('/filebrowser/view/tmp/test-snappy-filebrowser/test-view.notsnappy?compression=snappy')
    assert_true('Failed to decompress' in response.context['message'], response)

    # Snappy compressed succeed
    response = c.get('/filebrowser/view/tmp/test-snappy-filebrowser/test-view.snappy')
    assert_equal('snappy', response.context['view']['compression'])
    assert_equal(response.context['view']['contents'], 'This is a test of the emergency broadcasting system.', response)

    # Snappy compressed succeed
    response = c.get('/filebrowser/view/tmp/test-snappy-filebrowser/test-view.stillsnappy')
    assert_equal('snappy', response.context['view']['compression'])
    assert_equal(response.context['view']['contents'], 'The broadcasters of your area in voluntary cooperation with the FCC and other authorities.', response)

    # Largest snappy compressed file
    finish.append( MAX_SNAPPY_DECOMPRESSION_SIZE.set_for_testing(1) )
    response = c.get('/filebrowser/view/tmp/test-snappy-filebrowser/test-view.stillsnappy?compression=snappy')
    assert_true('File size is greater than allowed max snappy decompression size of 1' in response.context['message'], response)

  finally:
    for done in finish:
      done()
    try:
      cluster.fs.rmtree('/test-snappy-avro-filebrowser/')
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_view_snappy_compressed_avro():
  if not snappy_installed():
    raise SkipTest
  import snappy

  cluster = pseudo_hdfs4.shared_cluster()
  finish = []
  try:
    c = make_logged_in_client()
    cluster.fs.setuser(cluster.superuser)
    if cluster.fs.isdir("/test-snappy-avro-filebrowser"):
      cluster.fs.rmtree('/test-snappy-avro-filebrowser/')

    cluster.fs.mkdir('/test-snappy-avro-filebrowser/')

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
    f = cluster.fs.open('/test-snappy-avro-filebrowser/test-view.compressed.avro', "w")
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
    f = cluster.fs.open('/test-snappy-avro-filebrowser/test-view.compressed.avro', "r")
    assert_true('snappy' in f.read())
    f.close()

    # Snappy compressed succeed
    response = c.get('/filebrowser/view/test-snappy-avro-filebrowser/test-view.compressed.avro')
    assert_equal('avro', response.context['view']['compression'])
    assert_equal(eval(response.context['view']['contents']), dummy_datum, response)

  finally:
    for done in finish:
      done()
    try:
      cluster.fs.rmtree('/test-snappy-avro-filebrowser/')
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_view_avro():
  cluster = pseudo_hdfs4.shared_cluster()
  try:
    c = make_logged_in_client()
    cluster.fs.setuser(cluster.superuser)
    if cluster.fs.isdir("/test-avro-filebrowser"):
      cluster.fs.rmtree('/test-avro-filebrowser/')

    cluster.fs.mkdir('/test-avro-filebrowser/')

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

    f = cluster.fs.open('/test-avro-filebrowser/test-view.avro', "w")
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
    response = c.get('/filebrowser/view/test-avro-filebrowser/test-view.avro')
    # (Note: we use eval here cause of an incompatibility issue between
    # the representation string of JSON dicts in simplejson vs. json)
    assert_equal(eval(response.context['view']['contents']), dummy_datum)

    # offsetting should work as well
    response = c.get('/filebrowser/view/test-avro-filebrowser/test-view.avro?offset=1')
    assert_equal('avro', response.context['view']['compression'])

    f = cluster.fs.open('/test-avro-filebrowser/test-view2.avro', "w")
    f.write("hello")
    f.close()

    # we shouldn't autodetect non avro files
    response = c.get('/filebrowser/view/test-avro-filebrowser/test-view2.avro')
    assert_equal(response.context['view']['contents'], "hello")

    # we should fail to do a bad thing if they specify compression when it's not set.
    response = c.get('/filebrowser/view/test-avro-filebrowser/test-view2.avro?compression=gzip')
    assert_true('Failed to decompress' in response.context['message'])

  finally:
    try:
      cluster.fs.rmtree('/test-avro-filebrowser/')
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_view_parquet():
  cluster = pseudo_hdfs4.shared_cluster()
  try:
    c = make_logged_in_client()
    cluster.fs.setuser(cluster.superuser)
    if cluster.fs.isdir("/test-parquet-filebrowser"):
      cluster.fs.rmtree('/test-parquet-filebrowser/')

    cluster.fs.mkdir('/test-parquet-filebrowser/')

    # Parquet file encoded as hex.
    test_data = "50415231150015d40115d4012c15321500150615080000020000003201000000000100000002000000030000000400000005000000060000000700000008000000090000000a0000000b0000000c0000000d0000000e0000000f000000100000001100000012000000130000001400000015000000160000001700000018000000150015b60415b6042c1532150015061508000002000000320107000000414c474552494109000000415247454e54494e41060000004252415a494c0600000043414e41444105000000454759505408000000455448494f504941060000004652414e4345070000004745524d414e5905000000494e44494109000000494e444f4e45534941040000004952414e0400000049524151050000004a4150414e060000004a4f5244414e050000004b454e5941070000004d4f524f43434f0a0000004d4f5a414d42495155450400000050455255050000004348494e4107000000524f4d414e49410c00000053415544492041524142494107000000564945544e414d060000005255535349410e000000554e49544544204b494e47444f4d0d000000554e4954454420535441544553150015d40115d4012c1532150015061508000002000000320100000000010000000100000001000000040000000000000003000000030000000200000002000000040000000400000002000000040000000000000000000000000000000100000002000000030000000400000002000000030000000300000001000000150015d61e15d61e2c153215001506150800000200000032013300000020686167676c652e206361726566756c6c792066696e616c206465706f736974732064657465637420736c796c7920616761694c000000616c20666f7865732070726f6d69736520736c796c79206163636f7264696e6720746f2074686520726567756c6172206163636f756e74732e20626f6c6420726571756573747320616c6f6e6b0000007920616c6f6e6773696465206f66207468652070656e64696e67206465706f736974732e206361726566756c6c79207370656369616c207061636b61676573206172652061626f7574207468652069726f6e696320666f726765732e20736c796c79207370656369616c20650000006561732068616e672069726f6e69632c2073696c656e74207061636b616765732e20736c796c7920726567756c6172207061636b616765732061726520667572696f75736c79206f76657220746865207469746865732e20666c756666696c7920626f6c6463000000792061626f766520746865206361726566756c6c7920756e757375616c207468656f646f6c697465732e2066696e616c206475676f7574732061726520717569636b6c79206163726f73732074686520667572696f75736c7920726567756c617220641f00000076656e207061636b616765732077616b6520717569636b6c792e207265677526000000726566756c6c792066696e616c2072657175657374732e20726567756c61722c2069726f6e693a0000006c20706c6174656c6574732e20726567756c6172206163636f756e747320782d7261793a20756e757375616c2c20726567756c6172206163636f41000000737320657863757365732063616a6f6c6520736c796c79206163726f737320746865207061636b616765732e206465706f73697473207072696e742061726f756e7200000020736c796c792065787072657373206173796d70746f7465732e20726567756c6172206465706f7369747320686167676c6520736c796c792e206361726566756c6c792069726f6e696320686f636b657920706c617965727320736c65657020626c697468656c792e206361726566756c6c320000006566756c6c7920616c6f6e6773696465206f662074686520736c796c792066696e616c20646570656e64656e636965732e20420000006e6963206465706f7369747320626f6f73742061746f702074686520717569636b6c792066696e616c2072657175657374733f20717569636b6c7920726567756c61240000006f75736c792e2066696e616c2c20657870726573732067696674732063616a6f6c652061370000006963206465706f736974732061726520626c697468656c792061626f757420746865206361726566756c6c7920726567756c61722070615d0000002070656e64696e67206578637573657320686167676c6520667572696f75736c79206465706f736974732e2070656e64696e672c20657870726573732070696e746f206265616e732077616b6520666c756666696c79207061737420745a000000726e732e20626c697468656c7920626f6c6420636f7572747320616d6f6e672074686520636c6f73656c7920726567756c6172207061636b616765732075736520667572696f75736c7920626f6c6420706c6174656c6574733f2d000000732e2069726f6e69632c20756e757375616c206173796d70746f7465732077616b6520626c697468656c7920726a000000706c6174656c6574732e20626c697468656c792070656e64696e6720646570656e64656e636965732075736520666c756666696c79206163726f737320746865206576656e2070696e746f206265616e732e206361726566756c6c792073696c656e74206163636f756e5b0000006320646570656e64656e636965732e20667572696f75736c792065787072657373206e6f746f726e697320736c65657020736c796c7920726567756c6172206163636f756e74732e20696465617320736c6565702e206465706f736f000000756c6172206173796d70746f746573206172652061626f75742074686520667572696f7573206d756c7469706c696572732e206578707265737320646570656e64656e63696573206e61672061626f7665207468652069726f6e6963616c6c792069726f6e6963206163636f756e744e00000074732e2073696c656e7420726571756573747320686167676c652e20636c6f73656c792065787072657373207061636b6167657320736c656570206163726f73732074686520626c697468656c792e00000068656c7920656e746963696e676c792065787072657373206163636f756e74732e206576656e2c2066696e616c204f00000020726571756573747320616761696e73742074686520706c6174656c65747320757365206e65766572206163636f7264696e6720746f2074686520717569636b6c7920726567756c61722070696e743d00000065616e7320626f6f7374206361726566756c6c79207370656369616c2072657175657374732e206163636f756e7473206172652e206361726566756c6c6e000000792066696e616c207061636b616765732e20736c6f7720666f7865732063616a6f6c6520717569636b6c792e20717569636b6c792073696c656e7420706c6174656c657473206272656163682069726f6e6963206163636f756e74732e20756e757375616c2070696e746f2062651502195c48016d15080015022502180a6e6174696f6e5f6b657900150c250218046e616d650015022502180a726567696f6e5f6b657900150c2502180b636f6d6d656e745f636f6c001632191c194c26081c1502190519180a6e6174696f6e5f6b65791500163216fa0116fa01260800002682021c150c19051918046e616d651500163216dc0416dc04268202000026de061c1502190519180a726567696f6e5f6b65791500163216fa0116fa0126de06000026d8081c150c190519180b636f6d6d656e745f636f6c1500163216fc1e16fc1e26d80800001600163200280a706172717565742d6d7200ea00000050415231"

    f = cluster.fs.open('/test-parquet-filebrowser/test-parquet.parquet', "w")
    f.write(test_data.decode('hex'))

    # autodetect
    response = c.get('/filebrowser/view/test-parquet-filebrowser/test-parquet.parquet')

    assert_true('FRANCE' in response.context['view']['contents'])

  finally:
    try:
      cluster.fs.rmtree('/test-parquet-filebrowser/')
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_view_gz():
  cluster = pseudo_hdfs4.shared_cluster()
  try:
    c = make_logged_in_client()
    cluster.fs.setuser(cluster.superuser)
    if cluster.fs.isdir("/test-gz-filebrowser"):
      cluster.fs.rmtree('/test-gz-filebrowser/')

    cluster.fs.mkdir('/test-gz-filebrowser/')

    f = cluster.fs.open('/test-gz-filebrowser/test-view.gz', "w")
    sdf_string = '\x1f\x8b\x08\x082r\xf4K\x00\x03f\x00+NI\xe3\x02\x00\xad\x96b\xc4\x04\x00\x00\x00'
    f.write(sdf_string)
    f.close()

    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view.gz?compression=gzip')
    assert_equal(response.context['view']['contents'], "sdf\n")

    # autodetect
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view.gz')
    assert_equal(response.context['view']['contents'], "sdf\n")

    # ensure compression note is rendered
    assert_equal(response.context['view']['compression'], "gzip")
    assert_true('Output rendered from compressed' in response.content, response.content)

    # offset should do nothing
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view.gz?compression=gzip&offset=1')
    assert_true("Offsets are not supported" in response.context['message'], response.context['message'])

    f = cluster.fs.open('/test-gz-filebrowser/test-view2.gz', "w")
    f.write("hello")
    f.close()

    # we shouldn't autodetect non gzip files
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view2.gz')
    assert_equal(response.context['view']['contents'], "hello")

    # we should fail to do a bad thing if they specify compression when it's not set.
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view2.gz?compression=gzip')
    assert_true("Failed to decompress" in response.context['message'])

  finally:
    try:
      cluster.fs.rmtree('/test-gz-filebrowser/')
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_view_i18n():
  cluster = pseudo_hdfs4.shared_cluster()
  try:
    cluster.fs.setuser(cluster.superuser)
    cluster.fs.mkdir('/test-filebrowser/')

    # Test viewing files in different encodings
    content = u'pt-Olá en-hello ch-你好 ko-안녕 ru-Здравствуйте'
    view_helper(cluster, 'utf-8', content)
    view_helper(cluster, 'utf-16', content)

    content = u'你好-big5'
    view_helper(cluster, 'big5', content)

    content = u'こんにちは-shift-jis'
    view_helper(cluster, 'shift_jis', content)

    content = u'안녕하세요-johab'
    view_helper(cluster, 'johab', content)

    # Test that the default view is home
    c = make_logged_in_client()
    response = c.get('/filebrowser/view/')
    assert_equal(response.context['path'], '/')
    response = c.get('/filebrowser/view/?default_to_home=1')
    assert_equal("http://testserver/filebrowser/view/user/test", response["location"])
  finally:
    try:
      cluster.fs.rmtree('/test-filebrowser/')
    except Exception, ex:
      LOG.error('Failed to cleanup test directory: %s' % (ex,))


@attr('requires_hadoop')
def test_view_access():
  cluster = pseudo_hdfs4.shared_cluster()
  NO_PERM_DIR = u'/test-no-perm'

  try:
    c = make_logged_in_client()
    cluster.fs.setuser(cluster.superuser)
    cluster.fs.mkdir(NO_PERM_DIR, mode='700')

    response = c.get('/filebrowser/view/test-no-perm')
    assert_true('Cannot access' in response.context['message'])

    response = c.get('/filebrowser/view/test-does-not-exist')
    assert_true('Cannot access' in response.context['message'])
  finally:
    try:
      cluster.fs.rmtree(NO_PERM_DIR)
    except:
      pass      # Don't let cleanup errors mask earlier failures


@attr('requires_hadoop')
def test_index():
  HOME_DIR = u'/user/test'
  NO_HOME_DIR = u'/user/no_home'

  c = make_logged_in_client()
  c_no_home = make_logged_in_client(username='no_home')
  cluster = pseudo_hdfs4.shared_cluster()

  if not cluster.fs.exists(HOME_DIR):
    cluster.fs.create_home_dir(HOME_DIR)
  assert_false(cluster.fs.exists(NO_HOME_DIR))

  response = c.get('/filebrowser', follow=True)
  assert_equal(HOME_DIR, response.context['path'])
  assert_equal(HOME_DIR, response.context['home_directory'])

  response = c_no_home.get('/filebrowser', follow=True)
  assert_equal('/', response.context['path'])
  assert_equal(None, response.context['home_directory'])


def view_helper(cluster, encoding, content):
  """
  Write the content in the given encoding directly into the filesystem.
  Then try to view it and make sure the data is correct.
  """
  c = make_logged_in_client()
  filename = u'/test-filebrowser/test-view-carácter-internacional'
  bytestring = content.encode(encoding)

  try:
    f = cluster.fs.open(filename, "w")
    f.write(bytestring)
    f.close()

    response = c.get('/filebrowser/view%s?encoding=%s' % (filename, encoding))
    assert_equal(response.context['view']['contents'], content)

    response = c.get('/filebrowser/view%s?encoding=%s&end=8&begin=1' % (filename, encoding))
    assert_equal(response.context['view']['contents'],
                 unicode(bytestring[0:8], encoding, errors='replace'))
  finally:
    try:
      cluster.fs.remove(filename)
    except Exception, ex:
      LOG.error('Failed to cleanup %s: %s' % (filename, ex))


@attr('requires_hadoop')
def test_edit_i18n():
  cluster = pseudo_hdfs4.shared_cluster()
  try:
    cluster.fs.setuser(cluster.superuser)
    cluster.fs.mkdir('/test-filebrowser/')

    # Test utf-8
    pass_1 = u'en-hello pt-Olá ch-你好 ko-안녕 ru-Здравствуйте'
    pass_2 = pass_1 + u'yi-העלא'
    edit_helper(cluster, 'utf-8', pass_1, pass_2)

    # Test utf-16
    edit_helper(cluster, 'utf-16', pass_1, pass_2)

    # Test cjk
    pass_1 = u'big5-你好'
    pass_2 = pass_1 + u'世界'
    edit_helper(cluster, 'big5', pass_1, pass_2)

    pass_1 = u'shift_jis-こんにちは'
    pass_2 = pass_1 + u'世界'
    edit_helper(cluster, 'shift_jis', pass_1, pass_2)

    pass_1 = u'johab-안녕하세요'
    pass_2 = pass_1 + u'세상'
    edit_helper(cluster, 'johab', pass_1, pass_2)
  finally:
    try:
      cluster.fs.rmtree('/test-filebrowser/')
    except Exception, ex:
      LOG.error('Failed to remove tree /test-filebrowser: %s' % (ex,))


def edit_helper(cluster, encoding, contents_pass_1, contents_pass_2):
  """
  Put the content into the file with a specific encoding.
  """
  c = make_logged_in_client(cluster.superuser)

  # This path is non-normalized to test normalization too
  filename = u'//test-filebrowser//./test-edit-carácter-internacional with space and () en-hello pt-Olá ch-你好 ko-안녕 ru-Здравствуйте'

  # File doesn't exist - should be empty
  edit_url = '/filebrowser/edit' + filename
  response = c.get(edit_url)
  assert_equal(response.context['form'].data['path'], filename)
  assert_equal(response.context['form'].data['contents'], "")

  # Just going to the edit page and not hitting save should not
  # create the file
  assert_false(cluster.fs.exists(filename))

  try:
    # Put some data in there and post
    response = c.post("/filebrowser/save", dict(
        path=filename,
        contents=contents_pass_1,
        encoding=encoding), follow=True)
    assert_equal(response.context['form'].data['path'], filename)
    assert_equal(response.context['form'].data['contents'], contents_pass_1)

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
    assert_equal(response.context['form'].data['path'], filename)
    assert_equal(response.context['form'].data['contents'], contents_pass_2)
    f = cluster.fs.open(filename)
    assert_equal(f.read(), contents_pass_2.encode(encoding))
    assert_false('\r\n' in f.read()) # No CRLF line terminators
    f.close()

    # TODO(todd) add test for maintaining ownership/permissions
  finally:
    try:
      cluster.fs.remove(filename)
    except Exception, ex:
      LOG.error('Failed to remove %s: %s' % (smart_str(filename), ex))


@attr('requires_hadoop')
def test_upload_file():
  """Test file upload"""
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    USER_NAME = 'test'
    HDFS_DEST_DIR = "/tmp/fb-upload-test"
    LOCAL_FILE = __file__
    HDFS_FILE = HDFS_DEST_DIR + '/' + os.path.basename(__file__)

    cluster.fs.setuser(USER_NAME)
    client = make_logged_in_client(USER_NAME)

    cluster.fs.do_as_superuser(cluster.fs.mkdir, HDFS_DEST_DIR)
    cluster.fs.do_as_superuser(cluster.fs.chown, HDFS_DEST_DIR, USER_NAME, USER_NAME)
    cluster.fs.do_as_superuser(cluster.fs.chmod, HDFS_DEST_DIR, 0700)

    stats = cluster.fs.stats(HDFS_DEST_DIR)
    assert_equal(stats['user'], USER_NAME)
    assert_equal(stats['group'], USER_NAME)

    # Just upload the current python file
    resp = client.post('/filebrowser/upload/file?dest=%s' % HDFS_DEST_DIR, # GET param avoids infinite looping
                       dict(dest=HDFS_DEST_DIR, hdfs_file=file(LOCAL_FILE)))
    response = json.loads(resp.content)

    assert_equal(0, response['status'], response)
    stats = cluster.fs.stats(HDFS_FILE)
    assert_equal(stats['user'], USER_NAME)
    assert_equal(stats['group'], USER_NAME)

    f = cluster.fs.open(HDFS_FILE)
    actual = f.read()
    expected = file(LOCAL_FILE).read()
    assert_equal(actual, expected)

    # Upload again and so fails because file already exits
    resp = client.post('/filebrowser/upload/file?dest=%s' % HDFS_DEST_DIR,
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
      assert_true('Permission denied' in response['data'], response)
    except AttributeError:
      # Seems like a Django bug.
      # StopFutureHandlers() does not seem to work in test mode as it continues to MemoryFileUploadHandler after perm issue and so fails.
      pass
  finally:
    try:
      cluster.fs.remove(HDFS_DEST_DIR)
    except Exception, ex:
      pass

@attr('requires_hadoop')
def test_upload_zip():
  """Test archive upload"""
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    USER_NAME = 'test'
    HDFS_DEST_DIR = "/tmp/fb-upload-test"
    ZIP_FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/test.zip')
    HDFS_ZIP_FILE = HDFS_DEST_DIR + '/test.zip'
    HDFS_UNZIPPED_FILE = HDFS_DEST_DIR + '/test'

    cluster.fs.setuser(USER_NAME)
    client = make_logged_in_client(USER_NAME)

    cluster.fs.mkdir(HDFS_DEST_DIR)
    cluster.fs.chown(HDFS_DEST_DIR, USER_NAME)
    cluster.fs.chmod(HDFS_DEST_DIR, 0700)

    # Upload and unzip archive
    resp = client.post('/filebrowser/upload/archive?dest=%s' % HDFS_DEST_DIR,
                       dict(dest=HDFS_DEST_DIR, archive=file(ZIP_FILE)))
    response = json.loads(resp.content)
    assert_equal(0, response['status'], response)
    assert_false(cluster.fs.exists(HDFS_ZIP_FILE))
    assert_true(cluster.fs.isdir(HDFS_UNZIPPED_FILE))
    assert_true(cluster.fs.isfile(HDFS_UNZIPPED_FILE + '/test.txt'))

    # Upload archive
    resp = client.post('/filebrowser/upload/file?dest=%s' % HDFS_DEST_DIR,
                       dict(dest=HDFS_DEST_DIR, hdfs_file=file(ZIP_FILE)))
    response = json.loads(resp.content)
    assert_equal(0, response['status'], response)
    assert_true(cluster.fs.exists(HDFS_ZIP_FILE))
  finally:
    try:
      cluster.fs.remove(HDFS_DEST_DIR)
    except:
      pass

@attr('requires_hadoop')
def test_upload_tgz():
  """Test archive upload"""
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    USER_NAME = 'test'
    HDFS_DEST_DIR = "/tmp/fb-upload-test"
    TGZ_FILE = os.path.realpath('apps/filebrowser/src/filebrowser/test_data/test.tar.gz')
    HDFS_TGZ_FILE = HDFS_DEST_DIR + '/test.tar.gz'
    HDFS_DECOMPRESSED_FILE = HDFS_DEST_DIR + '/test'

    cluster.fs.setuser(USER_NAME)
    client = make_logged_in_client(USER_NAME)

    cluster.fs.mkdir(HDFS_DEST_DIR)
    cluster.fs.chown(HDFS_DEST_DIR, USER_NAME)
    cluster.fs.chmod(HDFS_DEST_DIR, 0700)

    # Upload and decompress archive
    resp = client.post('/filebrowser/upload/archive?dest=%s' % HDFS_DEST_DIR,
                       dict(dest=HDFS_DEST_DIR, archive=file(TGZ_FILE)))
    response = json.loads(resp.content)
    assert_equal(0, response['status'], response)
    assert_false(cluster.fs.exists(HDFS_TGZ_FILE))
    assert_true(cluster.fs.isdir(HDFS_DECOMPRESSED_FILE))
    assert_true(cluster.fs.isfile(HDFS_DECOMPRESSED_FILE + '/test.txt'))
    assert_equal(cluster.fs.read(HDFS_DECOMPRESSED_FILE + '/test.txt', 0, 4), "test")

    # Upload archive
    resp = client.post('/filebrowser/upload/file?dest=%s' % HDFS_DEST_DIR,
                       dict(dest=HDFS_DEST_DIR, hdfs_file=file(TGZ_FILE)))
    response = json.loads(resp.content)
    assert_equal(0, response['status'], response)
    assert_true(cluster.fs.exists(HDFS_TGZ_FILE))
  finally:
    try:
      cluster.fs.remove(HDFS_DEST_DIR)
    except:
      pass

def test_location_to_url():
  assert_equal('/filebrowser/view/var/lib/hadoop-hdfs', location_to_url('/var/lib/hadoop-hdfs', False))
  assert_equal('/filebrowser/view/var/lib/hadoop-hdfs', location_to_url('hdfs://localhost:8020/var/lib/hadoop-hdfs'))
  assert_equal('/filebrowser/view/', location_to_url('hdfs://localhost:8020'))
  assert_equal(None, location_to_url('thrift://10.0.0.1:9083'))

@attr('requires_hadoop')
def test_trash():
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    c = make_logged_in_client()
    USERNAME = 'test'
    cluster.fs.setuser(USERNAME)

    cluster.fs.do_as_superuser(cluster.fs.chown, '/user/%s' % USERNAME, USERNAME, USERNAME)

    HOME_TRASH_DIR = '/user/%s/.Trash/Current/user/%s' % (USERNAME, USERNAME)
    prefix = '/tmp/test_trash'
    PATH_1 = '/%s/1' % prefix
    cluster.fs.mkdir(prefix)
    cluster.fs.mkdir(PATH_1)

    c.post('/filebrowser/rmtree?skip_trash=true', dict(path=[HOME_TRASH_DIR]))

    # No trash folder
    response = c.get('/filebrowser/view/user/test?default_to_trash', follow=True)
    assert_equal([], response.redirect_chain)

    c.post('/filebrowser/rmtree', dict(path=[PATH_1]))

    # We have a trash folder so a redirect (Current not always there)
    response = c.get('/filebrowser/view/user/test?default_to_trash', follow=True)
    assert_true(any(['.Trash' in page for page, code in response.redirect_chain]), response.redirect_chain)

    c.post('/filebrowser/rmtree?skip_trash=true', dict(path=[HOME_TRASH_DIR]))

    # No home trash, just regular root trash
    response = c.get('/filebrowser/view/user/test?default_to_trash', follow=True)
    assert_true(any(['.Trash' in page for page, code in response.redirect_chain]), response.redirect_chain)
  finally:
    try:
      cluster.fs.rmtree(prefix)     # Clean up
    except:
      pass      # Don't let cleanup errors mask earlier failures

