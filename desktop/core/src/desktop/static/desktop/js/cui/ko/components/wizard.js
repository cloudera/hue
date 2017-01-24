// Copyright (c) 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/wizard
 * @description Defines cui-wizard which can have steps passed in like so:
 * Example: <cui-wizard>
 *           <step1></step1>
 *           <step2></step2>
 *          </cui-wizard>
 */

var componentUtils = require('cloudera-ui/ko/components/componentUtils');
var i18n = require('cloudera-ui/utils/i18n');
var ko = require('knockout');
var $ = require('jquery');
var WizardStep = require('./wizardStep');

class Wizard {
  /**
   * @constructor
   * @alias module:ko/components/wizard
   * @param {string} [params.cancelPage] A url to back to when the wizard is exited via cancel. Defaults to document.referrer.
   * @param {string} [params.cancelLabel] Optional label text for cancel. Defaults to 'Cancel'
   * @param {string} [params.exitPage] A url to back to when the wizard is exited via finish. Defaults to document.referrer.
   * @param {string} [params.onCancel] Callback for when user clicks Cancel. Defaults to _.noop.
   * @param {string} [params.onFinish] Callback for when user clicks Finish. Defaults to _.noop.
   * @param {string} [params.finishLabel] Optional label text for finish. Defaults to 'Finish'
   * @param {ko.observable} [params.showSidebar] Controls whether we display the sidebar. Defaults to true.
   * @param {object} componentInfo Extra knockout component info.
   * @param {Node[]} componentInfo.templateNodes The inner nodes passed into this component.
   */
  constructor(params, componentInfo) {
    this.element = componentInfo.element;

    /**
      * Keeps track of the index of the current step that is shown.
      */
    this.index = ko.observable(0);

    /**
     * Read-write observable array
     * A list of wizard steps.
     * @type {WizardStep[]}
     */
    this.steps = ko.observableArray();

    /**
      * Returns knockout component child instance.
      * @return {component}
      */
    this.currentStep = ko.pureComputed(function() {
      return this.steps()[this.index()];
    }, this);

    /**
      * Enables the "Previous" button based on the current step.
      * @type {boolean}
      */
    this.enablePrev = ko.pureComputed(function() {
      if (this.index() === 0) {
        return false;
      }

      var step = this.currentStep();
      if (step) {
        return step.enablePrev();
      } else {
        return false;
      }
    }, this);

    /**
      * Enables the "Next" / "Finish" button based on the current step.
      * @type {boolean}
      */
    this.enableNext = ko.pureComputed(function() {
      var step = this.currentStep();
      if (step) {
        return step.enableNext();
      } else {
        return false;
      }
    }, this);

    // Please leave this i18n var as is so the i18n compiler will work properly
    var defaultFinish = i18n.t('ko.components.wizard.finish');
    this.finishLabel = params.finishLabel || defaultFinish;

    // Please leave this i18n var as is so the i18n compiler will work properly
    var nextLabel = i18n.t('ko.components.wizard.next');

    /**
      * Returns label for the "Next" or "Finish" button label.
      * @type {string}
      */
    this.nextBtnLabel = ko.pureComputed(function() {
      return this.index() === (this.steps().length - 1) ? this.finishLabel : nextLabel;
    }, this);

    var cancel = i18n.t('ko.components.wizard.cancel');
    this.cancelBtnLabel = params.cancelLabel || cancel;

    /**
      * Used for the "Cancel" link.  If a referrer param is passed in, use that, otherwise use document.referrer.
      */
    this.cancelPage = params.cancelPage || document.referrer;

    /**
      * Used for the "Finish" button.  If a referrer param is passed in, use that, otherwise use document.referrer.
      */
    this.exitPage = params.exitPage || document.referrer;

    this.index.subscribe(function() {
      this._scrollToTopOfStep();
    }, this);

    this.onCancel = _.isFunction(params.onCancel) ? params.onCancel : _.noop;
    this.onFinish = _.isFunction(params.onFinish) ? params.onFinish : _.noop;

    this.showSidebar = ko.pureComputed(function() {
      return ko.unwrap(params.showSidebar) !== false;
    });
  }

  /**
    * Set window.location.href to this.cancelPage.
    */
  cancel() {
    var result = this.onCancel();
    if (result === undefined || result) {
      window.location.href = this.cancelPage;
    }
  }

  /**
    * Set window.location.href to this.exitPage.
    */
  finish() {
    var result = this.onFinish();
    if (result === undefined || result) {
      window.location.href = this.exitPage;
    }
  }

  /**
    * Call onLeave of the current step, when going to the next step.
    */
  nextStep() {
    var step = this.currentStep();
    var callback = this.onLeaveNext.bind(this);
    var isForward = true;
    step.onLeave(callback, isForward);
  }

  /**
    * Increments the step index by 1 and calls finish() if it's the last step, or calls onEnter for the next step.
    */
  onLeaveNext() {
    var next = this.index() + 1;
    if (next > this.steps().length - 1) {
      this.finish();
    } else {
      var callback = this.stepWasEntered.bind(this);
      this.index(next);
      this.currentStep().onEnter(callback, true);
    }
  }

  /**
    * Decrements the step index by 1 and calls onEnter for the previous step.
    */
  onLeavePrev() {
    var prev = this.index() - 1;
    if (prev >= 0) {
      var callback = this.stepWasEntered.bind(this);
      this.index(prev);
      this.currentStep().onEnter(callback);
    }
  }

  /**
    * Call onLeave of the current step, when going to the previous step.
    */
  prevStep() {
    var step = this.currentStep();
    var callback = this.onLeavePrev.bind(this);
    var isForward = false;
    step.onLeave(callback, isForward);
  }

  /**
   * If you are scrolled to the bottom of a step, the wizard container scrolltop needs to be reset.
   * This function should be called whenever the index changes.
   */
  _scrollToTopOfStep() {
    $(this.element).find('.cui-wizard-container').scrollTop(0);
  }

  /**
    * Callback for onEnter to fire off calls for analytics or anything else after a step is entered
    */
  stepWasEntered() {
    // TODO: Implement
  }

  /**
   * Finds the WizardStep elements that were rendered with the knockout template binding handler.
   * @param {Node} element The node that applied the template binding handler.
   */
  afterStepsRendered(element) {
    var steps = [];
    var wizard = this;

    $(element).children().each(function(index, node) {
      var component = componentUtils.componentFor(node);

      if (component && component instanceof WizardStep) {
        steps.push(component);

        // decorate a step based on wizard.index observable
        component.stepIndex = index;

        /**
         * Read-only computed
         * Returns the current state of a step: visited, current, unvisited.
         * Used for css styling.
         * @type {string}
         */
        component.stepState = ko.pureComputed(function() {
          var currentIndex = wizard.index();
          var stepIndex = this.stepIndex;

          return {
            unvisited: (stepIndex > currentIndex),
            visited: (stepIndex < currentIndex),
            current: (stepIndex === currentIndex)
          };
        }, component);
      }
    });

    this.steps(steps);

    // select the first step.
    var callback = this.stepWasEntered.bind(this);
    this.currentStep().onEnter(callback, true);
  }

}

var template = `
<div class="cui-wizard">
  <div class="cui-wizard-container">
    <!-- ko if: showSidebar -->
    <div class="cui-wizard-sidebar" data-bind="foreach: steps">
      <div class="cui-wizard-sidebar-item" data-bind="css: stepState">
        <span class="cui-wizard-sidebar-icon"></span>
        <span class="cui-wizard-sidebar-title" data-bind="text: title, attr: { title: title }"></span>
        <div class="cui-wizard-sidebar-connection"></div>
      </div>
    </div>
    <!-- /ko -->
    <div class="cui-wizard-content">
      <div data-bind="template: {
                       nodes: $componentTemplateNodes,
                       afterRender: function() { $component.afterStepsRendered($element); }
                      }">
      </div>
    </div>
  </div>
</div>
<div class="cui-wizard-footer">
  <div class="cui-wizard-footer-button-container">
    <a class="btn btn-link btn-lg cancel" data-bind="click: $component.cancel, text: cancelBtnLabel"></a>
    <div class="pull-right">
      <button class="btn btn-default btn-lg prev" data-bind="click: $component.prevStep, enable: enablePrev">${i18n.t('ko.components.wizard.previous')}</button>
      <button class="btn btn-primary btn-lg next" data-bind="click: $component.nextStep, enable: enableNext, text: nextBtnLabel"></button>
    </div>
  </div>
</div>
`;

componentUtils.addComponent(Wizard, 'cui-wizard', template);

module.exports = Wizard;
