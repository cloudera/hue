import $ from 'jquery';
import * as ko from 'knockout';

/**
 * This binding can be used to emulate position sticky for any element.
 *
 * Example:
 *
 * <div databind="stickVertical: { scrollContainer: '.some-container' }">...</div>
 *
 * @type {{init: ko.bindingHandlers.stickVertical.init}}
 */
ko.bindingHandlers.stickVertical = {
  init: function (element, valueAccessor) {
    const options = valueAccessor() || {};

    const $scrollContainer = $(options.scrollContainer || window);
    const $element = $(element);
    const $parent = $element.parent();

    let active = false;

    let throttleTimeout = -1;
    const throttledReposition = () => {
      window.clearTimeout(throttleTimeout);
      throttleTimeout = window.setTimeout(() => {
        const diff = $scrollContainer.offset().top - $parent.offset().top;
        if (diff > 0) {
          $element.animate({ 'margin-top': diff + 'px' }, 40);
          active = true;
        } else if (active) {
          $element.css({ 'margin-top': '' });
          active = false;
        }
      }, 50);
    };

    $scrollContainer.on('scroll.stickVertical', throttledReposition);
    $(window).on('resize.stickVertical', throttledReposition);

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      $scrollContainer.off('scroll.stickVertical');
      $(window).off('resize.stickVertical');
    });
  }
};
