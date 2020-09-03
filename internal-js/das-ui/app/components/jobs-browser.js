/*
 * This file was originally copied from Apache Ambari and has been modified. The modifications are subject to the
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

export default Ember.Component.extend({
  startTime: null,
  endTime: null,
  maxEndTime: null,
  statusFilter: null,
  titleFilter: null,
  jobId: {'asc':true},
  title: {'noSort':true},
  status: {'noSort':true},
  dateSubmitted: {'noSort':true},
  duration: {'noSort':true},
  sortProp:['id:desc'],
  sortedJobs: Ember.computed.sort('jobs', function (m1, m2) {
    if (m1.get('dateSubmitted') < m2.get('dateSubmitted')) {
      return 1;
    } else if (m1.get('dateSubmitted') > m2.get('dateSubmitted')) {
      return -1;
    }
    return 0;
  }),

  titleFilteredJobs: Ember.computed('sortedJobs', 'titleFilter', function() {
    if (!Ember.isEmpty(this.get('titleFilter'))) {
      return (this.get('sortedJobs').filter((entry) => entry.get('title').toLowerCase().indexOf(this.get('titleFilter').toLowerCase()) >= 0));
    } else {
      return this.get('sortedJobs');
    }
  }),

  filteredJobs: Ember.computed('titleFilteredJobs', 'statusFilter', 'sortProp', function () {
    if (this.get('statusFilter')) {
      return  this.get('titleFilteredJobs').filter((entry) => entry.get('status').toLowerCase() === this.get('statusFilter'));
    } else {
      return this.get('titleFilteredJobs');
    }
  }),

  filteredJobsSorted: Ember.computed.sort('filteredJobs', 'sortProp'),

  statusCounts: Ember.computed('titleFilteredJobs', function () {
    return this.get('titleFilteredJobs').reduce((acc, item, index) => {
      let status = item.get('status').toLowerCase();
      if (Ember.isEmpty(acc[status])) {
        acc[status] = 1;
      } else {
        acc[status] = acc[status] + 1;
      }
      return acc;
    }, {});
  }),


  actions: {
    sort(sortProp, sortField, key) {
      let perm = {};
      perm[key] = true;
      this.set(sortField, perm);
      this.set('sortProp', [sortProp]);
    },

    setDateRange(startDate, endDate) {
      this.sendAction('filterChanged', startDate, endDate);
    },

    selectJobForStatus(status) {
      let s = status.toLowerCase();
      if (s === 'all') {
        this.set('statusFilter');
      } else {
        this.set('statusFilter', s);
      }
    },

    clearTitleFilter() {
      this.set('titleFilter');
    }
  }
});
