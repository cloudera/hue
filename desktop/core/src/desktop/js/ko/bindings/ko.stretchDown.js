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

import huePubSub from 'utils/huePubSub';

ko.bindingHandlers.stretchDown = {
  init: function(element) {
    const $element = $(element);
    const $parent = $element.parent();

    let lastParentHeight = -1;
    let lastTop = -1;

    function stretch(force) {
      if (
        lastParentHeight !== $parent.innerHeight() ||
        lastTop !== $element.position().top ||
        force
      ) {
        lastParentHeight = $parent.innerHeight();
        lastTop = $element.position().top;
        $element.height(
          lastParentHeight - lastTop - ($element.outerHeight(true) - $element.innerHeight())
        );
        huePubSub.publish('assist.stretchDown', $element);
      }
    }

    window.setInterval(stretch, 200);
    huePubSub.subscribe('assist.forceStretchDown', () => {
      stretch(true);
    });
  }
};
