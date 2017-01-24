// (c) Copyright 2016 Cloudera, Inc. All Rights reserved
/**
 * @module ko/components/userFeedback
 */
import componentUtils   from 'cloudera-ui/ko/components/componentUtils';
import eventTypes       from 'cloudera-ui/ko/components/eventTypes';
import modalLoader      from 'cloudera-ui/ko/components/modalLoader';
import userFeedbackForm from 'cloudera-ui/ko/components/userFeedbackForm';
import i18n             from 'cloudera-ui/utils/i18n';
import pagebus          from 'cloudera-ui/utils/pagebus';
import $                from 'jquery';
import ko               from 'knockout';
import _                from '_';

var userFeedbackTemplate = `
<div class="cui-user-feedback"><button data-bind="click: showFeedbackForm" class="btn btn-primary">Feedback</btn></div>`;

class UserFeedback {
  /**
   * @param {object} params
   * @param {string|function} [params.defaultLocation] If it is a string, then it is treated as a CSS path selector.
   * If it is a function, then it is evaluated.
   */
  constructor(params, componentInfo) {
    /**
     * @type {string} Computes the current location.
     */
    this.defaultLocation = function() {
      if (_.isString(params.defaultLocation)) {
        return $(params.defaultLocation).text();
      } else if (_.isFunction(params.defaultLocation)) {
        return params.defaultLocation();
      } else {
        return $('h1:first').text();
      }
    };
  }

  showFeedbackForm() {
    var okButtonText = i18n.t('ko.components.userFeedback.okButtonText');
    var title = i18n.t('ko.components.userFeedback.modalTitle');

    pagebus.publish(eventTypes.SHOW_COMPONENT_MODAL, {
      componentName: 'cui-user-feedback-form',
      data: {
        defaultLocation: this.defaultLocation()
      },
      modalParams: {
        cancelVisible: true,
        okButtonText: okButtonText,
        title: title,
        onOK: function() {
          this.submitFeedback();
        }
      }
    });
  }
}

var COMPONENT_NAME = 'cui-user-feedback';

componentUtils.addComponent(UserFeedback, COMPONENT_NAME, userFeedbackTemplate);

module.exports = UserFeedback;
