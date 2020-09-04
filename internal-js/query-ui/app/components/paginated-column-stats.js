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
export default Ember.Component.extend({
    tagName: '',
    model: null,
    itemsOnAPage: 10,
    currentPage: 1,
    totalPages: 1,

    pagedContent: Ember.computed('model', 'itemsOnAPage', function(){
        let itemsOnAPage = this.get('itemsOnAPage');
        let pagedContent = [];
        let content = this.get('model');
        let count =0;
        while(content.length) {
            count++;
            pagedContent.push( { content : content.splice(0,itemsOnAPage), pageNumber: count});
        }
        this.set('totalPages', count);
        return pagedContent;
    }),

    currentPagedContent: Ember.computed('pagedContent', 'currentPage', function(){
        let currentPagedContent = this.get('pagedContent').filter(item => item.pageNumber == this.get('currentPage'))
        return currentPagedContent.get('firstObject');
    }),

    actions: {
        fetchStats(column) {
          this.sendAction('fetchStats', column);
        },

        toggleShowStats(column){
          this.sendAction('toggleShowStats', column);
        },

        goToPage(pageNumber){
          this.set('currentPage', pageNumber);
        }
    }
});
