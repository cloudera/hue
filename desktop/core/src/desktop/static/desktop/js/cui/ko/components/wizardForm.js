// Copyright (c) 2017 Cloudera, Inc. All rights reserved.

import Wizard from 'cloudera-ui/ko/components/wizard';
import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import i18n from 'cloudera-ui/utils/i18n';
import ko from 'knockout';
import _ from 'lodash';

/**
 * @module cloudera-ui/ko/components/wizardForm
 * @description WizardForm is basically a one-step wizard.
 * Because of this, the footer buttons are arranged slightly differently.
 * Most of the same params passed into Wizard work for WizardForm.
 * @example
 * <cui-wizard-form params="onFinish: function() { console.log('finished'); }, finishLabel: 'Submit', enableFinish: myFormIsValid">
 *  <h1>My form</h1>
 * </cui-wizard-form
 */
class WizardForm extends Wizard {
  /**
   * @param {object} params Most of the params for cui-wizard work here. Supported params: cancelPage, cancelLabel, finishLabel, exitPage, onCancel, onFinish.
   * @param {observable:boolean} [params.enableFinish] Read only observable that allows the form to be submitted.
   */
  constructor(params, componentInfo) {
    super(params, componentInfo);
    this.enableFinish = ko.pureComputed(function() {
      var enable = ko.unwrap(params.enableFinish);
      if (_.isUndefined(enable)) {
        return true;
      }

      return enable;
    });
    this.content = componentInfo.templateNodes;
  }
}

var template = `
<div class="cui-wizard">
  <div class="cui-wizard-container">
    <div class="cui-wizard-content">
        <!-- ko componentContextEscaper -->
        <div data-bind="template: { nodes: $component.content }"></div>
        <!-- /ko -->
      </div>
    </div>
  </div>
</div>
<div class="cui-wizard-footer">
  <div class="cui-wizard-footer-button-container">
      <div class="pull-right">
        <a class="btn btn-link btn-lg" data-bind="click: cancel, text: cancelBtnLabel"></a>
        <button class="btn btn-primary btn-lg" data-bind="click: finish, enable: enableFinish, text: finishLabel"></button>
      </div>
  </div>
</div>
`;

componentUtils.addComponent(WizardForm, 'cui-wizard-form', template);

export default WizardForm;
