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
import moment from 'moment';

const DEFAULT_MARK_COUNT = 10;

export default Ember.Component.extend({

  zoom: null,
  processor: null,
  scroll: 0,

  classNames: ["em-swimlane-ruler"],

  markDef: Ember.computed("processor.timeWindow", "zoom", function () {
    var markCount = parseInt(DEFAULT_MARK_COUNT * this.get("zoom") / 100),
        timeWindow = this.get("processor.timeWindow"),
        duration = moment.duration(parseInt(timeWindow / markCount)),

        markUnit = "Milliseconds",
        markBaseValue = 0,
        markWindow = 0,
        styleWidth = 0;

    if(markBaseValue = duration.years()) {
      markUnit = "Years";
    }
    else if(markBaseValue = duration.months()) {
      markUnit = "Months";
    }
    else if(markBaseValue = duration.days()) {
      markUnit = "Days";
    }
    else if(markBaseValue = duration.hours()) {
      markUnit = "Hours";
    }
    else if(markBaseValue = duration.minutes()) {
      markUnit = "Minutes";
    }
    else if(markBaseValue = duration.seconds()) {
      markUnit = "Seconds";
    }
    else {
      markBaseValue = duration.milliseconds();
    }

    if(markBaseValue > 10) {
      markBaseValue = Math.floor(markBaseValue / 10) * 10;
    }

    markWindow = moment.duration(markBaseValue, markUnit.toLowerCase()).asMilliseconds();
    styleWidth = markWindow / timeWindow * 100;

    return {
      unit: markUnit,
      baseValue: markBaseValue,
      markWindow: markWindow,
      style: Ember.String.htmlSafe(`width: ${styleWidth}%;`),
      count: parseInt(100 / styleWidth * 1.1)
    };
  }),

  marks: Ember.computed("processor.timeWindow", "markDef", function () {
    var def = this.get("markDef"),
        markWindow = def.markWindow,
        marks = [];

    for(var i=0, count = def.count; i < count; i++) {
      marks.push({
        duration: parseInt(markWindow * i)
      });
    }

    return marks;
  })

});
