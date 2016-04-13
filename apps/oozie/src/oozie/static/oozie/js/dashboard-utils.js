// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


function getStatusClass(status, prefix) {
  if (prefix == null) {
    prefix = "label-";
  }
  var klass = "";
  if (['SUCCEEDED', 'OK', 'DONE'].indexOf(status) > -1) {
    klass = prefix + "success";
  }
  else if (['RUNNING', 'READY', 'PREP', 'WAITING', 'SUSPENDED', 'PREPSUSPENDED', 'PREPPAUSED', 'PAUSED',
    'SUBMITTED',
    'SUSPENDEDWITHERROR',
    'PAUSEDWITHERROR'].indexOf(status) > -1) {
    klass = prefix + "warning";
  }
  else if (status == "IGNORED") {
    klass = prefix + "ignored";
  }
  else {
    klass = prefix + "important";
    if (prefix == "bar-") {
      klass = prefix + "danger";
    }
  }
  return klass;
}

function emptyStringIfNull(obj) {
  if (obj != null && obj != undefined) {
    return obj;
  }
  return "";
}

var PersistedButtonsFilters = function (oSettings, aData, iDataIndex) {

  var submittedBtn = $("a.btn-submitted.active");
  var submittedByFilter = true;
  if (submittedBtn.length > 0) {
    var statuses = [];
    $.each(submittedBtn, function () {
      statuses.push($(this).attr("data-value"));
    });

    var _submittedManually = aData[aData.length - 1];
    if (statuses.length == 1) {
      if (statuses[0] == 'COORDINATOR') {
        submittedByFilter = !_submittedManually;
      } else {
        submittedByFilter = _submittedManually;
      }
    }
  }

  return submittedByFilter;
}

var DateButtonsFilters = function (oSettings, aData, iDataIndex) {
  var dateBtn = $("a.btn-date.active");
  var dateFilter = true;
  if (dateBtn.length > 0) {
    var minAge = new Date() - parseInt(dateBtn.attr("data-value")) * 1000 * 60 * 60 * 24;
    var _dateColumn = aData[1];
    if (typeof $(_dateColumn).attr("data-type") == "undefined" || $(_dateColumn).attr("data-type") == "status") {
      _dateColumn = aData[0];
    }
    if (typeof _dateColumn == "string") {
      _dateColumn = $(_dateColumn).attr("data-sort-value");
    }
    dateFilter = _dateColumn * 1000 >= minAge;
  }
  return dateFilter;
}