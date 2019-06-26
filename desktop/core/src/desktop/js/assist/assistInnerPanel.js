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

import ko from 'knockout';

import apiHelper from 'api/apiHelper';

class AssistInnerPanel {
  /**
   * @param {Object} options
   * @param {string} options.type
   * @param {number} options.minHeight
   * @param {string} options.icon
   * @param {boolean} [options.rightAlignIcon] - Default false
   * @param {boolean} options.visible
   * @param {(AssistDbPanel|AssistHdfsPanel|AssistGitPanel|AssistDocumentsPanel|AssistS3Panel)} panelData
   * @constructor
   */
  constructor(options) {
    const self = this;
    self.minHeight = options.minHeight;
    self.icon = options.icon;
    self.type = options.type;
    self.name = options.name;
    self.panelData = options.panelData;
    self.rightAlignIcon = !!options.rightAlignIcon;
    self.iconSvg = options.iconSvg;

    self.visible = ko.observable(options.visible || true);
    apiHelper.withTotalStorage(
      'assist',
      'showingPanel_' + self.type,
      self.visible,
      false,
      options.visible
    );

    self.templateName =
      'assist-' +
      (['solr', 'kafka'].indexOf(self.type) !== -1 ? 'sql' : self.type) +
      '-inner-panel';

    const loadWhenVisible = () => {
      if (!self.visible()) {
        return;
      }
      if (self.type === 'documents' && !self.panelData.activeEntry().loaded()) {
        self.panelData.activeEntry().load();
      }
    };

    self.visible.subscribe(loadWhenVisible);
    loadWhenVisible();
  }
}

export default AssistInnerPanel;
