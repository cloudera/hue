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
import commons from '../mixins/commons';

export default Ember.Route.extend(commons, {
  title: "Application",
  info: Ember.inject.service(),
  ldapAuth: Ember.inject.service(),
  highlightedTab: {},
  pageReset: function () {
    this.send("resetTooltip");
  },
  setupController : function(controller, model) {
    this._super(controller, model);
    this.appendGA(model);
    controller.set('theRoute', this);
    this.setProductInfoInController(controller);
    this.setContextInController(controller);
    controller.set('rootURL', ENV.rootURL);
    controller.set('passwordRequired', false);

    controller.set('showSearchQuerySettings', false);
    controller.set('searchQuerySettings', {});
  },
  appendGA(model) {
    this.initiateGA(model);
  },
  setProductInfoInController(controller) {
    this.get('info').getProductInfo().then(data => {
        controller.set('aboutInfo',data);
    }, error => {
        controller.set('aboutInfo', { apiAccessError:true });
    });
  },
  setContextInController(controller) {
    return this.get('info').getContext().then(data => {
        controller.set('contextInfo',{ "username": data.username, "jdbcConnection": data.connectionUrl, "canUpdateJdbcConnection": data.canUpdateJdbcConnection});
        controller.set('isAdminUser', data.isAdminUser);
        return { "username": data.username, "jdbcConnection": data.connectionUrl}
    }, error => {
        controller.set('contextInfo', { apiAccessError:true });
        return {};
    });
  },
  actions: {
    didTransition: function(/* transition */) {
      this.pageReset();
    },
    bubbleBreadcrumbs: function (breadcrumbs) {
      this.set("controller.breadcrumbs", breadcrumbs);
    },
    setHighlightedTab(){
     this.set("highlightedTab", highlightedTab);
    },
    resetTooltip: function () {
      Ember.$(document).tooltip("destroy");
      Ember.$(document).tooltip({
        show: {
          delay: 500
        },
        open: function (event, ui) {
          setTimeout(function () {
            Ember.$(ui.tooltip).hide("fade");
          }, 5000);
        },
        track: true,
        tooltipClass: 'generic-tooltip'
      });
    },

    logout: function() {
      this.store.adapterFor('auth').logout()
      .catch((e) => {
          this.set('controller.logoutError', "Failed to logout");
      });
    },

    // Modal window actions
    openModal: function (componentName, options) {
      options = options || {};

      if(typeof componentName === "object") {
        options = componentName;
        componentName = null;
      }

      /*
      this.render(options.modalName || "simple-modal", {
        into: 'application',
        outlet: 'modal',
        model: {
          title: options.title,
          componentName: componentName,
          content: options.content,
          parentController: options.parentController
        }
      });
      */

      this.set('controller.searchQuerySettings.title', options.title);
      this.set('controller.searchQuerySettings.content', options.content);
      this.set('controller.searchQuerySettings.componentName', componentName);
      this.set('controller.searchQuerySettings.parentController', options.parentController);

      this.set('controller.showSearchQuerySettings', true);

      /*
      Ember.run.later(function () {
        Ember.$(".simple-modal").modal();
      });
      */


    },
    closeModal: function () {
      Ember.$(".simple-modal").modal("hide");
    },
    destroyModal: function () {
      Ember.run.later(this, function () {
        this.disconnectOutlet({
          outlet: 'modal',
          parentView: 'application'
        });
      });
    },

    setLoadTime: function (time) {
      this.set("controller.loadTime", time);
    },

    setSliderWidth(classLeftMenu, classRightMenu){
      this.get('controller').setProperties({classRightMenu:classRightMenu, classLeftMenu:classLeftMenu});
      this.setProperties({classRightMenu:classRightMenu, classLeftMenu:classLeftMenu});
    },

    setHeaderTitles(header){
      this.set('controller.header', header.header);
      this.set('controller.subHeader', header.subHeader)
    },
    resetConnection: function(){
      var _this = this;
      return this.get('info').resetJdbcConnection().then(function(data){
        return _this.setContextInController(_this.controller);
      });
    },
    saveConnection: function(newConnectionUrl){
      var _this = this;
      return this.get('info').setJdbcConnection(newConnectionUrl).then(function(data){
        return _this.setContextInController(_this.controller);
      });
    }
  },

  serviceCheck: Ember.inject.service(),
  ldapAuth: Ember.inject.service(),

  init() {
    this.get('ldapAuth').on('ask-password', this.askPassword.bind(this));
    this.get('ldapAuth').on('password-provided', this.passwordProvided.bind(this));
    return this._super(...arguments);
  },

  beforeModel() {
    if (ENV.APP.SHOULD_PERFORM_SERVICE_CHECK && !this.get('serviceCheck.checkCompleted')) {
      this.transitionTo('service-check');
    }
  },
  model() {
    return this.get('info').getContext().then(data => {
                return data.smartsense_id;
            }, error => {
                return "";
            });
  },
  askPassword() {
    this.set('ldapAuth.passwordRequired', true);
    this.set('controller.passwordRequired', true);
    this.transitionTo('password');
  },

  passwordProvided() {
    this.set('ldapAuth.passwordRequired', false);
    this.set('controller.passwordRequired', false);
    this.setProductInfoInController(this.get('controller'));
    this.setContextInController(this.get('controller'));
    this.transitionTo("hive-queries");
  }
});
