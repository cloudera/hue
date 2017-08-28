## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
from django.utils.translation import ugettext as _
%>

<%def name="contextPopover()">

  <script type="text/html" id="context-contents-hive-template">
    Hive: <a href="javascript: void(0);" data-bind="click: function () { console.log($data); }">Click me!</a>
  </script>

  <script type="text/html" id="context-contents-impala-template">
    Impala: <a href="javascript: void(0);" data-bind="click: function () { console.log($data); }">Click me!</a>
  </script>

  <script type="text/javascript">
    (function () {
      function ContextContentsHive() {
        var self = this;
      }

      function ContextContentsImpala() {
        var self = this;
      }

      ko.components.register('context-contents-hive', {
        viewModel: ContextContentsHive,
        template: { element: 'context-contents-hive-template' }
      });

      ko.components.register('context-contents-impala', {
        viewModel: ContextContentsImpala,
        template: { element: 'context-contents-impala-template' }
      });
    })();
  </script>

  <script type="text/html" id="context-contents-hdfs-template">
    HDFS: <a href="javascript: void(0);" data-bind="click: function () { console.log($data); }">Click me!</a>
  </script>

  <script type="text/html" id="context-contents-s3-template">
    S3: <a href="javascript: void(0);" data-bind="click: function () { console.log($data); }">Click me!</a>
  </script>

  <script type="text/javascript">
    (function () {
      function ContextContentsHdfs() {
        var self = this;
      }

      function ContextContentsS3() {
        var self = this;
      }

      ko.components.register('context-contents-hdfs', {
        viewModel: ContextContentsHdfs,
        template: { element: 'context-contents-hdfs-template' }
      });

      ko.components.register('context-contents-s3', {
        viewModel: ContextContentsS3,
        template: { element: 'context-contents-s3-template' }
      });
    })();
  </script>

  <script type="text/html" id="context-contents-hue-template">
    Hue: <a href="javascript: void(0);" data-bind="click: function () { console.log($data); }">Click me!</a>
  </script>

  <script type="text/javascript">
    (function () {
      function ContextContentsHue() {
        var self = this;
      }

      ko.components.register('context-contents-hue', {
        viewModel: ContextContentsHue,
        template: { element: 'context-contents-hue-template' }
      });
    })();
  </script>

  <script type="text/html" id="context-popover-contents">
    <div class="context-popover-content"><a href="javascript: void(0);" data-bind="click: function () { console.log($data); }">Click me!</a></div>
  </script>

  <script type="text/html" id="context-popover-template">
    <div class="hue-popover hue-context-popover" data-bind="css: orientationClass, style: { 'left': left() + 'px', 'top': top() + 'px', 'width': width() + 'px', height: height() + 'px' }, resizable: { containment: 'document', handles: resizeHelper.resizableHandles, start: resizeHelper.resizeStart, stop: resizeHelper.resizeStop, resize: resizeHelper.resize }">
      <div class="hue-popover-arrow" data-bind="style: { 'margin-left': leftAdjust() + 'px',  'margin-top': topAdjust() + 'px' }"></div>
      <div class="hue-popover-title context-popover-title">
        <div class="context-popover-breadcrumbs" data-bind="component: { name: 'hue-breadcrumbs', params: { breadcrumbs: breadcrumbs, onSelect: onBreadcrumbSelect } }"></div>
        <div class="context-popover-close">
          <a class="pointer inactive-action" data-bind="click: close"><i class="fa fa-fw fa-times"></i></a>
        </div>
      </div>
      <!-- ko with: activeEntry -->
      <!-- ko component: { name: 'context-contents-' + sourceType, params: { data: $data } } --><!-- /ko -->
      <!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
    (function () {

      var CONTEXT_POPOVER_ID = 'contextPopover';
      var HALF_SIZE_LIMIT_X = 130;
      var HALF_SIZE_LIMIT_Y = 100;
      var HALF_ARROW = 6;

      var preventHide = false;
      var intervals = [];
      var pubSubs = [];

      var hidePopover = function () {
        if (! preventHide) {
          if ($('#' + CONTEXT_POPOVER_ID).length > 0) {
            ko.cleanNode($('#' + CONTEXT_POPOVER_ID)[0]);
            huePubSub.publish('context.popover.dispose');
            $('#' + CONTEXT_POPOVER_ID).remove();
            $(document).off('click', hideOnClickOutside);
            while (intervals.length > 0) {
              window.clearInterval(intervals.pop());
            }
            while (pubSubs.length > 0) {
              pubSubs.pop().remove();
            }
            huePubSub.publish('context.popover.hidden');
          }
        }
      };

      var hideOnClickOutside = function (event) {
        if (jQuery.contains(document, event.target) && !$.contains($('#' + CONTEXT_POPOVER_ID)[0], event.target) && ($('.modal')[0].length === 0 || !$.contains($('.modal')[0], event.target))) {
          hidePopover();
        }
      };

      function ResizeHelper(orientation, leftAdjust, topAdjust) {
        var self = this;

        var apiHelper = ApiHelper.getInstance();

        var originalMidX, originalWidth, originalRightX, originalLeftX, originalMidY, originalHeight, originalTopY, originalBottomY;
        var rightX, leftX, leftDiff, rightDiff, topY, bottomY, topDiff, bottomDiff;
        var redrawHeaders = false;

        window.setTimeout(function () {
          var offset = $('.hue-popover').offset();
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
        }, 0);

        self.saveSize = function () {
          apiHelper.setInTotalStorage('assist', 'popover.size', {
            width: $('.hue-popover').width(),
            height: $('.hue-popover').height()
          });
        };

        self.resizeStart = function (event, ui) {
          preventHide = true;
        };

        self.resizeStop = function (event, ui) {
          if (redrawHeaders) {
            huePubSub.publish('table.extender.redraw', 'sampleTab');
            redrawHeaders = false;
          }

          huePubSub.publish('context.popover.resized');

          // Delay or it will close the popover when releasing at the window borders
          window.setTimeout(function () {
            preventHide = false;
          }, 300);

          self.saveSize();
        };

        var resizeTopBottomHorizontal = function (event, ui) {
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

        var resizeLeftRightVertical = function (event, ui) {
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

        switch(orientation) {
          case 'top':
            self.resizableHandles = "w, nw, n, ne, e";
            self.resize = function (event, ui) {
              resizeTopBottomHorizontal(event, ui);
              // TODO: Implement resize height limits when popover is above
            };
            break;
          case 'right':
            self.resizableHandles = "n, ne, e, se, s";
            self.resize = function (event, ui) {
              resizeLeftRightVertical(event, ui);
              if (ui.size.width < 350) {
                ui.size.width = 350;
                $('.hue-popover').css('width', 350 + 'px');
              }
            };
            break;
          case 'bottom':
            self.resizableHandles = "e, se, s, sw, w";
            self.resize = function (event, ui) {
              resizeTopBottomHorizontal(event, ui);
              if (ui.size.height < 200) {
                ui.size.height = 200;
                $('.hue-popover').css('height', 200 + 'px');
              }
            };
            break;
          case 'left':
            self.resizableHandles = "s, sw, w, nw, n";
            self.resize = function (event, ui) {
              resizeLeftRightVertical(event, ui);
              // TODO: Implement resize width limits when popover is on the left
            };
            break;
        }
      }

      var generateBreadcrumbs = function (params) {
        if ((params.sourceType === 'hive' || params.sourceType === 'impala') && params.data.type !== 'hdfs') {
          var breadcrumbs = [];
          var currentPath = [];
          params.data.identifierChain.forEach(function (identifier) {
            currentPath.push(identifier.name);
            breadcrumbs.push({
              label: identifier.name,
              sourceType: params.sourceType,
              path: currentPath.concat(),
              defaultDatabase: params.defaultDatabase
            })
          });
          return breadcrumbs;
        } else if (params.data && params.data.type === 'hdfs') {
          var breadcrumbs = [];
          var currentPath = [];
          var type = 'hdfs';
          if (/^s3a?:\/\//i.test(params.data.path)) {
            type = 's3'
          }
          params.data.path.replace(/^[a-z0-9]+:\/\//i, '').split('/').forEach(function (pathPart) {
            if (pathPart) {
              currentPath.push(pathPart);
              breadcrumbs.push({
                label: pathPart,
                sourceType: type,
                path: currentPath.concat()
              })
            }
          });
          return breadcrumbs;
        } else {
          return [];
        }
      };

      function ContextPopoverViewModel(params) {
        var self = this;
        self.disposalFunctions = [];

        var apiHelper = ApiHelper.getInstance();

        self.left = ko.observable(0);
        self.top = ko.observable(0);

        self.breadcrumbs = ko.observableArray(generateBreadcrumbs(params));
        self.activeEntry = ko.observable(self.breadcrumbs()[self.breadcrumbs().length - 1]);

        self.onBreadcrumbSelect = function (breadcrumb) {
          var newBreadcrumbs = [];
          self.breadcrumbs().every(function (existingBreadcrumb) {
            newBreadcrumbs.push(existingBreadcrumb);
            return existingBreadcrumb !== breadcrumb;
          });
          self.activeEntry(newBreadcrumbs[newBreadcrumbs.length - 1]);
          self.breadcrumbs(newBreadcrumbs);
        };

        self.showInAssistEnabled = typeof params.showInAssistEnabled !== 'undefined' ? params.showInAssistEnabled : true;

        var popoverSize = apiHelper.getFromTotalStorage('assist', 'popover.size', {
          width: 450,
          height: 400
        });

        self.width = ko.observable(popoverSize.width);
        self.height = ko.observable(popoverSize.height);

        self.leftAdjust = ko.observable(0);
        self.topAdjust = ko.observable(0);
        self.data = params.data;
        self.sourceType = params.sourceType;
        self.defaultDatabase = params.defaultDatabase;
        self.close = hidePopover;
        var orientation = params.orientation || 'bottom';
        self.contents = null;
        self.resizeHelper = new ResizeHelper(orientation, self.leftAdjust, self.topAdjust);

        if (typeof params.source.element !== 'undefined') {
          // Track the source element and close the popover if moved
          var $source = $(params.source.element);
          var originalSourceOffset = $source.offset();
          var currentSourceOffset;
          intervals.push(window.setInterval(function () {
            currentSourceOffset = $source.offset();
            if (currentSourceOffset.left !== originalSourceOffset.left || currentSourceOffset.top !== originalSourceOffset.top) {
              hidePopover();
            }
          }, 200));
        }

        var windowWidth = $(window).width();
        var fitHorizontally = function () {
          var left = params.source.left + Math.round((params.source.right - params.source.left) / 2) - (self.width() / 2);
          if (left + self.width() > windowWidth - 10) {
            self.leftAdjust(left + self.width() - windowWidth + 5);
            left = windowWidth - self.width() - 10;
          } else if (left < 10) {
            self.leftAdjust(left - 10 - HALF_ARROW);
            left = 10;
          } else {
            self.leftAdjust(-HALF_ARROW);
          }
          self.left(left);
        };

        var windowHeight = $(window).height();
        var fitVertically = function () {
          var top = params.source.top + Math.round((params.source.bottom - params.source.top) / 2) - (self.height() / 2);
          if (top + self.height() > windowHeight - 10) {
            self.topAdjust(top + self.height() - windowHeight + 5);
            top = windowHeight - self.height() - 10;
          } else if (top < 10) {
            self.topAdjust(top - 10 - HALF_ARROW);
            top = 10;
          } else {
            self.topAdjust(-HALF_ARROW);
          }
          self.top(top);
        };

        switch (orientation) {
          case 'top':
            fitHorizontally();
            self.top(params.source.top - self.height());
            break;
          case 'right':
            fitVertically();
            self.left(params.source.right);
            break;
          case 'bottom':
            fitHorizontally();
            self.top(params.source.bottom);
            break;
          case 'left':
            fitVertically();
            self.left(params.source.left - self.width());
        }

        self.orientationClass = 'hue-popover-' + orientation;

        if (params.delayedHide) {
          var hideTimeout = -1;
          var onLeave = function () {
            hideTimeout = window.setTimeout(function () {
              $('.hue-popover').fadeOut(200, function () {
                hidePopover();
              })
            }, 1000);
          };

          var onEnter = function () {
            window.clearTimeout(hideTimeout);
          };

          $(params.delayedHide).add($('.hue-popover')).on('mouseleave', onLeave).on('mouseenter', onEnter);

          var keepPopoverOpenOnClick = function () {
            window.clearTimeout(hideTimeout);
            $(params.delayedHide).add($('.hue-popover')).off('mouseleave', onLeave).off('mouseenter', onEnter);
          };

          $('.hue-popover').on('click', keepPopoverOpenOnClick);

          self.disposalFunctions.push(function () {
            $(params.delayedHide).add($('.hue-popover')).off('mouseleave', onLeave).off('mouseenter', onEnter);
            $('.hue-popover').off('click', keepPopoverOpenOnClick);
          });
        }

        var closeOnEsc = function (e) {
          if (e.keyCode === 27) {
            hidePopover();
          }
        };

        $(document).on('keyup', closeOnEsc);

        self.disposalFunctions.push(function () {
          $(document).off('keyup', closeOnEsc);
        });

        window.setTimeout(function() {
          $(document).on('click', hideOnClickOutside);
        }, 0);

        self.disposalFunctions.push(function () {
          $(document).off('click', hideOnClickOutside);
        })
      }

      ContextPopoverViewModel.prototype.dispose = function() {
        var self = this;
        self.disposalFunctions.forEach(function (fn) {
          fn();
        })
      };

      ko.components.register('context-popover', {
        viewModel: ContextPopoverViewModel,
        template: { element: 'context-popover-template' }
      });

      huePubSub.subscribe('context.popover.hide', hidePopover);

      huePubSub.subscribe('context.popover.show', function (details) {
        hidePopover();
        var $contextPopover = $('<div id="' + CONTEXT_POPOVER_ID + '" data-bind="component: { name: \'context-popover\', params: $data }" />');
        $('body').append($contextPopover);
        ko.applyBindings(details, $contextPopover[0]);
        huePubSub.publish('context.popover.shown');
      });
    })();
  </script>
</%def>