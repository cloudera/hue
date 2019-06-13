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

import $ from 'jquery';

$.fn.dataTableExt.afnSortData['dom-sort-value'] = function(oSettings, iColumn) {
  const aData = [];
  oSettings.oApi._fnGetTrNodes(oSettings).forEach(nRow => {
    const oElem = $('td:eq(' + iColumn + ')', nRow);
    let _val = oElem.text();
    if (typeof oElem.attr('data-sort-value') == 'undefined') {
      if (typeof oElem.find('span').attr('data-sort-value') != 'undefined') {
        _val = parseInt(oElem.find('span').attr('data-sort-value'));
      }
    } else {
      _val = parseInt(oElem.attr('data-sort-value'));
    }
    aData.push(_val);
  });

  return aData;
};
