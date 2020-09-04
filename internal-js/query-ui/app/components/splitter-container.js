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
import SC from 'ember-cli-splitter/components/splitter-container';
import commons from '../mixins/commons';

const {
  $,
  Component,
  computed,
  isNone,
  get,
  getProperties,
  set,
  setProperties
} = Ember;

export default SC.extend(commons, {

  init() {
    this._super(...arguments);
    $(window).on('resize', this.handleResize.bind(this));
  },

  willDestroyElement () {
    this._super(...arguments);
    $(window).off("resize");
  },

  handleResize (e) {
    this.sendAction('handleSplitterDrag');
  },

  actions: {
    someFunc(){
      this.sendAction('someFunc');
    }
  },

  mouseUp() {
    set(this, 'isDragging', false);
    this._removeGlobalListeners();
    console.log('Drop event ends here.');

    Ember.$('.domain-range').css('margin-left',  ($($('.splitter-pane')[1]).width() -500)/2 + 'px');
    let rangeCountContainer = Ember.$('.domain-range').width();
    let splitterPaneRightWidth = Ember.$('.splitter-pane').last().width();
    
    if(splitterPaneRightWidth < rangeCountContainer){
       Ember.$('.domain-range').css('visibility', 'hidden');
    } else{
       Ember.$('.domain-range').css('visibility', 'visible');
    }
    this.closeTooltip();

    this.sendAction('handleSplitterDrag');
  },

  mouseMove({ pageX }) {

    // Ignore unless dragging is enabled
    if (!get(this, 'isDragging')) {
      return;
    } else{
      Ember.$('.em-table-footer-component').css('visibility', 'hidden');
    }

    let {
      firstPane,
      lastPane,
      barPosition
    } = getProperties(this, 'firstPane', 'lastPane', 'barPosition');

    // Calculate the percentage of the firstPane
    let percent = (pageX - firstPane.$().offset().left) / this.$().width() * 100;

    if (pageX < barPosition) {
      // Moving left, decrease size of firstPane
      set(firstPane, 'width', percent);
      // Account for minWidths
      set(lastPane, 'width', 99 - firstPane.get('width'));
    } else {
      // Moving right, decrease size of lastPane
      set(lastPane, 'width', 99 - percent);
      // Account for minWidths
      set(firstPane, 'width', 99 - lastPane.get('width'));
    }
  }

});
