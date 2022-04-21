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

import logging
import os
import subprocess
import sys
import time
from desktop.conf import TIME_ZONE
from django.core.management.base import BaseCommand
from hadoop import cluster
from hadoop import conf as hdfs_conf
from desktop.hue_curl import Curl
from liboozie.conf import OOZIE_URL, SECURITY_ENABLED as OOZIE_SECURITY_ENABLED
from search.conf import SOLR_URL, SECURITY_ENABLED as SOLR_SECURITY_ENABLED

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t, gettext as _
else:
  from django.utils.translation import ugettext_lazy as _t, ugettext as _

LOG = logging.getLogger(__name__)

DEFAULT_LOG_DIR = 'logs'
log_dir = os.getenv("DESKTOP_LOG_DIR", DEFAULT_LOG_DIR)

current_milli_time = lambda: int(round(time.time() * 1000))


def get_service_info(service):
  service_info = {}
  if service.lower() == 'solr':
    service_info['url'] = SOLR_URL.get()
    service_info['security_enabled'] = SOLR_SECURITY_ENABLED.get()
  if service.lower() == 'oozie':
    service_info['url'] = OOZIE_URL.get()
    service_info['security_enabled'] = OOZIE_SECURITY_ENABLED.get()
  if service.lower() == 'httpfs':
    hdfs_config = hdfs_conf.HDFS_CLUSTERS['default']
    service_info['url'] = hdfs_config.WEBHDFS_URL.get()
    service_info['security_enabled'] = hdfs_config.SECURITY_ENABLED.get()
  if service.lower() == 'rm':
    yarn_cluster = cluster.get_cluster_conf_for_job_submission()
    service_info['url'] = yarn_cluster.RESOURCE_MANAGER_API_URL.get()
    service_info['security_enabled'] = yarn_cluster.SECURITY_ENABLED.get()
  if service.lower() == 'jhs':
    yarn_cluster = cluster.get_cluster_conf_for_job_submission()
    service_info['url'] = yarn_cluster.HISTORY_SERVER_API_URL.get()
    service_info['security_enabled'] = yarn_cluster.SECURITY_ENABLED.get()
  if service.lower() == 'sparkhs':
    yarn_cluster = cluster.get_cluster_conf_for_job_submission()
    service_info['url'] = yarn_cluster.SPARK_HISTORY_SERVER_URL.get()
    service_info['security_enabled'] = yarn_cluster.SPARK_HISTORY_SERVER_SECURITY_ENABLED.get()

  if 'url' not in service_info:
    LOG.info("Hue does not have %s configured, cannot test %s" % (service, service))
  elif service_info['url'] is None:
    LOG.info("Hue does not have %s configured, cannot test %s" % (service, service))

  if service_info['url'].endswith('/'):
    service_info['url'] = service_info['url'][:-1]

  return service_info


def add_service_test(available_services, options='all', service_name=None, testname=None, suburl=None, method='GET',
                     teststring=None, test_options=None):
  if options['service'] == "all" or options['service'] == service_name.lower():
    if not service_name in available_services:
      service_info = get_service_info(service_name)
      url = service_info['url']
      security_enabled = service_info['security_enabled']
      available_services[service_name] = {}
      available_services[service_name]['url'] = url
      available_services[service_name]['security_enabled'] = security_enabled
    # Tests
    if not 'tests' in available_services[service_name]:
      available_services[service_name]['tests'] = {}
    if not testname in available_services[service_name]['tests']:
      for test_option in test_options.keys():
        suburl = suburl.replace(test_option, str(test_options[test_option]))
      available_services[service_name]['tests'][testname] = {}
      available_services[service_name]['tests'][testname]['url'] = '%s/%s' % (
        available_services[service_name]['url'], suburl)
      available_services[service_name]['tests'][testname]['method'] = method
      available_services[service_name]['tests'][testname]['test'] = teststring


class Command(BaseCommand):
  """
  Handler for renaming duplicate User objects
  """

  try:
    from optparse import make_option
    option_list = BaseCommand.option_list + (
      make_option("--service", help=_t("Comma separated services to test, all, httpfs, solr, oozie, rm, jhs, sparkhs."),
                  action="store", default='all', dest='service'),
      make_option("--testname", help=_t("Test for a given service, must only include one service name."),
                  action="store", default=None, dest='testname'),
      make_option("--testoptions", help=_t(
        "Comma separated list of options for test. IE: oozie_job=0000778-190820133637006-oozie-oozi-C,getlogs=true"),
                  action="store", default=None, dest='testoptions'),
      make_option("--showcurl", help=_t("Show curl commands."),
                  action="store_true", default=False, dest='showcurl'),
      make_option("--response", help=_t("Show entire REST response."),
                  action="store_true", default=False, dest='entireresponse'),
      make_option("--username", help=_t("User to doAs."),
                  action="store", default="admin", dest='username'),
      make_option("--verbose", help=_t("Verbose."),
                  action="store_true", default=False, dest='verbose'),
    )

  except AttributeError, e:
    baseoption_test = 'BaseCommand' in str(e) and 'option_list' in str(e)
    if baseoption_test:
      def add_arguments(self, parser):
        parser.add_argument("--service",
                            help=_t("Comma separated services to test, all, httpfs, solr, oozie, rm, jhs, sparkhs."),
                            action="store", default='all', dest='service'),
        parser.add_argument("--testname", help=_t("Test for a given service, must only include one service name."),
                            action="store", default=None, dest='testname'),
        parser.add_argument("--testoptions", help=_t(
          "Comma separated list of options for test. IE: oozie_job=0000778-190820133637006-oozie-oozi-C,getlogs=true"),
                            action="store", default=None, dest='testoptions'),
        parser.add_argument("--showcurl", help=_t("Show curl commands."),
                            action="store_true", default=False, dest='showcurl'),
        parser.add_argument("--response", help=_t("Show entire REST response."),
                            action="store_true", default=False, dest='entireresponse'),
        parser.add_argument("--username", help=_t("User to doAs."),
                            action="store", default="admin", dest='username'),
        parser.add_argument("--verbose", help=_t("Verbose."),
                            action="store_true", default=False, dest='verbose')
    else:
      LOG.warn(str(e))
      sys.exit(1)

  def handle(self, *args, **options):
    test_options = {}
    test_options['TIME_ZONE'] = TIME_ZONE.get()
    test_options['DOAS'] = options['username']
    test_options['NOW'] = current_milli_time()
    test_options['NOWLESSMIN'] = test_options['NOW'] - 60000
    if options['testoptions'] is not None:
      for test_option in options['testoptions'].split(','):
        option, option_value = test_option.split('=')
        test_options[option.upper()] = option_value

    test_services = options['service'].split(',')
    supported_services = ['all', 'httpfs', 'solr', 'oozie', 'rm', 'jhs', 'sparkhs']
    allowed_tests = {}
    allowed_tests['httpfs'] = {}
    allowed_tests['httpfs']['USERHOME'] = None

    allowed_tests['jhs'] = {}
    allowed_tests['jhs']['FINISHED'] = None

    allowed_tests['oozie'] = {}
    allowed_tests['oozie']['STATUS'] = None
    allowed_tests['oozie']['CONFIGURATION'] = None
    allowed_tests['oozie']['WORKFLOWS'] = None
    allowed_tests['oozie']['COORDS'] = None
    allowed_tests['oozie']['WORKFLOW'] = "oozie_id=0000001-190820133637006-oozie-oozi-W"
    allowed_tests['oozie']['WORKFLOWLOG'] = "oozie_id=0000001-190820133637006-oozie-oozi-W"
    allowed_tests['oozie']['WORKFLOWDEF'] = "oozie_id=0000001-190820133637006-oozie-oozi-W"
    allowed_tests['oozie']['COORD'] = "oozie_id=0000001-190820133637006-oozie-oozi-C"

    allowed_tests['rm'] = {}
    allowed_tests['rm']['CLUSTERINFO'] = None

    allowed_tests['solr'] = {}
    allowed_tests['solr']['JMX'] = None

    if options['testname'] is not None:
      if len(test_services) > 1 or "all" in test_services:
        LOG.warn("When using --testname you must only submit one service name and you must not use all")
        sys.exit(1)

      if options['testname'] not in allowed_tests[options['service'].lower()].keys():
        LOG.warn(
          "--testname %s not found in allowed_tests for service %s" % (options['testname'], options['service']))
        LOG.warn("Allowed tests for service:")
        for test in allowed_tests[options['service'].lower()].keys():
          if allowed_tests[options['service'].lower()][test] is None:
            testoptions = "NONE"
          else:
            testoptions = allowed_tests[options['service'].lower()][test]
          LOG.warn("testname: %s : testoptions: %s" % (test, testoptions))
        sys.exit(1)

    if not any(elem in test_services for elem in supported_services):
      LOG.warn("Your service list does not contain a supported service: %s" % options['service'])
      LOG.warn("Supported services: all, httpfs, solr, oozie, rm, jhs, sparkhs")
      LOG.warn("Format: httpfs,solr,oozie")
      sys.exit(1)

    if not all(elem in supported_services for elem in test_services):
      LOG.warn("Your service list contains an unsupported service: %s" % options['service'])
      LOG.warn("Supported services: all, httpfs, solr, oozie, rm, jhs, sparkhs")
      LOG.warn("Format: httpfs,solr,oozie")
      sys.exit(1)

    if options['service'] == 'sparkhs':
      LOG.warn("Spark History Server not supported yet")
      sys.exit(1)

    LOG.info("TEST: %s" % str(test_options['NOW']))
    LOG.info("Running REST API Tests on Services: %s" % options['service'])
    curl = Curl(verbose=options['verbose'])

    available_services = {}

    # Add Solr
    add_service_test(available_services, options=options, service_name="Solr", testname="JMX",
                     suburl='jmx', method='GET', teststring='solr.solrxml.location', test_options=test_options)

    # Add Oozie
    if options['testname'] is None or options['testname'].upper() == "STATUS":
      add_service_test(available_services, options=options, service_name="Oozie", testname="STATUS",
                       suburl='v1/admin/status?timezone=TIME_ZONE&user.name=hue&doAs=DOAS', method='GET',
                       teststring='{"systemMode":"NORMAL"}', test_options=test_options)

    elif options['testname'].upper() == 'CONFIGURATION':
      add_service_test(available_services, options=options, service_name="Oozie", testname="CONFIGURATION",
                       suburl='v2/admin/configuration?timezone=TIME_ZONE&user.name=hue&doAs=DOAS', method='GET',
                       teststring='{"oozie.email.smtp.auth', test_options=test_options)

    elif options['testname'].upper() == 'WORKFLOWS':
      add_service_test(available_services, options=options, service_name="Oozie", testname="WORKFLOWS",
                       suburl='v1/jobs?len=100&doAs=DOAS&filter=user=admin;startcreatedtime=-7d&user.name=hue&offset'
                              '=1&timezone=TIME_ZONE&jobtype=wf',
                       method='GET',
                       teststring='"workflows":[', test_options=test_options)

    elif options['testname'].upper() == 'WORKFLOW':
      add_service_test(available_services, options=options, service_name="Oozie", testname="WORKFLOW",
                       suburl='v1/job/OOZIE_ID?timezone=TIME_ZONE&suser.name=hue&logfilter=&doAs=DOAS', method='GET',
                       teststring='{"appName":', test_options=test_options)

    elif options['testname'].upper() == 'WORKFLOWLOG':
      add_service_test(available_services, options=options, service_name="Oozie", testname="WORKFLOWLOG",
                       suburl='v2/job/OOZIE_ID?timezone=TIME_ZONE&show=log&user.name=hue&logfilter=&doAs=DOAS',
                       method='GET',
                       teststring='org.apache.oozie.service.JPAService: SERVER', test_options=test_options)

    elif options['testname'].upper() == 'WORKFLOWDEF':
      add_service_test(available_services, options=options, service_name="Oozie", testname="WORKFLOWDEF",
                       suburl='v2/job/OOZIE_ID?timezone=TIME_ZONE&show=definition&user.name=hue&logfilter=&doAs=DOAS',
                       method='GET',
                       teststring='xmlns="uri', test_options=test_options)

    elif options['testname'].upper() == 'COORDS':
      add_service_test(available_services, options=options, service_name="Oozie", testname="COORDS",
                       suburl='v1/jobs?len=100&doAs=DOAS&filter=user=admin;startcreatedtime=-7d&user.name=hue&offset'
                              '=1&timezone=TIME_ZONE&jobtype=coord',
                       method='GET',
                       teststring='"coordinatorjobs":[', test_options=test_options)

    elif options['testname'].upper() == 'COORD':
      add_service_test(available_services, options=options, service_name="Oozie", testname="COORD",
                       suburl='v1/job/OOZIE_ID?timezone=TIME_ZONE&suser.name=hue&logfilter=&doAs=DOAS', method='GET',
                       teststring='{"appName":', test_options=test_options)

    # Add HTTPFS
    add_service_test(available_services, options=options, service_name="Httpfs", testname="USERHOME",
                     suburl='user/DOAS?op=GETFILESTATUS&user.name=hue&DOAS=%s', method='GET',
                     teststring='"type":"DIRECTORY"', test_options=test_options)

    # Add RM
    add_service_test(available_services, options=options, service_name="RM", testname="CLUSTERINFO",
                     suburl='ws/v1/cluster/info', method='GET', teststring='"clusterInfo"', test_options=test_options)

    # Add JHS
    add_service_test(available_services, options=options, service_name="JHS", testname="FINISHED",
                     suburl='ws/v1/history/mapreduce/jobs?finishedTimeBegin=NOWLESSMIN&finishedTimeEnd=NOW',
                     method='GET',
                     teststring='{"jobs"', test_options=test_options)

    for service in available_services:
      for service_test in available_services[service]['tests']:
        LOG.info("Running %s %s Test:" % (service, service_test))
        start_time = time.time()
        response = curl.do_curl_available_services(available_services[service]['tests'][service_test])
        returned_in = (time.time() - start_time) * 1000
        if available_services[service]['tests'][service_test]['test'] in response:
          LOG.info("TEST: %s %s: Passed in %dms: %s found in response" % (
            service, service_test, returned_in, available_services[service]['tests'][service_test]['test']))
          if options['entireresponse']:
            LOG.info("TEST: %s %s: Response: %s" % (service, service_test, response))
        else:
          LOG.info("TEST: %s %s: Failed in %dms: Response: %s" % (service, service_test, returned_in, response))

    log_file = log_dir + '/backend_test_curl.log'
    print ""
    print "Tests completed, view logs here: %s" % log_file
    print "Report:"
    cmd = 'grep -A1000 "%s" %s | grep "TEST:" | sed "s/.*INFO.*TEST:/  TEST:/g"' % (str(test_options['NOW']), log_file)
    grep_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    grep_response = grep_process.communicate()[0]
    print "%s" % grep_response
    print ""
    print "OS Repro Commands are:"
    cmd = 'grep -A1000 "%s" %s | grep "OSRUN:" | sed "s/.*INFO.*OSRUN:/  /g"' % (str(test_options['NOW']), log_file)
    grep_process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    grep_response = grep_process.communicate()[0]
    print "%s" % grep_response
