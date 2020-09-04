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

import Ember from 'ember';

import DAGInfoSerializer from './dag-info';

var MoreObject = more.Object;

function getStatus(source) {
  var status = Ember.get(source, 'otherinfo.status') || Ember.get(source, 'primaryfilters.status.0'),
      event = source.events;

  if(!status && event) {
    if(event.findBy('eventtype', 'DAG_STARTED')) {
      status = 'RUNNING';
    }
  }

  return status;
}

function getStartTime(source) {
  var time = Ember.get(source, 'otherinfo.startTime'),
      event = source.events;

  if(!time && event) {
    event = event.findBy('eventtype', 'DAG_STARTED');
    if(event) {
      time = event.timestamp;
    }
  }

  return time;
}

function getEndTime(source) {
  var time = Ember.get(source, 'otherinfo.endTime'),
      event = source.events;

  if(!time && event) {
    event = event.findBy('eventtype', 'DAG_FINISHED');
    if(event) {
      time = event.timestamp;
    }
  }

  return time;
}

function getContainerLogs(source) {
  var containerLogs = [],
      otherinfo = Ember.get(source, 'otherinfo');

  if(!otherinfo) {
    return undefined;
  }

  for (var key in otherinfo) {
    if (key.indexOf('inProgressLogsURL_') === 0) {
      let logs = Ember.get(source, 'otherinfo.' + key);
      if (logs.indexOf('http') !== 0) {
        logs = 'http://' + logs;
      }
      let attemptID = key.substring(18);
      containerLogs.push({
        text : attemptID,
        href: logs
      });
    }
  }

  return containerLogs;
}

function getIdNameMap(source) {
  var nameIdMap = Ember.get(source, 'otherinfo.vertexNameIdMapping'),
      idNameMap = {};

  if(nameIdMap) {
    MoreObject.forEach(nameIdMap, function (name, id) {
      idNameMap[id] = name;
    });
  }

  return idNameMap;
}

export default DAGInfoSerializer.extend({
  maps: {
    name: 'primaryfilters.dagName.0',

    submitter: 'primaryfilters.user.0',

    callerID: 'primaryfilters.callerId.0',

    atsStatus: getStatus,
    // progress

    startTime: getStartTime,
    endTime: getEndTime,
    // duration

    // appID
    domain: 'domain',

    queueName: 'otherinfo.queueName',

    containerLogs: getContainerLogs,

    vertexIdNameMap: getIdNameMap,
    vertexNameIdMap: 'otherinfo.vertexNameIdMapping',

    amWsVersion: 'otherinfo.amWebServiceVersion',
  }
});
