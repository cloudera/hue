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

class LangRefContext {
  constructor(options) {
    const self = this;
    self.popover = options.popover;
    self.title = ko.observable();
    self.body = ko.observable();

    self.topicId =
      'topics/impala_' + options.data.identifier.toLowerCase().replace(/ /g, '_') + '.xml';

    $.get(window.IMPALA_DOC_INDEX[self.topicId]).done(topic => {
      self.title(topic.title);
      self.body(topic.body);
    });

    $('.hue-popover').on('click.contextLangRef', event => {
      if (event.target.className === 'hue-doc-internal-link') {
        huePubSub.publish('assist.lang.ref.show.topic', {
          ref: $(event.target).data('doc-ref'),
          anchorId: $(event.target).data('doc-anchor-id')
        });
      }
    });
  }

  dispose() {
    $('.hue-popover').off('click.contextLangRef');
  }

  openInRightAssist() {
    const self = this;
    huePubSub.publish('assist.lang.ref.show.topic', { ref: self.topicId });
    huePubSub.publish('context.popover.hide');
  }
}

export default LangRefContext;
