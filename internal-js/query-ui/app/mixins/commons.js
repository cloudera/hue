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
export default Ember.Mixin.create({
    closeAutocompleteSuggestion: function() {
        Ember.$(".CodeMirror-hints").remove();
    },
    setActiveTabAsCompose: function() {
        setTimeout(()=>{
            this.removePreviousActiveSelection('queries');
             Ember.$(".left-pane").find(".menu-queries").addClass("active");
        }, 10);
    },
    setActiveTabAsQueries: function() {
        setTimeout(()=>{
            this.removePreviousActiveSelection('hive-queries');
            Ember.$(".left-pane").find(".menu-hive-queries").addClass("active");
        }, 10);
    },
    setActiveTab: function(routeName) {
        try {
          setTimeout(()=>{
            this.removePreviousActiveSelection(routeName);
            Ember.$(".left-pane").find(`.menu-${routeName}`).addClass("active");
          }, 1000);
        } catch(e){}
    },
    removePreviousActiveSelection(route){
        this.closeTooltip();
        Ember.$(".left-pane").find(".menu, .submenu, .list-group-item").removeClass("active");
        Ember.$(".left-green-arrow").addClass("hide");
        Ember.$(".menu-"+route).find(".left-green-arrow").first().removeClass("hide");
    },
    closeTooltip() {
        Ember.$(".ui-tooltip-content").parents('div').remove();
    },
    getQueryDetailsPage(queryId) {
        return "<a class='query-details-breadcrumbs' href='#/'>Queries </a>/ "+queryId;
    },
    setErrorPageONCompose: function(){
        Ember.run.later(function () {
            let container = Ember.$(".worksheet-container");
            if(container) {
                container.addClass('hide');
            }
        }, 1000);
    },
    setUserLevelProperty: function(model) {
        ga('set', 'dimension1', model.info.clusterId);
        ga('send', 'hivestudio');
    }
});
