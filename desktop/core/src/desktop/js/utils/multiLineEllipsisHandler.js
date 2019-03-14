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
import ko from 'knockout';

import hueUtils from 'utils/hueUtils';

const checkOverflow = function(element) {
  return element.offsetHeight < element.scrollHeight || element.offsetWidth < element.scrollWidth;
};

class MultiLineEllipsisHandler {
  constructor(options) {
    const self = this;

    self.element = options.element;
    self.$element = $(options.element);
    self.overflowHeight = options.overflowHeight;
    self.expandable = options.expandable;
    self.expandClass = options.expandClass;
    self.expandActionClass = options.expandActionClass;
    self.overflowing = options.overflowing;

    self.onActionRender = options.onActionRender;

    self.lastKnownOffsetHeight;
    self.lastKnownOffsetWidth;
    self.isOverflowing;

    self.expanded = options.expanded || ko.observable(false);
    self.updateOverflowHeight();

    self.contents = options.text;
    self.element.innerHTML = self.contents;

    const linkRegex = /(?:(?:[a-z]+:\/\/)|www\.)[^\s\/]+(?:[.\/]\S+)*[^\s`!()\[\]{};:'".,<>?«»“”‘’]/gi;

    self.renderContents = function(contents) {
      if (options.linkify) {
        return hueUtils.deXSS(
          contents.replace(linkRegex, val => {
            return (
              '<a href="' +
              (val.toLowerCase().indexOf('www') === 0 ? 'http://' + val : val) +
              '" target="_blank">' +
              val +
              '</a>'
            );
          })
        );
      }
      return hueUtils.deXSS(contents);
    };

    self.delayedResumeTimeout = window.setTimeout(() => {
      self.resume();
    }, 0);
  }

  updateOverflowHeight() {
    const self = this;
    if (self.overflowHeight) {
      self.$element.css('max-height', self.expanded() ? '' : self.overflowHeight);
      self.$element.css('overflow', self.expanded() ? '' : 'hidden');
    }
  }

  resume() {
    const self = this;
    self.refresh();
    window.clearInterval(self.sizeCheckInterval);
    self.sizeCheckInterval = window.setInterval(() => {
      if (
        self.element.offsetWidth !== self.lastKnownOffsetWidth ||
        self.element.offsetHeight !== self.lastKnownOffsetHeight
      ) {
        self.refresh();
      }
    }, 500);
  }

  pause() {
    const self = this;
    window.clearTimeout(self.delayedResumeTimeout);
    window.clearInterval(self.sizeCheckInterval);
  }

  dispose() {
    const self = this;
    self.pause();
  }

  refresh() {
    const self = this;
    self.$element.empty();
    const textElement = $('<span>').appendTo(self.$element)[0];
    if (self.expandable) {
      textElement.innerHTML = self.renderContents
        ? self.renderContents(self.contents)
        : self.contents;
      if (self.expanded() || checkOverflow(self.element)) {
        self.$element.append('&nbsp;');
        const $expandLink = $(
          '<a href="javascript:void(0);"><i class="fa fa-fw ' +
            (self.expanded() ? 'fa-chevron-up' : 'fa-chevron-down') +
            '"></i></a>'
        );
        if (self.expandActionClass) {
          $expandLink.addClass(self.expandActionClass);
        }
        $expandLink.appendTo(self.$element);
        $expandLink.add(textElement).click(e => {
          self.expanded(!self.expanded());
          self.updateOverflowHeight();
          if (self.expanded()) {
            if (self.expandClass) {
              self.$element.addClass(self.expandClass);
            }
            self.refresh();
            self.pause();
          } else {
            if (self.expandClass) {
              self.$element.removeClass(self.expandClass);
            }
            self.resume();
          }
        });
      }
    } else {
      textElement.innerHTML = self.renderContents
        ? self.renderContents(self.contents)
        : self.contents;
    }

    if (self.onActionRender) {
      self.onActionRender(self.$element, checkOverflow(self.element));
    }

    self.isOverflowing = false;

    if (!self.expanded()) {
      while (checkOverflow(self.element)) {
        self.isOverflowing = true;
        const contents = $(textElement).contents();
        const lastContent = contents[contents.length - 1];
        // Check for text node
        if (lastContent.nodeType === 3) {
          const lastSpaceIndex = lastContent.textContent.regexLastIndexOf(/\s\S+/);
          if (lastSpaceIndex !== -1) {
            lastContent.replaceWith(
              document.createTextNode(lastContent.textContent.substring(0, lastSpaceIndex) + '...')
            );
          } else if (contents.length > 1) {
            textElement.removeChild(lastContent);
          } else {
            break;
          }
        } else if (contents.length > 1) {
          // Remove any elements like links
          textElement.removeChild(lastContent);
        }
      }
    }

    if (ko.isObservable(self.overflowing) && self.overflowing() !== self.isOverflowing) {
      self.overflowing(self.isOverflowing);
    }
    self.lastKnownOffsetHeight = self.element.offsetHeight;
    self.lastKnownOffsetWidth = self.element.offsetWidth;
  }

  setText(text) {
    const self = this;
    self.contents = text;
    self.refresh();
  }
}

export default MultiLineEllipsisHandler;
