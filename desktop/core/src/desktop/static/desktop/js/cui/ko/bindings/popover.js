// Copyright (c) 2016 Cloudera, Inc. All rights reserved.
var $ = require('jquery');
var ko = require('knockout');
var _ = require('_');

require('bootstrap/tooltip');
require('bootstrap/popover');

/**
 * Defines a Knockout Custom Binding to use Bootstrap Popover plugin
 *   Depends on Bootstrap Popover Plugin.
 *   The value object of this binding is passed to the Popover plugin, so all the
 *   parameters are available, and also the data attributes definitions.
 *   The default overrides are defined in 'ko.bindingHandlers.popover.options'.
 *   See http://getbootstrap.com/2.3.2/javascript.html#popovers for more information.
 *
 *   Example:
 *     data-bind="popover: {
 *       placement: 'bottom',
 *       title: nameObservable,
 *       content: descriptionObservable
 *   }"
 *
 *   Example:
 *     data-bind="popover: {
 *         title: '<span data-bind="text: myTitle">Hello</span>',
 *        content: '<div data-bind="visible: myVisible">Hello</div>',
 *        hasKoBindings: true
 *     },
 *     myTitle: nameObservable,
 *     myVisible: descriptionObservable
 *   }"
 *
 *   You can also use KO templates for both the title and content, for that use
 *   "titleTemplate" and "titleContent" instead of "title" and "content".
 *
 *   Example:
 *     data-bind="popover: {
 *       titleTemplateName: 'template-popover-title',
 *       templateName: 'template-popover-contents',
 *       trigger: 'click'
 *     }"
 *     ...
 *     <script type="text/html" id="template-popover-contents">
 *       <span data-bind="text: titleObservable"></span>
 *     </script>
 *     <script type="text/html" id="template-popover-contents">
 *       <div data-bind="text: contentObservable"></div>
 *     </script>
 *
 *   The templates will be bound on show and the binding will be removed on
 *   hide.
 *
 *   If you want some action to happen on show and hide you can also supply
 *   a function name to the "onShow" and "onHide" attributes. It will then
 *   call those functions on the viewmodel when KO templates are used.
 *
 *   Example:
 *     data-bind="popover: {
 *       titleTemplate: 'template-popover-title',
 *       contentTemplate: 'template-popover-contents',
 *       onShow: 'fetchContentsUsingAjax',
 *       onHide: 'stopAutoRefresh',
 *       trigger: 'click'
 *     }"
 *     ...
 *     var viewModel = {
 *       contentObservable: ko.observable(),
 *       fetchContentsUsingAjax: function() { ... },
 *       stopAutoRefresh: function() { ... },
 *     }
 **/
ko.bindingHandlers.popover = {
  init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
    var local = ko.utils.unwrapObservable(valueAccessor()),
    $element = $(element);

    $element.attr('role', 'button');
    $element.attr('data-toggle', 'popover');

    // Extend default options with data-bind options
    var options = _.defaults({}, local, ko.bindingHandlers.popover.options);

    var hasKoBindings = false || options.hasKoBindings;

    /**
     * Adds popover options that use either ko template or ko component.
     * @param {string} bindingType The ko binding we want to apply: template or component.
     * @param {string} attr The bootstrap option for a popover: title or content.
     */
    function addKOBinding(bindingType, attr) {
      var optionsBinding = bindingType + 'Name';

      if (attr === 'title') {
        optionsBinding = attr + _.capitalize(optionsBinding);
      }

      if (!_.isUndefined(options[optionsBinding])) {
        hasKoBindings = true;
        options[attr] = '<!-- ko ' + bindingType + ': "' + options[optionsBinding] + '" --><!-- /ko -->';
      }
    }

    addKOBinding('template', 'title');
    addKOBinding('template', 'content');
    addKOBinding('component', 'title');
    addKOBinding('component', 'content');

    // Call the plugin with the options on init
    $element.popover(options);

    var popover = $element.data('bs.popover');

    /**
     * Expose a public function on bootstrap Popover to reposition a popover.
     * Reposition calculates the new position of the popover and applies the placement.
     */
    popover.reposition = function() {
      var popoverEl = this.$tip[0];

      // recalculate position using bootstrap tooltip functions
      var pos = this.getPosition();
      var actualWidth = popoverEl.offsetWidth;
      var actualHeight = popoverEl.offsetHeight;
      var calculatedOffset = this.getCalculatedOffset(options.placement, pos, actualWidth, actualHeight);
      this.applyPlacement(calculatedOffset, options.placement);
    };

    var cleanTooltip = function() {
      if (popover.$tip) {
        ko.cleanNode(popover.$tip[0]);
      }
    };

    // This needs to be done before the popover is shown,
    // to ensure there is no flicker effect.
    $element.on('show.bs.popover', function() {
      if (options.popoverClass) {
        popover.$tip.addClass(options.popoverClass);
      }

      popover.reposition();

      if (!_.isUndefined(options.onShow)) {
        viewModel[options.onShow]();
      }

      popover.$tip.find('button.close').click(function() {
        popover.hide();
      });
    });

    // This needs to be done after the popover is shown.
    $element.on('shown.bs.popover', function() {
      if (hasKoBindings) {
        popover.$tip.data('popover', popover);
        var childBindingContext = bindingContext.createChildContext(viewModel);
        ko.applyBindingsToDescendants(childBindingContext, popover.$tip[0]);

        // Need to reposition the popover just in case.
        popover.reposition();
      }
    });

    $element.on('hidden.bs.popover', function() {
      cleanTooltip();
      if (!_.isUndefined(options.onHide)) {
        viewModel[options.onHide]();
      }
    });

    // Destroy the plugin when DOM node is removed
    ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
      cleanTooltip();
      $(element).popover('destroy');
    });

    // Dismisses the popover when a modal opens or closes
    // note: modals lazy-loaded as text! requirejs modules might not be accounted for
    $('.modal').on('show.bs.modal hide.bs.modal', function() {
      $element.popover('hide');
    });
  },

  // Default plugin options overrides
  options: {
    placement: 'right',
    trigger: 'hover',
    container: 'body',
    html: true
  }
};

function dismissPopovers(event) {
  $('[data-toggle="popover"]').each(function() {
    //the 'is' for buttons that trigger popups
    //the 'has' for icons within a button that triggers a popup
    if (!$(this).is(event.target) && $(this).has(event.target).length === 0) {

      // check whether the clicked target is within the popover content for this popover
      var popover = $(this).data('bs.popover');

      if (popover.$tip && $(popover.$tip[0]).has(event.target).length === 0 && popover.$tip.hasClass('in')) {
        $(this).popover('hide');
      }
    }
  });
}

function repositionPopovers() {
  $('.popover').each(function() {
    if (this.id) {
      var popover = $('[aria-describedby=' + this.id + ']').data('bs.popover');
      if (popover && popover.reposition) {
        popover.reposition();
      }
    }
  });
}
/**
 * Fire a popover reposition for each open popover.
 */
$(window).on('resize', repositionPopovers);

$(document).ready(function() {
  document.addEventListener('scroll', repositionPopovers, true);
});

// handle click outside popover to dismiss popover
$(document)
  .on('click', dismissPopovers)

// dropdowns don't propogate click events, so you have to listen to a shown event instead.
  .on('shown.bs.dropdown', dismissPopovers);
