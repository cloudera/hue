// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/modal
 * @description Wrap a template with a modal.
 * Example:
 *  <cui-modal params="">
 *    Your Content
 *  </cui-modal>
 *
 *  Params:
 *   title: a string
 *   showDialog: a boolean
 *   closeVisible: default false
 *   cancelVisible: default false
 *   okVisible: default true
 *   okButtonText: default Ok
 *   onOK: click function
 *   isSaving: default false
 * cui-modal is basically a wrapper for the bootstrap modal module, but provides basic html template.
 * Any inner nodes will be wrapped with a knockout modal template.
 * The inner nodes' context will be the outer context of cui-modal.
 * We do not pollute the inner nodes with the component context.
 * If the component context is needed, you can access $component.
 *
 * @see node_modules/bootstrap/js/modal.js
 */
var modal = require('bootstrap/modal');
var componentUtils = require('cloudera-ui/ko/components/componentUtils');
var i18n = require('cloudera-ui/utils/i18n');
var $ = require('jquery');
var ko = require('knockout');
var _ = require('_');

var modalTemplate = `
<div class="modal fade" tabindex="-1" role="dialog" aria-hidden="true" data-bind="attr: attr">
  <div class="modal-dialog">
    <div class="modal-content">
      <form data-bind="submit: onOK">
        <div class="modal-header" data-bind="attr: {id: _headerId}">
          <button type="button" class="close" data-bind="visible: !disableDismiss, click: _.bind(_onClose, $component)" >
            <span aria-hidden="true">&times;</span>
            <span class="sr-only" data-bind="text: closeButtonText"></span>
          </button>
          <h2 class="modal-title" data-bind="text: title"></h2>
        </div>
        <!-- ko componentContextEscaper -->
        <div class="modal-body" data-bind="template: { nodes: $component.content }"></div>
        <!-- /ko -->
        <div class="modal-footer">
          <!-- ko if: _.isEmpty($component.childNodeTemplates['cui-modal-footer']) -->
            <button name="close" type="button" class="btn btn-primary" data-bind="visible: closeVisible, click: _.bind(_onClose, $component), text: closeButtonText"></button>
            <button name="cancel" type="button" class="btn btn-link" data-bind="visible: cancelVisible, click: _.bind(_onCancel, $component), text: cancelButtonText"></button>
            <button name="reset" type="reset" class="btn btn-link" data-bind="visible: resetVisible, click: _.bind(_onReset, $component), text: resetButtonText"></button>
            <button name="ok" type="submit" data-bind="visible: okVisible, enable: okEnabled, click: _.bind(_onOK, $component), attr: { class : okButtonClass }">
              <span data-bind="text: okButtonText"></span>
              <span data-bind="visible: isSaving">...</span>
            </button>
          <!-- /ko -->
          <!-- ko injectChildTemplate: 'cui-modal-footer' -->
          <!-- /ko -->
        </div>
      </form>
    </div>
  </div>
</div>`;

var count = 0;

/**
 * @constructor
 * @alias module:ko/components/modal
 * @param {object} params cui-modal params.
 * @param {boolean} [params.okVisible] optional boolean/observable to show the ok button.
 *  Default true.
 * @param {boolean} [params.cancelVisible] optional boolean or boolean observable to show the cancel button.
 *  Default false.
 * @param {boolean} [params.resetVisible] optional boolean or boolean observable to show the reset button.
 *  Default false.
 * @param {boolean} [params.closeVisible] optional boolean or boolean observable to show the close button.
 *  Default false.
 * @param {boolean} [params.disableDismiss] optional boolean to disable dismissing the dialog. Defaults to false.
 *  When true, we remove the 'x' close button. Clicking cannot dismiss the modal.  You have to click ok or cancel to dismiss.
 * @param {boolean} [params.showDialog] optional boolean observable to show/hide the modal.
 * @param {function} [params.onOK] optional callback when ok button is clicked. Bound to $parent.
 * @param {function} [params.onReset] optional callback when reset button is clicked. Bound to $parent.
 * @param {function} [params.onClose] optional callback when close button is clicked. Bound to $parent.
 * @param {function} [params.onCancel optional callback when cancel button is clicked. Bound to $parent.
 * @param {string} [params.title] Modal title.
 * @param {string} [params.modalClass] Special class to customize the modal-dialog (defaults to modal-lg).
 * @param {string} [params.okButtonClass] Css class to add to the ok button.
 * @param {boolean} [params.okEnabled] optionally disable/enable the ok button with an observable boolean.
 * @param {boolean} [params.isSaving] optionally trigger saving ellipsis '...' with an observable boolean.
 * @param {object} [params.attr] optionally add attributes to the toplevel div.
 *  Defaults to add aria-labeledby attribute to div.modal.
 * @param {object} [params.destroyOnClose] optional Default false.
 * @param {object} [params.modalOptions] Options for the bootstrap modal (show, keyboard, backdrop).
 * @param {object} componentInfo knockout node data for inner templates.
 */
var ModalComponent = function(params, componentInfo) {
  this.element = componentInfo.element;

  this.$modal = $(this.element).find('.modal');

  this.show = ko.isObservable(params.showDialog) ?
    params.showDialog :
    ko.observable(params.showDialog);

  componentUtils.captureChildTemplate(this, componentInfo.templateNodes, 'cui-modal-footer');

  this.show.subscribe(function(showValue) {
    var modalOption = showValue ? 'show' : 'hide';
    this.$modal.modal(modalOption);
  }, this);

  /**
   * Any option that can go into bootstrap $.modal:
   * Supported options:
   *  - show {boolean} if we want to initially show the modal, can be observable.
   *  - keyboard {boolean} if we allow keyboard dismiss with ESC default true.
   *  - backdrop {boolean|string} defaults to true, can also be 'static', which makes it so mouse click doesn't dismiss.
   * @see http://getbootstrap.com/javascript/#modals-options
   * @type {object}
   */
  var defaultModalOptions = {
    show: !!this.show(),
    keyboard: true,
    backdrop: true
  };

  this.modalOptions = _.extend(defaultModalOptions, params.modalOptions);

  var okButtonText = i18n.t('ko.components.modal.ok');
  var cancelButtonText = i18n.t('ko.components.modal.cancel');
  var resetButtonText = i18n.t('ko.components.modal.reset');
  var closeButtonText = i18n.t('ko.components.modal.close');

  _.defaults(this, params, {
    // button texts customization
    okButtonText: okButtonText,
    cancelButtonText: cancelButtonText,
    resetButtonText: resetButtonText,
    closeButtonText: closeButtonText,

    // visibility customization
    closeVisible: false,
    cancelVisible: false,
    resetVisible: false,
    okVisible: true,
    disableDismiss: false,

    isSaving: false,
    okEnabled: true,

    destroyOnClose: false
  });

  /**
   * ! this makes it so clicking outside the modal does not dismiss it
   * If no close/ok/cancel buttons are present,
   *  Game Over: you will not be able to dismiss the modal.
   */
  if (this.disableDismiss) {
    this.modalOptions.backdrop = 'static';
    this.modalOptions.keyboard = false;
  }

  // callback customizations
  /**
   * @param {ModalComponent} modal The current modal.
   * @param {Event} event A jquery/bootstrap dismiss event.
   */
  var hideCallback = _.bind(function(modal, event) {
    this.dismiss();
  }, this);
  this.onOK = params.onOK || _.noop;
  this.onReset = params.onReset || _.noop;
  this.onClose = params.onClose || _.noop;
  this.onCancel = params.onCancel || _.noop;

  this.title = params.title;
  this.modalClass = params.modalClass || 'modal-lg';
  this.okButtonClass = params.okButtonClass || 'btn btn-primary';

  // If we are saving, disable any ok button.
  this._okEnabled = this.okEnabled;
  this.okEnabled = ko.pureComputed(function() {
    return ko.unwrap(this._okEnabled) && !ko.unwrap(this.isSaving);
  }, this);

  this._headerId = 'modal-header-' + count++;
  this.attr = _.defaults({}, params.attr, {
    'aria-labelledby': this._headerId,
    class: 'modal fade ' + this.modalClass
  });

  // inner template nodes
  this.content = componentInfo.templateNodes;

  this.$modal.on('show.bs.modal', _.bind(function(event) {
    this._lastActiveElement = document.activeElement;
  }, this))
    .on('hide.bs.modal', _.bind(function(event) {
      this.dismiss();
    }, this))
    .on('hidden.bs.modal', _.bind(function(event) {
      if (this.destroyOnClose) {
        // We cannot remove the dialog immediately because
        // sometimes, we want to submit the form on the popup
        // itself, but that gets called after this function is
        // executed. So we have to delay the remove.
        setTimeout(function() {
          $(componentInfo.element).remove();
        }, 50);
      }

      if (this._lastActiveElement) {
        this._lastActiveElement.focus();
        this._lastActiveElement = undefined;
      }

      /**
       * If we still have modals open, make sure modal-open css class still is on document body.
       * This keeps the scrolling behavior correct.
       */
      if ($('.modal.in').length) {
        $(document.body).addClass('modal-open');
      }
    }, this))
    .on('shown.bs.modal', _.bind(function() {
      // $firstInput is not the close button.
      var $firstInput = this.$modal.find(':input:not(.close):visible:enabled:first');
      if ($firstInput.length === 0) {
        // modals with no inputs (like alerts) should select the primary button.
        var $button = this.$modal.find('.btn-primary:visible:enabled');
        if ($button.length === 0) {
          // no primary button? select *any* button you can find
          $button = this.$modal.find('.btn,button:visible:enabled:first');
        }

        $button.focus();
      } else {
        $firstInput.focus();
      }
    }, this))
    .modal(this.modalOptions);

  /**
   * This method attempts to do the same thing that bootstrap-select does with dropupAuto, but within a Modal.
   * Basically when the user clicks the dropdown-toggle we look at the modal <fieldset> (if any).
   * The <fieldset> is the element that adds the overflow-y: scroll;
   * Using the height of the fieldset, we construct a border where, if we cross the border,
   *  we try to add the dropup class to the nearest btn-group or input-group-btn (for OPEN_LIST widgets)
   * We add one other restriction that says don't bother adding dropup if the top of the dropdown - the menu height
   * is negative.  This means that the menu would draw outside the top of the window.
   */
  this.$modal.on('click', '.dropdown-toggle', function adjustModalDropup(event) {
    var $fieldset = $(event.target).closest('fieldset');
    if ($fieldset.length > 0) {
      var $dropdown = $(event.target),
          $menu = $dropdown.next('.dropdown-menu'),
          fieldsetBorder = $fieldset.offset().top + $fieldset.height(),
          maxAllowableVisibleMenu = $dropdown.offset().top + ($dropdown.height() * 3),
          outsideFieldset = maxAllowableVisibleMenu > fieldsetBorder,
          outsideWindowBottom = maxAllowableVisibleMenu > $(window).height(),
          outsideWindowTop = ($dropdown.offset().top - $menu.height()) > 0,
          shouldAddDropup = (outsideFieldset || outsideWindowBottom) && outsideWindowTop;

      $dropdown.closest('.btn-group,.input-group-btn')
        .toggleClass('dropup', shouldAddDropup);
    }

  });
};

/**
 * Returns an object that will be applied to onOK, onClose, etc.
 * Generally, we return the outer context.$data.
 * If the outer context data has a function, modalComponent,
 *  we try to ask the outerdata to elaborate and give us a more suitable object to use.
 * @private
 * @return {object}
 */
ModalComponent.prototype._boundData = function() {
  var context = ko.contextFor(this.element);
  var data = context.$data;
  if (data.modalComponent) {
    data = data.modalComponent() || data;
  }

  return data;
};

function wrapDismiss(context, fn, modal) {
  return function() {
    var result = fn.apply(context, arguments);
    if (result === undefined || result) {
      modal.dismiss();
    }
  };
}

/**
 * Calls any onOK function, then dismisses unless the onOK function returns false.
 * @private
 */
ModalComponent.prototype._onOK = function() {
  wrapDismiss(this._boundData(), this.onOK, this)();
};

/**
 * Calls any onDismiss function, then dismisses unless the onClose function returns false.
 * @private
 */
ModalComponent.prototype._onClose = function() {
  wrapDismiss(this._boundData(), this.onClose, this)();
};

/**
 * Calls any onDismiss function, then dismisses unless the onCancel function returns false.
 * @private
 */
ModalComponent.prototype._onCancel = function() {
  wrapDismiss(this._boundData(), this.onCancel, this)();
};

/**
 * Calls any onDismiss function, then dismisses unless the onReset function returns false.
 * @private
 */
ModalComponent.prototype._onReset = function() {
  wrapDismiss(this.onReset, this._boundData(), this)();
};

/**
 * Invoked on component disposal.
 */
ModalComponent.prototype.dispose = function() {
  this.$modal.data('bs.modal', null);
};

/**
 * Dismiss the cui-modal.
 */
ModalComponent.prototype.dismiss = function() {
  this.show(false);
};

ko.bindingHandlers.modalDismiss = {
  init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    var $modal = bindingContext.$component;
    var callback = wrapDismiss(bindingContext.$data, valueAccessor(), $modal);
    ko.bindingHandlers.click.init(element, function() {
      return callback;
    }, allBindingsAccessor, viewModel, bindingContext);
  }
};

componentUtils.addComponent(ModalComponent, 'cui-modal', modalTemplate);

module.exports = ModalComponent;
