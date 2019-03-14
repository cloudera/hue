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

import apiHelper from 'api/apiHelper';
import huePubSub from 'utils/huePubSub';

const HALF_SIZE_LIMIT_X = 130;
const HALF_SIZE_LIMIT_Y = 100;

class ResizeHelper {
  constructor(orientation, leftAdjust, topAdjust, preventHideCallback) {
    const self = this;

    let originalMidX,
      originalWidth,
      originalRightX,
      originalLeftX,
      originalMidY,
      originalHeight,
      originalTopY,
      originalBottomY;
    let rightX, leftX, leftDiff, rightDiff, topY, bottomY, topDiff, bottomDiff;
    let redrawHeaders = false;

    const initOriginalValues = function(attempt) {
      if (attempt > 20) {
        return;
      }
      window.setTimeout(() => {
        const offset = $('.hue-popover').offset();
        if (!offset) {
          // Popover isn't visible yet, wait a bit and try again
          attempt++;
          initOriginalValues(attempt);
          return;
        }
        if (orientation === 'right') {
          offset.left -= 5;
        } else if (orientation === 'bottom') {
          offset.top -= 5;
        }
        originalHeight = $('.hue-popover').height();
        originalWidth = $('.hue-popover').width();
        originalMidX = offset.left + originalWidth / 2;
        originalMidY = offset.top + originalHeight / 2;
        originalLeftX = offset.left;
        originalRightX = offset.left + originalWidth;
        originalTopY = offset.top;
        originalBottomY = offset.top + originalHeight;
      }, attempt * 20);
    };

    initOriginalValues(0);

    self.saveSize = function() {
      apiHelper.setInTotalStorage('assist', 'popover.size', {
        width: $('.hue-popover').width(),
        height: $('.hue-popover').height()
      });
    };

    self.resizeStart = function(event, ui) {
      preventHideCallback(true);
    };

    self.resizeStop = function(event, ui) {
      if (redrawHeaders) {
        huePubSub.publish('table.extender.redraw', 'sampleTab');
        redrawHeaders = false;
      }

      huePubSub.publish('context.popover.resized');

      // Delay or it will close the popover when releasing at the window borders
      window.setTimeout(() => {
        preventHideCallback(false);
      }, 300);

      self.saveSize();
    };

    const resizeTopBottomHorizontal = function(event, ui) {
      leftX = ui.position.left;
      rightX = ui.position.left + ui.size.width;

      if (rightX < originalMidX + HALF_SIZE_LIMIT_X) {
        ui.size.width = originalMidX + HALF_SIZE_LIMIT_X - ui.position.left;
        rightX = ui.position.left + ui.size.width;
        $('.hue-popover').css('width', ui.size.width + 'px');
      }

      if (leftX > originalMidX - HALF_SIZE_LIMIT_X) {
        ui.position.left = originalMidX - HALF_SIZE_LIMIT_X;
        ui.size.width = ui.originalSize.width - (ui.position.left - ui.originalPosition.left);
        leftX = ui.position.left;
        rightX = ui.position.left + ui.size.width;
        $('.hue-popover').css('left', ui.position.left + 'px');
        $('.hue-popover').css('width', ui.size.width + 'px');
      }

      leftDiff = originalLeftX - leftX;
      rightDiff = originalRightX - rightX;
      $('.hue-popover-arrow').css('margin-left', (leftDiff + rightDiff) / 2 + leftAdjust() + 'px');
    };

    const resizeLeftRightVertical = function(event, ui) {
      if (!redrawHeaders && ui.originalPosition.top !== ui.position.top) {
        redrawHeaders = true;
        huePubSub.publish('table.extender.hide', 'sampleTab');
      }
      topY = ui.position.top;
      bottomY = ui.position.top + ui.size.height;

      if (bottomY < originalMidY + HALF_SIZE_LIMIT_Y) {
        ui.size.height = originalMidY + HALF_SIZE_LIMIT_Y - ui.position.top;
        bottomY = ui.position.top + ui.size.height;
        $('.hue-popover').css('height', ui.size.height + 'px');
      }

      if (topY > originalMidY - HALF_SIZE_LIMIT_Y) {
        ui.position.top = originalMidY - HALF_SIZE_LIMIT_Y;
        ui.size.height = ui.originalSize.height - (ui.position.top - ui.originalPosition.top);
        topY = ui.position.top;
        bottomY = ui.position.top + ui.size.height;
        $('.hue-popover').css('top', ui.position.top + 'px');
        $('.hue-popover').css('height', ui.size.height + 'px');
      }

      topDiff = originalTopY - topY;
      bottomDiff = originalBottomY - bottomY;
      $('.hue-popover-arrow').css('margin-top', (topDiff + bottomDiff) / 2 + topAdjust() + 'px');
    };

    switch (orientation) {
      case 'top':
        self.resizableHandles = 'w, nw, n, ne, e';
        self.resize = function(event, ui) {
          resizeTopBottomHorizontal(event, ui);
          // TODO: Implement resize height limits when popover is above
        };
        break;
      case 'right':
        self.resizableHandles = 'n, ne, e, se, s';
        self.resize = function(event, ui) {
          resizeLeftRightVertical(event, ui);
          if (ui.size.width < 350) {
            ui.size.width = 350;
            $('.hue-popover').css('width', 350 + 'px');
          }
        };
        break;
      case 'bottom':
        self.resizableHandles = 'e, se, s, sw, w';
        self.resize = function(event, ui) {
          resizeTopBottomHorizontal(event, ui);
          if (ui.size.height < 200) {
            ui.size.height = 200;
            $('.hue-popover').css('height', 200 + 'px');
          }
        };
        break;
      case 'left':
        self.resizableHandles = 's, sw, w, nw, n';
        self.resize = function(event, ui) {
          resizeLeftRightVertical(event, ui);
          // TODO: Implement resize width limits when popover is on the left
        };
        break;
    }
  }
}

export default ResizeHelper;
