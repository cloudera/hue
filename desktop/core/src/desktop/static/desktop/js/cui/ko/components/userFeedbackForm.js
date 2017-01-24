// (c) Copyright 2016 Cloudera, Inc. All Rights reserved
/**
 * @module ko/components/userFeedbackForm
 */
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import eventTypes     from 'cloudera-ui/ko/components/eventTypes';
import pagebus        from 'cloudera-ui/utils/pagebus';
import $              from 'jquery';
import ko             from 'knockout';
import _              from '_';

var userFeedbackFormTemplate = `
<div class="form-horizontal cui-feedback-form">
  <div class="form-group">
    <label class="control-label col-md-2 col-sm-3 col-xs-12">Comments</label>
    <div class="col-md-8 col-sm-6 col-xs-12">
      <textarea class="form-control" placeholder="" rows="12" data-bind="attr: { maxlength: MAX_LENGTH }, textInput: feedback"></textarea>
      <span class="help-block text-right"><span data-bind="text: remaining"></span></span>
    </div>
  </div>
  <div class="control-group">
    <label class="control-label col-md-2 col-sm-3 col-xs-12">Location</label>
    <div class="col-md-8 col-sm-6 col-xs-12">
      <input class="form-control" type="text" data-bind="attr: { maxlength: MAX_LENGTH }, textInput: location"/>
    </div>
  </div>
</div>`;

class UserFeedbackForm {
  /**
   * @param {object} params
   * @param {string} params.defaultLocation The current location.
   */
  constructor(params) {
    this.feedback = ko.observable('');
    this.MAX_LENGTH = 500;

    this.location = ko.observable(params.defaultLocation);

    this.remaining = ko.pureComputed(function() {
      return this.MAX_LENGTH - this.feedback().length;
    }, this);

    this.isValid = ko.pureComputed(function() {
      return $.trim(this.location()).length > 0 &&
        $.trim(this.feedback()).length > 0;
    });
  }

  submitFeedback() {
    pagebus.publish(eventTypes.USER_FEEDBACK_FORM_SUBMIT, {
      location: this.location(),
      feedback: this.feedback()
    });
  }
}

componentUtils.addComponent(UserFeedbackForm, 'cui-user-feedback-form', userFeedbackFormTemplate);

module.exports = UserFeedbackForm;
