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
"""
Tests for filebrowser views
"""
from django.utils.encoding import smart_str
from nose.plugins.attrib import attr
from hadoop import pseudo_hdfs4
from avro import schema, datafile, io
from desktop.lib.django_test_util import make_logged_in_client
from nose.tools import assert_true, assert_false, assert_equal

try:
  import json
except ImportError:
  import simplejson as json

import logging
import urlparse

LOG = logging.getLogger(__name__)

@attr('requires_hadoop')
def test_chown():
  cluster = pseudo_hdfs4.shared_cluster()

  # Only the Hadoop superuser really has carte blanche here
  c = make_logged_in_client(cluster.superuser)
  cluster.fs.setuser(cluster.superuser)

  PATH = u"/test-chown-en-Español"
  cluster.fs.mkdir(PATH)
  c.post("/filebrowser/chown", dict(path=PATH, user="x", group="y"))
  assert_equal("x", cluster.fs.stats(PATH)["user"])
  assert_equal("y", cluster.fs.stats(PATH)["group"])
  c.post("/filebrowser/chown", dict(path=PATH, user="__other__", user_other="z", group="y"))
  assert_equal("z", cluster.fs.stats(PATH)["user"])

  # Make sure that the regular user chown form doesn't have useless fields,
  # and that the superuser's form has all the fields it could dream of.
  PATH = '/filebrowser/chown-regular-user'
  cluster.fs.mkdir(PATH)
  cluster.fs.chown(PATH, 'chown_test', 'chown_test')
  response = c.get('/filebrowser/chown', dict(path=PATH, user='chown_test', group='chown_test'))
  assert_true('<option value="__other__"' in response.content)
  c = make_logged_in_client('chown_test')
  response = c.get('/filebrowser/chown', dict(path=PATH, user='chown_test', group='chown_test'))
  assert_false('<option value="__other__"' in response.content)


@attr('requires_hadoop')
def test_listdir():
  cluster = pseudo_hdfs4.shared_cluster()
  try:
    c = make_logged_in_client(cluster.superuser)
    cluster.fs.setuser(cluster.superuser)

    # These paths contain non-ascii characters. Your editor will need the
    # corresponding font library to display them correctly.
    #
    # We test that mkdir can handle unicode strings as well as byte strings.
    # And even when the byte string can't be decoded properly (big5), the listdir
    # still succeeds.
    orig_paths = [
      u'greek-Ελληνικά',
      u'chinese-漢語',
      'listdir%20.,<>~`!@#$%^&()_-+="',
    ]

    prefix = '/test-filebrowser/'
    for path in orig_paths:
      c.post('/filebrowser/mkdir', dict(path=prefix, name=path))

    # Read the parent dir
    response = c.get('/filebrowser/view' + prefix)
    dir_listing = response.context['files']
    assert_equal(len(orig_paths) + 1, len(dir_listing))

    for dirent in dir_listing:
      path = dirent['name']
      if path == '..':
        continue

      assert_true(path in orig_paths)

      # Drill down into the subdirectory
      url = urlparse.urlsplit(dirent['url'])[2]
      resp = c.get(url)

      # We are actually reading a directory
      assert_equal('..', resp.context['files'][0]['name'],
                   "'%s' should be a directory" % (path,))

    # Delete user's home if there's already something there
    if cluster.fs.isdir("/user/test"):
      cluster.fs.rmtree("/user/test")
    assert_false(response.context['home_directory'])

    # test's home directory now exists. Should be returned.
    cluster.fs.mkdir('/user/test')
    c = make_logged_in_client()
    response = c.get('/filebrowser/view/test-filebrowser/')
    assert_equal(response.context['home_directory'], '/user/test')
  finally:
    try:
      cluster.fs.rmtree('/test-filebrowser')
      cluster.fs.rmtree('/user/test')
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
    assert_false(response.context.has_key('view'))

  finally:
    try:
      cluster.fs.rmtree('/test-avro-filebrowser/')
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

    # offset should do nothing
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view.gz?compression=gzip&offset=1')
    assert_false(response.context.has_key('view'))

    f = cluster.fs.open('/test-gz-filebrowser/test-view2.gz', "w")
    f.write("hello")
    f.close()

    # we shouldn't autodetect non gzip files
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view2.gz')
    assert_equal(response.context['view']['contents'], "hello")

    # we should fail to do a bad thing if they specify compression when it's not set.
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view2.gz?compression=gzip')
    assert_false(response.context.has_key('view'))

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
    cluster.fs.mkdir('/user/test')
    cluster.fs.chown("/user/test", "test", "test")
    response = c.get('/filebrowser/view/?default_to_home=1')
    assert_equal("http://testserver/filebrowser/view/user/test", response["location"])
  finally:
    try:
      cluster.fs.rmtree('/test-filebrowser/')
      cluster.fs.rmtree('/user/test')
    except Exception, ex:
      LOG.error('Failed to cleanup test directory: %s' % (ex,))


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
  filename = u'//test-filebrowser//./test-edit-carácter-internacional'

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
    f.close()

    # TODO(todd) add test for maintaining ownership/permissions
  finally:
    try:
      cluster.fs.remove(filename)
    except Exception, ex:
      LOG.error('Failed to remove %s: %s' % (smart_str(filename), ex))


@attr('requires_hadoop')
def test_upload():
  """Test file upload"""
  cluster = pseudo_hdfs4.shared_cluster()
  try:
    USER_NAME = cluster.fs.superuser
    cluster.fs.setuser(USER_NAME)
    DEST = "/tmp/fb-upload-test"
    client = make_logged_in_client(USER_NAME)

    # Just upload the current python file
    resp = client.post('/filebrowser/upload',
                       dict(dest=DEST, hdfs_file=file(__file__)))

    assert_true("View uploaded file" in resp.content)
    stats = cluster.fs.stats(DEST)
    assert_equal(stats['user'], USER_NAME)
    assert_equal(stats['group'], USER_NAME)

    f = cluster.fs.open(DEST)
    actual = f.read()
    expected = file(__file__).read()
    assert_equal(actual, expected)
  finally:
    try:
      cluster.fs.remove(DEST)
    except Exception, ex:
      pass
