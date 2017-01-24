// Copyright (c) 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/helpIcon
 * @description Help icon component
 * Example: <cui-help-icon params="popoverOptions: {container: 'body'}">
 *           Lorem ipsum helper
 *          </cui-help-icon>
 */

import componentUtils from 'cloudera-ui/ko/components/componentUtils';
import i18n from 'cloudera-ui/utils/i18n';
import ko from 'knockout';
import $ from 'jquery';
import _ from '_';
import 'cloudera-ui/ko/bindings/popover';

class HelpIcon {
  /**
   * @constructor
   * @alias module:ko/components/helpIcon
   * @param {object} [params.popoverOptions] Optional popover arguments.  Defaults to {html:true}
   *        For the title param in popoverOptions, we look for the title in params, then the element title, and finally data-title.
   */
  constructor(params, componentInfo) {
    var $element = $(componentInfo.element);

    /**
      * Title tooltip shown before popover is triggered.
      */
    this.title = params.title || $element.attr('title') || $element.attr('data-title');

    var templateNodesAsString = $('<div>').append(componentInfo.templateNodes).html();

    // the ko binding is applied to the value returned by params.content;
    // so if the value is html mutations will be bound, however,
    //  if params.content is an observable returning a plain string
    //  the observable's mutation will not be bound
    var content = ko.utils.unwrapObservable(params.content) || templateNodesAsString;

    /**
      * Default options for the popover.
      */
    this.myDefaults = {
      content: function() {
        return content;
      },
      html: true,
      trigger: 'click',
      container: componentInfo.element,
      popoverClass: 'cui-popover-lg'
    };

    /**
      * If title is available, pass that to the popover defaults (otherwise a title header won't be present in the popover).
      */
    if (this.title) {
      this.myDefaults.title = this.title;
    }

    /**
      * Options for the popover merged with the customizations the user passes in.
      */
    this.popoverOptions = _.defaults({}, params.popoverOptions, this.myDefaults);
  }
}

var template = `
<span class="btn btn-primary cui-help-icon cui-icon-question" data-bind="attr: {title: title}, popover: popoverOptions" data-toggle="popover"></span>
`;

componentUtils.addComponent(HelpIcon, 'cui-help-icon', template);

module.exports = HelpIcon;
