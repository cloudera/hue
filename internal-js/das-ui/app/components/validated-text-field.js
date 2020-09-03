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

/** Example :
 * {{#validated-text-field
 * inputValue=bindedTextValue invalidClass='form-control red-border' validClass='form-control' regex="^[a-z]+$"
 * allowEmpty=false tooltip="Enter valid word" errorMessage="Please enter valid word" placeholder="Enter Word"}}
 * {{/validated-text-field}}
 */
export default Ember.Component.extend({
  classNameBindings: ['tagClassName'],
  tagClassName : false, // set it to non false value if you want a specific class to be assigned
  allowEmpty: true,
  valid: true,
  setValid: function () {
    this.set("valid", true);
    this.set("inputClass", this.get("validClass"));
    this.set("message", this.get("tooltip"));
  },
  setInvalid: function () {
    this.set("valid", false);
    this.set("inputClass", this.get("invalidClass"));
    this.set("message", this.get("errorMessage"));
  },
  onChangeInputValue: function () {
    var regStr = this.get("regex");
    var regExp = new RegExp(regStr, "g");
    if (this.get("inputValue")) {
      var arr = this.get("inputValue").match(regExp);
      if (arr != null && arr.length === 1) {
        this.setValid();
      }
      else {
        this.setInvalid();
      }
    } else {
      if (this.get("allowEmpty")) {
        this.setValid();
      } else {
        this.setInvalid();
      }
    }
  }.observes("inputValue").on('init')
});
