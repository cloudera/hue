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

import deXSS from 'utils/html/deXSS';

const checkOverflow = element =>
  element &&
  (element.offsetHeight < element.scrollHeight || element.offsetWidth < element.scrollWidth);

class MultiLineEllipsisHandler {
  constructor(options) {
    this.element = options.element;
    this.$element = $(options.element);
    this.overflowHeight = options.overflowHeight;
    this.expandable = options.expandable;
    this.expandClass = options.expandClass;
    this.expandActionClass = options.expandActionClass;
    this.overflowing = options.overflowing;

    this.onActionRender = options.onActionRender;

    this.lastKnownOffsetHeight;
    this.lastKnownOffsetWidth;
    this.isOverflowing;

    this.expanded = options.expanded || ko.observable(false);
    this.updateOverflowHeight();

    this.contents = options.text;
    this.element.innerHTML = deXSS(this.contents);

    const linkRegex =
      /(?:(?:[a-z]+:\/\/)|www\.)[^\s\/]+(?:[.\/]\S+)*[^\s`!()\[\]{};:'".,<>?«»“”‘’]/gi;

    this.renderContents = contents => {
      if (options.linkify) {
        return deXSS(
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
      return deXSS(contents);
    };

    this.delayedResumeTimeout = window.setTimeout(() => {
      this.resume();
    }, 0);
  }

  updateOverflowHeight() {
    if (this.overflowHeight) {
      this.$element.css('max-height', this.expanded() ? '' : this.overflowHeight);
      this.$element.css('overflow', this.expanded() ? '' : 'hidden');
    }
  }

  resume() {
    this.refresh();
    window.clearInterval(this.sizeCheckInterval);
    this.sizeCheckInterval = window.setInterval(() => {
      if (
        this.element.offsetWidth !== this.lastKnownOffsetWidth ||
        this.element.offsetHeight !== this.lastKnownOffsetHeight
      ) {
        this.refresh();
      }
    }, 500);
  }

  pause() {
    window.clearTimeout(this.delayedResumeTimeout);
    window.clearInterval(this.sizeCheckInterval);
  }

  dispose() {
    this.pause();
  }

  refresh() {
    this.$element.empty();
    const textElement = $('<span>').appendTo(this.$element)[0];
    if (this.expandable) {
      textElement.innerHTML = this.renderContents
        ? this.renderContents(this.contents)
        : this.contents;
      if (this.expanded() || checkOverflow(this.element)) {
        this.$element.append('&nbsp;');
        const $expandLink = $(
          '<a href="javascript:void(0);"><i class="fa fa-fw ' +
            (this.expanded() ? 'fa-chevron-up' : 'fa-chevron-down') +
            '"></i></a>'
        );
        if (this.expandActionClass) {
          $expandLink.addClass(this.expandActionClass);
        }
        $expandLink.appendTo(this.$element);
        $expandLink.add(textElement).click(e => {
          this.expanded(!this.expanded());
          this.updateOverflowHeight();
          if (this.expanded()) {
            if (this.expandClass) {
              this.$element.addClass(this.expandClass);
            }
            this.refresh();
            this.pause();
          } else {
            if (this.expandClass) {
              this.$element.removeClass(this.expandClass);
            }
            this.resume();
          }
        });
      }
    } else {
      textElement.innerHTML = this.renderContents
        ? this.renderContents(this.contents)
        : this.contents;
    }

    if (this.onActionRender) {
      this.onActionRender(this.$element, checkOverflow(this.element));
    }

    this.isOverflowing = false;

    if (!this.expanded()) {
      while (checkOverflow(this.element)) {
        this.isOverflowing = true;
        const contents = $(textElement).contents();
        const lastContent = contents[contents.length - 1];
        // Check for text node
        if (lastContent && lastContent.nodeType === 3) {
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
        } else if (contents && contents.length > 1) {
          // Remove any elements like links
          textElement.removeChild(lastContent);
        } else {
          console.warn('Failed adjusting text length in element:');
          console.warn(textElement);
          break;
        }
      }
    }

    if (ko.isObservable(this.overflowing) && this.overflowing() !== this.isOverflowing) {
      this.overflowing(this.isOverflowing);
    }
    this.lastKnownOffsetHeight = this.element.offsetHeight;
    this.lastKnownOffsetWidth = this.element.offsetWidth;
  }

  setText(text) {
    this.contents = text;
    this.refresh();
  }
}

export default MultiLineEllipsisHandler;
