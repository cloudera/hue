/*
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

import Ember from 'ember';

import LoaderSerializer from './loader';

function getProcessorClass(source) {
  var name = Ember.get(source, 'classname') || "";
  return name.substr(name.lastIndexOf('.') + 1);
}

export default LoaderSerializer.extend({
  extractArrayPayload: function (payload) {
    return payload.vertices;
  },

  maps: {
    entityID: 'vertexId',
    name: 'name',
    status: 'status',

    initTime: 'initRequestedTime',
    startTime: 'startTime',
    endTime: 'endTime',
    firstTaskStartTime: 'stats.firstTaskStartTime',
    lastTaskFinishTime: 'stats.lastTaskFinishTime',

    totalTasks: 'taskCount',
    failedTasks: 'failedTaskCount',
    succeededTasks: 'succeededTaskCount',
    killedTasks: 'killedTaskCount',

    failedTaskAttempts: 'failedTaskAttemptCount',
    killedTaskAttempts: 'killedTaskAttemptCount',

    minDuration:  'stats.minTaskDuration',
    maxDuration:  'stats.maxTaskDuration',
    avgDuration:  'stats.avgTaskDuration',

    firstTasksToStart:  'stats.firstTasksToStart',
    lastTasksToFinish:  'stats.lastTasksToFinish',
    shortestDurationTasks:  'stats.shortestDurationTasks',
    longestDurationTasks:  'stats.longestDurationTasks',

    processorClassName: getProcessorClass,

    dagID: '',

//    servicePlugin: 'otherinfo.servicePlugin',
  }
});
