// Copyright (c) 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/wizardStep
 * @description Defines the interface for the steps inside a wizard component.
 */

var ko = require('knockout');

class WizardStep {
  constructor() {
    /**
      * Enables the "Next" / "Finish" button based on the result of this.enableNextComputed.
      * @type {boolean}
      */
    this.enableNext = ko.pureComputed(this.enableNextComputed, this);

    /**
      * Enables the "Previous" button based on the result of this.enablePrevComputed.
      * @type {boolean}
      */
    this.enablePrev = ko.pureComputed(this.enablePrevComputed, this);

    /**
      * Tracks if step is selected or not.
      * @type {boolean}
      */
    this.isStepSelected = ko.observable(false);

    /**
     * Title for the step.  Each step should override this.
     * @type {string}
     */
    this.title = '';
  }

  /**
    * Before enter of a step, make API requests or whatever is needed to set up the step, then call callback.
    * This should be overriden, this is a public function.
    * @param {function} callback A callback to call to when the wizard is entered.
    */
  beforeEnter(callback) {
    callback();
  }

  /**
    * Before leave of a step, validate user input or whatever is needed, then call callback.
    * This should be overriden, this is a public function.
    * @param {function} callback A callback to call to when the wizard is exited.
    */
  beforeLeave(callback) {
    callback();
  }

  /**
    * Return true or false depending if Next should be enabled.
    * This should be overriden, this is a public function.
    * @return {boolean}
    */
  enableNextComputed() {
    return true;
  }

  /**
    * Return true or false depending if Previous should be enabled.
    * This should be overriden, this is a public function.
    * @return {boolean}
    */
  enablePrevComputed() {
    return true;
  }

  /**
    * On enter of a step, handle the direction, and then call callback when direction is valid.
    * @param {function} callback A callback to call to when the wizard is entered.
    * @param {boolean} [isForward] Direction of the event.
    */
  onEnter(callback, isForward) {
    if (!this.isStepSelected()) {
      if (isForward) {
        this.beforeEnter(_.bind(function() {
          // Need to call this.isStepSelected() again, because
          // beforeEnter may call this function
          // asynchronously.
          if (!this.isStepSelected()) {
            this.isStepSelected(true);
          }
        }, this), isForward);
      } else {
        this.isStepSelected(true);
      }
    }
  }

  /**
    * On leave of a step, handle the direction, and then call callback when direction is valid.
    * @param {function} callback A callback to call to when the wizard is exited.
    * @param {boolean} [isForward] Direction of the event.
    */
  onLeave(callback, isForward) {
    if (isForward) {
      this.beforeLeave(_.bind(function() {
        // when leaving, hide the step and proceed.
        // Need to call this.isStepSelected() again, because
        // beforeLeave may call this function afterwards.
        if (this.isStepSelected()) {
          this.isStepSelected(false);
          callback();
        }
      }, this), isForward);
    } else {
      this.isStepSelected(false);
      callback();
    }
  }

  /**
   * Wraps all child classes with an "if" binding handler
   * This makes it so a template only renderes when you are selected.
   * @param {string} template The child class template.
   * @return {string}
   */
  decorateTemplate(template) {
    return '<!-- ko if: isStepSelected -->' + template + '<!-- /ko -->';
  }

}

module.exports = WizardStep;
