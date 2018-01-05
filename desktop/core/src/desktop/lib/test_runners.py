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

import sys
import threading

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test.signals import template_rendered

from django_nose.runner import NoseTestSuiteRunner, translate_option
from mako import runtime
from mako.template import Template


__all__ = ['HueTestRunner']

# Capturing the mako context is not thread safe, so we wrap rendering in a mutex.
_MAKO_LOCK = threading.RLock()


def _instrumented_test_render(self, *args, **data):
    """
    An instrumented Template render method, providing a signal
    that can be intercepted by the test system Client
    """

    with _MAKO_LOCK:
      def mako_callable_(context, *args, **kwargs):
        template_rendered.send(sender=self, template=self, context=context)
        return self.original_callable_[-1](context, *args, **kwargs)

      if hasattr(self, 'original_callable_'):
        self.original_callable_.append(self.callable_)
      else:
        self.original_callable_ = [self.callable_]

      self.callable_ = mako_callable_
      try:
        response = runtime._render(self, self.original_callable_[-1], args, data)
      finally:
        self.callable_ = self.original_callable_.pop()

      return response


class HueTestRunner(NoseTestSuiteRunner):
  __test__ = False


  def setup_test_environment(self, **kwargs):
    super(HueTestRunner, self).setup_test_environment(**kwargs)
    Template.original_render = Template.render
    Template.render = _instrumented_test_render


  def teardown_test_environment(self, **kwargs):
    super(HueTestRunner, self).teardown_test_environment(**kwargs)
    Template.render = Template.original_render
    del Template.original_render


  def run_tests(self, test_labels, *args):
    nose_argv = (['nosetests'] + list(test_labels))

    if args:
      nose_argv.extend(args)

    if hasattr(settings, 'NOSE_ARGS'):
      nose_argv.extend(settings.NOSE_ARGS)

    # Skip over 'manage.py test' and any arguments handled by django.
    django_opts = ['--noinput', '--liveserver', '-p', '--pattern']
    #for opt in BaseCommand.option_list:
    #  django_opts.extend(opt._long_opts)
    #  django_opts.extend(opt._short_opts)

    nose_argv.extend(translate_option(opt) for opt in sys.argv[1:]
    if opt.startswith('-') and not any(opt.startswith(d) for d in django_opts))

    # if --nose-verbosity was omitted, pass Django verbosity to nose
    if ('--verbosity' not in nose_argv and not any(opt.startswith('--verbosity=') for opt in nose_argv)):
      nose_argv.append('--verbosity=%s' % str(self.verbosity))

    if self.verbosity >= 1:
      print(' '.join(nose_argv))

    result = self.run_suite(nose_argv)
    # suite_result expects the suite as the first argument.  Fake it.
    return self.suite_result({}, result)
