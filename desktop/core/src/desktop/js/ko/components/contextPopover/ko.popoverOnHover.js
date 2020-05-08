// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import $ from 'jquery';
import * as ko from 'knockout';
import { CONTEXT_POPOVER_CLASS, CONTEXT_POPOVER_HIDDEN_EVENT } from './ko.contextPopover';
import huePubSub from 'utils/huePubSub';

import { HIDE_CONTEXT_POPOVER_EVENT } from './ko.contextPopover';

const DEFAULT_DELAY = 700;

export const NAME = 'popoverOnHover';

ko.bindingHandlers[NAME] = {
  init: (element, valueAccessor, allBindings, viewModel, bindingContext) => {
    let options = valueAccessor();
    const $element = $(element);
    const popoverSelector = '.' + CONTEXT_POPOVER_CLASS;

    if (typeof options === 'function') {
      options = {
        onHover: options,
        delay: DEFAULT_DELAY
      };
    }

    let visible = false;
    let clickedOpen = false;
    let showTimeout = -1;
    let hideTimeout = -1;

    const clearTimeouts = () => {
      window.clearTimeout(showTimeout);
      window.clearTimeout(hideTimeout);
    };

    const hide = () => {
      clearTimeouts();
      hideTimeout = window.setTimeout(() => {
        visible = false;
        $(popoverSelector).off('.onHover');
        huePubSub.publish(HIDE_CONTEXT_POPOVER_EVENT);
      }, options.delay);
    };

    const show = event => {
      clearTimeouts();
      if (visible) {
        return;
      }

      showTimeout = window.setTimeout(() => {
        visible = true;
        huePubSub.publish(HIDE_CONTEXT_POPOVER_EVENT);
        options.onHover.bind(bindingContext.$data)(
          bindingContext.$data,
          event,
          options.positionAdjustments
        );
      }, options.delay);
    };

    $element.on('click.onHover', event => {
      clearTimeouts();
      clickedOpen = true;
      visible = true;
      options.onHover.bind(bindingContext.$data)(
        bindingContext.$data,
        event,
        options.positionAdjustments
      );
    });

    $element.on('mouseenter.onHover', show);

    $element.on('mouseleave.onHover', () => {
      if (clickedOpen) {
        return;
      }
      clearTimeouts();
      // Keep open if mouse moves to the context popover
      if (visible) {
        const $popoverSelector = $(popoverSelector);
        $popoverSelector.on('mouseenter.onHover', () => {
          clearTimeouts();
        });
        $popoverSelector.on('mouseleave.onHover', () => {
          hide();
        });
        hide();
      }
    });

    const hiddenSub = huePubSub.subscribe(CONTEXT_POPOVER_HIDDEN_EVENT, () => {
      visible = false;
      clickedOpen = false;
    });

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      $element.off('.onHover');
      $(popoverSelector).off('.onHover');
      clearTimeouts();
      hiddenSub.remove();
      if (visible) {
        huePubSub.publish(HIDE_CONTEXT_POPOVER_EVENT);
      }
    });
  }
};
