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
import ENV from '../config/environment';

const SORT_OPTIONS = [
  {
    title: "Start Time",
    field: "startTime"
  },
  {
    title: "Finish Time",
    field: "finishTime"
  },
  {
    title: "Time Taken",
    field: "timeTaken"
  }
];

const FILTER_OPTIONS = [{
  description: "Top 20 longest running tasks",
  status: undefined,
  sort: SORT_OPTIONS[2],
  sortDesc: true,
  limit: 20
}, {
  description: "20 Errored tasks",
  status: "ERROR",
  sort: undefined,
  limit: 20
}, {
  description: "20 tasks which started last",
  status: undefined,
  sort: SORT_OPTIONS[0],
  sortDesc: true,
  limit: 20
}];

const STATUS_OPTIONS = [
  "NEW",
  "STARTING",
  "RUNNING",
  "SUCCEEDED",
  "FAILED",
  "KILLED"
];

const GROUPBY_OPTIONS = [{
  title: "Task Attempt",
  description: "No Grouping",
  field: "taskAttemptId"
}, {
  title: "Task",
  description: "Tasks",
  field: "taskId"
}, {
  title: "Container",
  description: "Containers",
  field: "containerId"
}, {
  title: "Node",
  description: "Nodes",
  field: "nodeId"
}];

const LIMIT_OPTIONS =  [5, 10, 20, 25, 50, 100];

const ZOOM_OPTIONS =  ["Vertex Time", "Visible Task Attempts"];

export default Ember.Component.extend({

  classNames: ["task-attempt-swimlane"],

  env: ENV,

  non: "",

  filterOption: FILTER_OPTIONS[0],
  filterOptions: FILTER_OPTIONS,

  limitOptions: LIMIT_OPTIONS,
  statusOptions: STATUS_OPTIONS,
  sortOptions: SORT_OPTIONS,

  groupBy: GROUPBY_OPTIONS[0],
  groupByOptions: GROUPBY_OPTIONS,

  zoomOption: ZOOM_OPTIONS[0],
  zoomOptions: ZOOM_OPTIONS,

  tooltipContents: null,
  selectedAttempt: null,

  query: null,
  vertex: null,
  taskAttempts: null,

  filterOptionDescription: Ember.computed("filterOption", function () {
    let filterOption = this.get("filterOption"),
        desc = filterOption.description;

    if(!desc) {
      let descArr = [filterOption.limit];

      if(filterOption.status) {
        descArr.push(filterOption.status.toLocaleLowerCase());
      }
      descArr.push("tasks");

      if(filterOption.sort) {
        descArr.push("in");
        descArr.push(filterOption.sortDesc ? "decreasing" : "increasing");
        descArr.push("order of", filterOption.sort.title.toLocaleLowerCase());
      }

      desc = descArr.join(" ");
    }

    return desc;
  }),

  timeData: Ember.computed("zoomOption", "vertex", "taskAttempts", function () {
    if(this.get("zoomOption") == "Vertex Time") {
      return {
        minTime: this.get("vertex.startTime"),
        maxTime: this.get("vertex.endTime"),
        timeWindow: this.get("vertex.duration")
      };
    }

    var taskAttempts = this.get("taskAttempts");

    if(taskAttempts && taskAttempts.get("length") > 0) {
      let minTime = Ember.get(taskAttempts, "firstObject.startTime"),
        maxTime = minTime;

      taskAttempts.forEach(function (attempt) {
        if(minTime > attempt.get("startTime")) {
          minTime = attempt.get("startTime");
        }
        if(maxTime < attempt.get("finishTime")) {
          maxTime = attempt.get("finishTime");
        }
      });

      return {
        minTime: minTime,
        maxTime: maxTime,
        timeWindow: maxTime - minTime
      };
    }

    return null;
  }),

  groupedTaskAttempts: Ember.computed("taskAttempts", "groupBy", "timeData", function () {
    var groupHash = {},
        groupArray = [],
        groupField = this.get("groupBy.field"),
        taskAttempts = this.get("taskAttempts");

    if(taskAttempts) {
      let {minTime, maxTime, timeWindow} = this.get("timeData");

      taskAttempts.forEach(function (attempt) {
        let groupId = Ember.get(attempt, groupField),
            groupObj = groupHash[groupId];

        if(!groupObj) {
          groupObj = {
            groupId: groupId,
            attempts: []
          };

          groupHash[groupId] = groupObj;
          groupArray.push(groupObj);
        }

        if(attempt.get("finishTime") == undefined) {
          attempt.set("finishTime", maxTime);
        }

        Ember.set(attempt, "left", ((attempt.get("startTime") - minTime) / timeWindow) * 100);
        Ember.set(attempt, "right", ((maxTime - attempt.get("finishTime")) / timeWindow) * 100);

        groupObj.attempts.push(attempt);
      });
    }

    Ember.run.later(this, "renderBars", 200);

    return groupArray;
  }),

  sendLoadData: function () {
    let sort = this.get("filterOption.sort");
    if(sort) {
      sort = sort.field + ":" + (this.get("filterOption.sortDesc") ? "desc" : "asc");
    }
    this.sendAction("loadData", this.get("filterOption.status"), sort, this.get("filterOption.limit"));
  },

  renderBars: function () {
    if(this.$()) {
      this.$().find(".attempt-bar").each(function (index, element) {
        var element = Ember.$(element);
        element.css({
          left: element.data("left") + "%",
          right: element.data("right") + "%",
        });
      });
    }
  },

  didInsertElement: function () {
    this.sendLoadData();
    this.$().find('.dropdown>button').dropdown();
  },

  updateFilter: function (option) {
    this.set("filterOption", Object.assign({}, option));
    this.sendLoadData();
  },

  createCustomFilterObj: function () {
    var filterOptions = this.get("filterOption");
    return {
      status: filterOptions.status,
      sort: filterOptions.sort,
      sortDesc: filterOptions.sortDesc,
      limit: filterOptions.limit
    };
  },

  actions: {
    filterChanged: function (option) {
      this.updateFilter(option);
    },

    statusChanged: function (status) {
      var filterOptions = this.createCustomFilterObj();
      filterOptions.status = status;
      this.updateFilter(filterOptions);
    },
    limitChanged: function (limit) {
      var filterOptions = this.createCustomFilterObj();
      filterOptions.limit = limit;
      this.updateFilter(filterOptions);
    },
    sortChanged: function (index) {
      var filterOptions = this.createCustomFilterObj();
      filterOptions.sort = SORT_OPTIONS[index];
      this.updateFilter(filterOptions);
    },
    toggleSortOrder: function () {
      var filterOptions = this.createCustomFilterObj();
      filterOptions.sortDesc = !filterOptions.sortDesc;
      this.updateFilter(filterOptions);
    },

    groupByChanged: function (option) {
      this.set("groupBy", option);
    },
    zoomChanged: function (option) {
      this.set("zoomOption", option);
    },

    attemptClicked: function (selectedAttempt) {
      this.set("selectedAttempt", selectedAttempt);
    },
    actionBarrier: function(){}
  }

});
