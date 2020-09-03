/*
 * This file was originally copied from Apache Tez and has been modified. The modifications are subject to the
 * following provisions.
 *
 * HORTONWORKS DATAPLANE SERVICE AND ITS CONSTITUENT SERVICES
 *
 * (c) 2016-2018 Hortonworks, Inc. All rights reserved.
 *
 * This code is provided to you pursuant to your written agreement with Hortonworks, which may be the terms of the
 * Affero General Public License version 3 (AGPLv3), or pursuant to a written agreement with a third party authorized
 * to distribute this code.  If you do not have a written agreement with Hortonworks or with an authorized and
 * properly licensed third party, you do not have any rights to this code.
 *
 * If this code is provided to you under the terms of the AGPLv3:
 * (A) HORTONWORKS PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY KIND;
 * (B) HORTONWORKS DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT
 *   LIMITED TO IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE;
 * (C) HORTONWORKS IS NOT LIABLE TO YOU, AND WILL NOT DEFEND, INDEMNIFY, OR HOLD YOU HARMLESS FOR ANY CLAIMS ARISING
 *   FROM OR RELATED TO THE CODE; AND
 * (D) WITH RESPECT TO YOUR EXERCISE OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, HORTONWORKS IS NOT LIABLE FOR ANY
 *   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO,
 *   DAMAGES RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF BUSINESS ADVANTAGE OR UNAVAILABILITY,
 *   OR LOSS OR CORRUPTION OF DATA.
 *
 */

var buildInfo = require('./build-info');

module.exports = {
  // IDE side configurations
  SHOULD_PERFORM_SERVICE_CHECK: false,
  SHOULD_AUTO_REFRESH_TABLES: true,
  SHOULD_AUTO_REFRESH_DATABASES: true,

  // Search side configurations
  buildVersion: buildInfo.version || "",
  isStandalone: true, // Must be set false while running in wrapped mode
  rowLoadLimit: 9007199254740991,
  pollingInterval: 3000,

  hosts: {
    timeline: 'http://localhost:8188',
    rm: 'http://localhost:8088',
    studio: '/'
  },
  namespaces: {
    webService: {
      timeline: 'ws/v1/timeline',
      appHistory: 'ws/v1/applicationhistory',
      rm: 'ws/v1/cluster',
      am: 'proxy/{app_id}/ws/v{version:2}/tez',
      studio: 'api'
    },
    web: {
      rm: 'cluster'
    },
  },
  paths: {
    studio: {
      'indexed-query': "query/search",
      'suggested-search': 'suggested-searches',
      'facet': '{entity_type}/facets',
      'vertex': 'hive/vertices',
      'task-attempt': 'hive/task-attempts'
    },
    timeline: {
      dag: 'TEZ_DAG_ID',
      task: 'TEZ_TASK_ID',
      attempt: 'TEZ_TASK_ATTEMPT_ID',

      'dag-info': 'TEZ_DAG_EXTRA_INFO',
      'hive-query': 'HIVE_QUERY_ID',

      app: 'TEZ_APPLICATION'
    },
    am: {
      "dag-am": 'dagInfo',
      "vertex-am": 'verticesInfo',
      "task-am": 'tasksInfo',
      "attempt-am": 'attemptsInfo',
    },
    rm: {
      "app-rm": "apps"
    }
  },
  hrefs: {
    help: "https://github.com/hortonworks/hivestudio",
    license: "http://www.apache.org/licenses/LICENSE-2.0"
  },

  tables: {
    defaultColumns: {
      counters: [
        // File System Counters
        {
          counterName: 'FILE_BYTES_READ',
          counterGroupName: 'org.apache.tez.common.counters.FileSystemCounter',
        },
        {
          counterName: 'FILE_BYTES_WRITTEN',
          counterGroupName: 'org.apache.tez.common.counters.FileSystemCounter',
        },
        {
          counterName: 'FILE_READ_OPS',
          counterGroupName: 'org.apache.tez.common.counters.FileSystemCounter',
        },
        {
          counterName: 'FILE_LARGE_READ_OPS',
          counterGroupName: 'org.apache.tez.common.counters.FileSystemCounter',
        },
        {
          counterName: 'FILE_WRITE_OPS',
          counterGroupName: 'org.apache.tez.common.counters.FileSystemCounter',
        },
        {
          counterName: 'HDFS_BYTES_READ',
          counterGroupName: 'org.apache.tez.common.counters.FileSystemCounter',
        },
        {
          counterName: 'HDFS_BYTES_WRITTEN',
          counterGroupName: 'org.apache.tez.common.counters.FileSystemCounter',
        },
        {
          counterName: 'HDFS_READ_OPS',
          counterGroupName: 'org.apache.tez.common.counters.FileSystemCounter',
        },
        {
          counterName: 'HDFS_LARGE_READ_OPS',
          counterGroupName: 'org.apache.tez.common.counters.FileSystemCounter',
        },
        {
          counterName: 'HDFS_WRITE_OPS',
          counterGroupName: 'org.apache.tez.common.counters.FileSystemCounter',
        },

        // Task Counters
        {
          counterName: "NUM_SPECULATIONS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "REDUCE_INPUT_GROUPS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "REDUCE_INPUT_RECORDS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "SPLIT_RAW_BYTES",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "COMBINE_INPUT_RECORDS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "SPILLED_RECORDS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "NUM_SHUFFLED_INPUTS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "NUM_SKIPPED_INPUTS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "NUM_FAILED_SHUFFLE_INPUTS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "MERGED_MAP_OUTPUTS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "GC_TIME_MILLIS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "CPU_MILLISECONDS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "PHYSICAL_MEMORY_BYTES",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "VIRTUAL_MEMORY_BYTES",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "COMMITTED_HEAP_BYTES",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "INPUT_RECORDS_PROCESSED",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "OUTPUT_RECORDS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "OUTPUT_LARGE_RECORDS",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "OUTPUT_BYTES",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "OUTPUT_BYTES_WITH_OVERHEAD",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "OUTPUT_BYTES_PHYSICAL",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "ADDITIONAL_SPILLS_BYTES_WRITTEN",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "ADDITIONAL_SPILLS_BYTES_READ",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "ADDITIONAL_SPILL_COUNT",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "SHUFFLE_BYTES",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "SHUFFLE_BYTES_DECOMPRESSED",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "SHUFFLE_BYTES_TO_MEM",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "SHUFFLE_BYTES_TO_DISK",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "SHUFFLE_BYTES_DISK_DIRECT",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "NUM_MEM_TO_DISK_MERGES",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "NUM_DISK_TO_DISK_MERGES",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "SHUFFLE_PHASE_TIME",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "MERGE_PHASE_TIME",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "FIRST_EVENT_RECEIVED",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
        {
          counterName: "LAST_EVENT_RECEIVED",
          counterGroupName: "org.apache.tez.common.counters.TaskCounter",
        },
      ],

      dagCounters: [
        {
          counterName :"NUM_FAILED_TASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"NUM_KILLED_TASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"NUM_SUCCEEDED_TASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"TOTAL_LAUNCHED_TASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"OTHER_LOCAL_TASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"DATA_LOCAL_TASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"RACK_LOCAL_TASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"SLOTS_MILLIS_TASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"FALLOW_SLOTS_MILLIS_TASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"TOTAL_LAUNCHED_UBERTASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"NUM_UBER_SUBTASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },
        {
          counterName :"NUM_FAILED_UBERTASKS",
          counterGroupName :"org.apache.tez.common.counters.DAGCounter",
        },

        {
          counterName: "REDUCE_OUTPUT_RECORDS",
          counterGroupName: "REDUCE_OUTPUT_RECORDS",
        },
        {
          counterName: "REDUCE_SKIPPED_GROUPS",
          counterGroupName: "REDUCE_SKIPPED_GROUPS",
        },
        {
          counterName: "REDUCE_SKIPPED_RECORDS",
          counterGroupName: "REDUCE_SKIPPED_RECORDS",
        },
        {
          counterName: "COMBINE_OUTPUT_RECORDS",
          counterGroupName: "COMBINE_OUTPUT_RECORDS",
        },
        {
          counterName: "SKIPPED_RECORDS",
          counterGroupName: "SKIPPED_RECORDS",
        },
        {
          counterName: "INPUT_GROUPS",
          counterGroupName: "INPUT_GROUPS",
        }
      ]
    }
  },

  // Here you can pass flags/options to your application instance
  // when it is created
  SHOULD_PERFORM_SERVICE_CHECK: false,
  SHOULD_AUTO_REFRESH_TABLES: true,
  SHOULD_AUTO_REFRESH_DATABASES: true

};
