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
from nose.plugins.attrib import attr
from hadoop import mini_cluster
from desktop.lib.django_test_util import make_logged_in_client
from nose.tools import assert_true, assert_false, assert_equal
import logging

LOG = logging.getLogger(__name__)

@attr('requires_hadoop')
def test_chown():
  cluster = mini_cluster.shared_cluster(conf=True)
  try:
    # Only the Hadoop superuser really has carte blanche here
    c = make_logged_in_client(cluster.superuser)
    cluster.fs.setuser(cluster.superuser)

    PATH = "/test-chown"
    cluster.fs.mkdir(PATH)
    c.post("/filebrowser/chown", dict(path=PATH, user="x", group="y"))
    assert_equal("x", cluster.fs.stats(PATH)["user"])
    assert_equal("y", cluster.fs.stats(PATH)["group"])
    c.post("/filebrowser/chown", dict(path=PATH, user="__other__", user_other="z", group="y"))
    assert_equal("z", cluster.fs.stats(PATH)["user"])

  finally:
    cluster.shutdown()

@attr('requires_hadoop')
def test_listdir():
  cluster = mini_cluster.shared_cluster(conf=True)
  try:
    c = make_logged_in_client()
    cluster.fs.setuser(cluster.superuser)

    # Delete if there's already something there
    if cluster.fs.isdir("/user/test"):
      cluster.fs.rmtree("/user/test")

    cluster.fs.mkdir('/test-filebrowser/listdir')
    response = c.get('/filebrowser/view/test-filebrowser/')
    paths = [f['path'] for f in response.context['files']]
    assert_true("/test-filebrowser/listdir" in paths)

    # test's home dir doesn't exist yet
    assert_false(response.context['home_directory'])

    # test's home directory now exists. Should be returned.
    cluster.fs.mkdir('/user/test')
    response = c.get('/filebrowser/view/test-filebrowser/')
    assert_equal(response.context['home_directory'], '/user/test')
  finally:
    cluster.shutdown()


@attr('requires_hadoop')
def test_view_gz():
  cluster = mini_cluster.shared_cluster(conf=True)
  try:
    c = make_logged_in_client()
    cluster.fs.setuser(cluster.superuser)

    if cluster.fs.isdir("/test-gz-filebrowser"):
      cluster.fs.rmtree('/test-gz-filebrowser/')

    cluster.fs.mkdir('/test-gz-filebrowser/')

    f = cluster.fs.open('/test-gz-filebrowser/test-view.gz', "w")
    sdf_string='\x1f\x8b\x08\x082r\xf4K\x00\x03f\x00+NI\xe3\x02\x00\xad\x96b\xc4\x04\x00\x00\x00'
    f.write(sdf_string)
    f.close()

    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view.gz?compression=gzip')
    assert_equal(response.context['view']['contents'], "sdf\n")

# autodetect
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view.gz')
    assert_equal(response.context['view']['contents'], "sdf\n")

#offset should do nothing
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view.gz?compression=gzip&offset=1')
    assert_false(response.context.has_key('view'))


    f = cluster.fs.open('/test-gz-filebrowser/test-view2.gz', "w")
    f.write("hello")
    f.close()

#we shouldn't autodetect  non gzip files
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view2.gz')
    assert_equal(response.context['view']['contents'], "hello")

#we should fail to do a bad thing if they specify compression when it's not set.
    response = c.get('/filebrowser/view/test-gz-filebrowser/test-view2.gz?compression=gzip')
    assert_false(response.context.has_key('view'))

  finally:
    cluster.shutdown()

@attr('requires_hadoop')
def test_view():
  cluster = mini_cluster.shared_cluster(conf=True)
  try:
    c = make_logged_in_client()
    cluster.fs.setuser(cluster.superuser)

    cluster.fs.mkdir('/test-filebrowser/')

    f = cluster.fs.open('/test-filebrowser/test-view', "w")
    f.write("hello")
    f.close()

    response = c.get('/filebrowser/view/test-filebrowser/test-view')
    assert_equal(response.context['view']['contents'], "hello")

    response = c.get('/filebrowser/view/test-filebrowser/test-view?end=2&begin=1')
    assert_equal(response.context['view']['contents'], "he")

    response = c.get('/filebrowser/view/')
    assert_equal(response.context['path'], '/')
    cluster.fs.mkdir('/user/test')
    cluster.fs.chown("/user/test", "test", "test")
    response = c.get('/filebrowser/view/?default_to_home=1')
    assert_equal("http://testserver/filebrowser/view/user/test", response["location"])
  finally:
    cluster.shutdown()


@attr('requires_hadoop')
def test_edit():
  cluster = mini_cluster.shared_cluster(conf=True)
  try:
    c = make_logged_in_client(cluster.superuser)
    cluster.fs.setuser(cluster.superuser)

    cluster.fs.mkdir('/test-filebrowser/')
    # File doesn't exist - should be empty
    test_path = '//test-filebrowser//test-edit'
    # (this path is non-normalized to test normalization too)
    edit_url = '/filebrowser/edit' + test_path
    response = c.get(edit_url)
    assert_equal(response.context['form'].data['path'],
                 test_path)
    assert_equal(response.context['form'].data['contents'], "")

    # Just going to the edit page and not hitting save should not
    # create the file
    assert_false(cluster.fs.exists(test_path))

    # Put some data in there and post
    new_contents = "hello world from editor"
    response = c.post("/filebrowser/save", dict(
        path=test_path,
        contents=new_contents), follow=True)
    assert_equal(response.context['form'].data['path'],
                 test_path)
    assert_equal(response.context['form'].data['contents'],
                 new_contents)

    # File should now exist
    assert_true(cluster.fs.exists(test_path))
    # And its contents should be what we expect
    f = cluster.fs.open(test_path)
    assert_equal(f.read(), new_contents)
    f.close()

    # We should be able to overwrite the file with another save
    new_contents = "hello world again from editor"
    response = c.post("/filebrowser/save", dict(
        path=test_path,
        contents=new_contents), follow=True)
    assert_equal(response.context['form'].data['path'],
                 test_path)
    assert_equal(response.context['form'].data['contents'],
                 new_contents)
    f = cluster.fs.open(test_path)
    assert_equal(f.read(), new_contents)
    f.close()

    # TODO(todd) add test for maintaining ownership/permissions
  finally:
    cluster.shutdown()
