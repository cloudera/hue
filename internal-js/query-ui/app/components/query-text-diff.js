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

// Must be convert into an ember addon

import Ember from 'ember';

export default Ember.Component.extend({

  type: null,
  info: null,

  title: null,

  codeMirror: null,

  classNames: ['caller-info'],

  mode: Ember.computed("type", function () {
    switch(this.get("type")) {
      case 'Hive':
        return 'text/x-hive';
      case 'Pig':
        return 'text/x-pig';
      default:
        return 'text/x-sql';
    }
  }),

  _init:  Ember.on('didInsertElement', function() {
    Ember.run.scheduleOnce('afterRender', this, function() {
    	let value, orig1, orig2, dv, panes = 2, highlight = true, connect = "align", collapse = false;
		let target = document.getElementById("view");
		target.innerHTML = "";
		value = sqlFormatter.format(this.get('query1')), orig1 = sqlFormatter.format(this.get('query1')), orig2 = sqlFormatter.format(this.get('query2'));
		let codeMirror = CodeMirror.MergeView(target, {
			value: value,
			origLeft: panes == 3 ? orig1 : null,
			orig: orig2,
			lineNumbers: true,
			mode: "text/x-sql",
			highlightDifferences: highlight,
			connect: connect,
            indentUnit: 2,
            smartIndent: true,
            tabSize: 4,
            electricChars: true,
            lineWrapping: true,
            lineNumbers: true,
            readOnly: true,
			      collapseIdentical: collapse
		  });
      this.set('codeMirror', codeMirror);
    });
  })
});
