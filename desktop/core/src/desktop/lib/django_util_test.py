# Tests for django_util
# Some parts based on http://www.djangosnippets.org/snippets/1044/
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

import datetime

from nose.tools import assert_true, assert_equal, assert_not_equal, assert_raises
from django.http import HttpResponse, HttpResponseRedirect

from desktop.lib.django_test_util import configure_django_for_test, create_tables
from desktop.lib.django_util import reverse_with_get, timesince, humanize_duration
configure_django_for_test()

from desktop.lib import django_util, exceptions
from django.db import models

class TestModel(models.Model):
  class Meta:
    app_label = "TEST_APP"

  my_int = models.IntegerField()
  my_str = models.TextField(max_length=100)
  last_modified = models.DateTimeField(auto_now=True)

class TestDjangoUtil(object):
  def test_update_if_dirty(self):
    """
    Tests that update_if_dirty works.
    We use the last_modified field as a proxy for knowing
    whether or not we actually did a save.
    """
    create_tables(TestModel)
    x = TestModel()
    x.my_int = 3
    x.my_string = "foo"
    x.save()
    last_mod = x.last_modified

    django_util.update_if_dirty(x, my_int=3, my_string="bar")
    assert_not_equal(x.last_modified, last_mod)
    last_mod = x.last_modified

    django_util.update_if_dirty(x, my_int=3, my_string="bar")
    assert_equal(x.last_modified, last_mod)

    x.delete()

  def test_encode_json_unrenderable(self):
    class Foo(object):
      pass
    assert_raises(TypeError, django_util.encode_json, [ Foo() ])

  def test_get_app_nice_name(self):
    assert_equal('File Browser', django_util.get_app_nice_name('filebrowser'))

  def test_encode_json_model(self):
    assert_equal('{"model": "TEST_APP.testmodel", "pk": null, "fields": {"my_int": 3, "my_str": "foo", "last_modified": null}}',
        django_util.encode_json(TestModel(my_int=3, my_str="foo")))
    assert_equal('[{"model": "TEST_APP.testmodel", "pk": null, "fields": {"my_int": 3, "my_str": "foo", "last_modified": null}}]',
        django_util.encode_json([TestModel(my_int=3, my_str="foo")]))
  
  def test_timesince(self):
    assert_equal(timesince(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(1000)), "16 minutes, 40 seconds")
    assert_equal(timesince(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(60)), "1 minute")
    assert_equal(timesince(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(1)), "1 second")
    assert_equal(timesince(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(2)), "2 seconds")
    assert_equal(timesince(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(10000)), "2 hours, 46 minutes")

    assert_equal(timesince(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(1000), abbreviate=True), "16m, 40s")
    assert_equal(timesince(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(60), abbreviate=True), "1m")
    assert_equal(timesince(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(1), abbreviate=True), "1s")
    assert_equal(timesince(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(2), abbreviate=True), "2s")
    assert_equal(timesince(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(10000), abbreviate=True), "2h, 46m")

  def test_humanize_duration(self):

    assert_equal(humanize_duration(seconds=1000), "16 minutes, 40 seconds")
    assert_equal(humanize_duration(seconds=60), "1 minute")
    assert_equal(humanize_duration(seconds=1), "1 second")
    assert_equal(humanize_duration(seconds=2), "2 seconds")
    assert_equal(humanize_duration(seconds=10000), "2 hours, 46 minutes")

    assert_equal(humanize_duration(seconds=1000, abbreviate=True), "16m, 40s")
    assert_equal(humanize_duration(seconds=60, abbreviate=True), "1m")
    assert_equal(humanize_duration(seconds=1, abbreviate=True), "1s")
    assert_equal(humanize_duration(seconds=2, abbreviate=True), "2s")


  def test_encode_json_to_jsonable(self):
    class Foo(object):
      def to_jsonable(self):
        return "foo"
    assert_equal('"foo"', django_util.encode_json(Foo()))
    assert_equal('["foo", "foo"]', django_util.encode_json([Foo(), Foo()]))
    assert_equal('{"model": "TEST_APP.testmodel", "pk": null, "fields": {"my_int": 3, "my_str": "foo", "last_modified": null}}',
        django_util.encode_json(TestModel(my_int=3, my_str="foo")))

    class Bar(object):
      to_jsonable = "not a callable"
    assert_raises(TypeError, django_util.encode_json, [ Bar() ])

  def test_encode_json_thrift(self):
    # TODO(philip): I've avoided writing this because
    # I don't want to modify sys.path to include the gen-py stuff.
    pass

  def test_render_json_jsonp(self):
    assert_equal("foo(3);", django_util.render_json(3, jsonp_callback="foo").content)

  def test_render_json_jsonp_bad_name(self):
    # Bad names
    for x in [r"%evil-name", "3vil", "", "evil%"]:
      assert_raises(django_util.IllegalJsonpCallbackNameException,
        django_util.render_json, "whatever-value", x)
    # Fine names
    for x in ["a", "$", "_", "a9", "a9$"]:
      django_util.render_json("whatever-value", x)


  def test_exceptions(self):
    msg = "b0rked file"
    the_file = "foobar"
    try:
      raise exceptions.MessageException(msg, the_file)
    except Exception, e:
      assert_equal(msg, e.message)
      assert_equal(the_file, e.data['filename'])
      assert_true(msg in str(e))


def test_popup_injection():
  """Test that result injection works"""
  base = HttpResponse('<html><head></head><body>Hello</body></html>')
  resp = django_util.render_injected(base, ' Cookie monster')
  assert_true('Hello Cookie monster' in resp.content)

  redirect = HttpResponseRedirect('http://www.cnn.com')
  resp = django_util.render_injected(redirect, 'Cookie monster')
  assert_true('Cookie monster' not in resp.content)

  json = django_util.render_json('blah')
  resp = django_util.render_injected(json, 'Cookie monster')
  assert_true('Cookie monster' not in resp.content)

  assert_raises(AssertionError, django_util.render_injected, "foo", "bar")

def test_reverse_with_get():
  # Basic view
  assert_equal("/", reverse_with_get("desktop_views.index"))
  # Arguments for the view
  assert_equal("/desktop/api2/user_preferences/foo", reverse_with_get("desktop.api2.user_preferences", kwargs=dict(key="foo")))
  # Arguments for the view as well as GET parameters
  assert_equal("/desktop/api2/user_preferences/foo?a=1&b=2",
    reverse_with_get("desktop.api2.user_preferences", kwargs=dict(key="foo"), get=dict(a=1,b=2)))
  # You can use a list of args instead of kwargs, too
  assert_equal("/desktop/api2/user_preferences/foo?a=1&b=2",
    reverse_with_get("desktop.api2.user_preferences", args=["foo"], get=dict(a=1,b=2)))
  # Just GET parameters
  assert_equal("/?a=1", reverse_with_get("desktop_views.index", get=dict(a="1")))
  # No GET parameters
  assert_equal("/", reverse_with_get("desktop_views.index", get=dict()))

def test_unicode_ok():
  assert_equal("/?a=x%C3%A9", reverse_with_get("desktop_views.index", get=dict(a="x" + unichr(233))))
