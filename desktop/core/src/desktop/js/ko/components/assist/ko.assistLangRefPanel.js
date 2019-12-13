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

import apiHelper from 'api/apiHelper';
import componentUtils from 'ko/components/componentUtils';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

// prettier-ignore
const TEMPLATE = `
  <script type="text/html" id="language-reference-topic-tree">
    <!-- ko if: $data.length -->
    <ul class="assist-docs-topic-tree " data-bind="foreach: $data">
      <li>
        <a class="black-link" href="javascript: void(0);" data-bind="click: function () { $component.selectedTopic($data); }, toggle: open">
          <i class="fa fa-fw" style="font-size: 12px;" data-bind="css: { 'fa-chevron-right': children.length && !open(), 'fa-chevron-down': children.length && open() }"></i>
          <span class="assist-field-link" href="javascript: void(0);" data-bind="css: { 'blue': $component.selectedTopic() === $data }, text: title"></span>
        </a>
        <!-- ko if: open -->
        <!-- ko template: { name: 'language-reference-topic-tree', data: children } --><!-- /ko -->
        <!-- /ko -->
      </li>
    </ul>
    <!-- /ko -->
  </script>

  <div class="assist-inner-panel">
    <div class="assist-flex-panel">
      <div class="assist-flex-header">
        <div class="assist-inner-header">
          <div class="function-dialect-dropdown" data-bind="component: { name: 'hue-drop-down', params: { fixedPosition: true, value: sourceType, entries: availableTypes, linkTitle: '${I18n(
            'Selected dialect'
          )}' } }" style="display: inline-block"></div>
        </div>
      </div>
      <div class="assist-flex-search">
        <div class="assist-filter">
          <form autocomplete="off">
            <input class="clearable" type="text" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS } placeholder="Filter..." data-bind="clearable: query, value: query, valueUpdate: 'afterkeydown'">
          </form>
        </div>
      </div>
      <div class="assist-docs-topics" data-bind="css: { 'assist-flex-fill': !selectedTopic(), 'assist-flex-40': selectedTopic() }">
        <!-- ko ifnot: query -->
        <!-- ko template: { name: 'language-reference-topic-tree', data: topics } --><!-- /ko -->
        <!-- /ko -->
        <!-- ko if: query -->
        <!-- ko if: filteredTopics().length > 0 -->
        <ul class="assist-docs-topic-tree" data-bind="foreach: filteredTopics">
          <li>
            <a class="assist-field-link" href="javascript: void(0);" data-bind="css: { 'blue': $component.selectedTopic() === $data }, click: function () { $component.selectedTopic($data); }, html: titleMatch() || title"></a>
          </li>
        </ul>
        <!-- /ko -->
        <!-- ko if: filteredTopics().length === 0 -->
        <ul class="assist-docs-topic-tree">
          <li class="assist-no-entries">${I18n('No results found.')}</li>
        </ul>
        <!-- /ko -->
        <!-- /ko -->
      </div>
      <!-- ko if: selectedTopic -->
      <div class="assist-flex-60 assist-docs-details" data-bind="with: selectedTopic">
        <div class="assist-panel-close"><button class="close" data-bind="click: function() { $component.selectedTopic(undefined); }">&times;</button></div>
        <div data-bind="html: bodyMatch() || body()"></div>
      </div>
      <!-- /ko -->
    </div>
  </div>
`;

class LanguageReferenceTopic {
  constructor(entry, index) {
    this.ref = entry.ref;
    this.title = entry.title;
    this.index = index;
    this.weight = 1;
    this.children = [];
    entry.children.forEach(child => {
      this.children.push(new LanguageReferenceTopic(child, this.index));
    });
    this.loadDeferred = $.Deferred();
    this.loading = ko.observable(false);
    this.body = ko.observable();
    this.bodyMatch = ko.observable();
    this.open = ko.observable(false);
    this.titleMatch = ko.observable();
  }

  load() {
    if (this.body() || this.loading()) {
      return this.loadDeferred.promise();
    }
    this.loading(true);
    apiHelper
      .simpleGet(this.index[this.ref])
      .done(doc => {
        this.body(doc.body);
      })
      .always(() => {
        this.loading(false);
        this.loadDeferred.resolve(this);
      });
    return this.loadDeferred.promise();
  }
}

class AssistLangRefPanel {
  constructor(params, element) {
    this.disposals = [];
    this.availableTypes = ko.observableArray();
    this.sourceType = ko.observable();

    this.allTopics = {
      impala: [],
      hive: []
    };

    window.IMPALA_DOC_TOP_LEVEL.forEach(topLevelItem => {
      this.allTopics.impala.push(new LanguageReferenceTopic(topLevelItem, window.IMPALA_DOC_INDEX));
    });
    window.HIVE_DOC_TOP_LEVEL.forEach(topLevelItem => {
      this.allTopics.hive.push(new LanguageReferenceTopic(topLevelItem, window.HIVE_DOC_INDEX));
    });

    const updateType = type => {
      if (this.availableTypes().indexOf(type) !== -1) {
        this.sourceType(type);
      }
    };

    const activeSnippetTypeSub = huePubSub.subscribe('active.snippet.type.changed', details => {
      updateType(details.type);
    });

    const configSub = huePubSub.subscribe('cluster.config.set.config', clusterConfig => {
      const lastActiveType = this.sourceType();
      if (
        clusterConfig.app_config &&
        clusterConfig.app_config.editor &&
        clusterConfig.app_config.editor.interpreters
      ) {
        const typesIndex = {};
        clusterConfig.app_config.editor.interpreters.forEach(interpreter => {
          if (interpreter.type === 'hive' || interpreter.type === 'impala') {
            typesIndex[interpreter.type] = true;
          }
        });
        this.availableTypes(Object.keys(typesIndex).sort());

        if (lastActiveType && typesIndex[lastActiveType]) {
          this.sourceType(lastActiveType);
        } else {
          this.sourceType(this.availableTypes().length ? this.availableTypes()[0] : undefined);
        }
      } else {
        this.availableTypes([]);
      }
    });

    huePubSub.publish('cluster.config.get.config');

    this.disposals.push(() => {
      configSub.remove();
      activeSnippetTypeSub.remove();
    });

    huePubSub.publish('get.active.snippet.type', updateType);

    this.topics = ko.pureComputed(() => {
      return this.sourceType() ? this.allTopics[this.sourceType()] : [];
    });

    this.selectedTopic = ko.observable();

    const selectedSub = this.selectedTopic.subscribe(newTopic => {
      if (newTopic) {
        newTopic.load();
      }
    });
    this.disposals.push(() => {
      selectedSub.dispose();
    });

    this.query = ko.observable().extend({ throttle: 200 });
    this.filteredTopics = ko.observableArray();

    const sortFilteredTopics = () => {
      this.filteredTopics.sort((a, b) => {
        if (a.weight !== b.weight) {
          return b.weight - a.weight;
        }
        return a.title.localeCompare(b.title);
      });
    };

    this.query.subscribe(newVal => {
      if (!newVal) {
        return;
      }
      const lowerCaseQuery = this.query().toLowerCase();
      const replaceRegexp = new RegExp('(' + lowerCaseQuery + ')', 'i');
      this.filteredTopics([]);

      let sortTimeout = -1;

      const findInside = topic => {
        topic.load().done(loadedTopic => {
          let match = false;
          const titleIndex = loadedTopic.title.toLowerCase().indexOf(lowerCaseQuery);
          if (titleIndex !== -1) {
            loadedTopic.weight = titleIndex === 0 ? 2 : 1;
            loadedTopic.titleMatch(
              loadedTopic.title.replace(new RegExp('(' + lowerCaseQuery + ')', 'i'), '<b>$1</b>')
            );
            loadedTopic.bodyMatch(undefined);
            this.filteredTopics.push(loadedTopic);
            match = true;
          } else if (
            loadedTopic.body() &&
            loadedTopic
              .body()
              .toLowerCase()
              .indexOf(lowerCaseQuery) !== -1
          ) {
            loadedTopic.weight = 0;
            loadedTopic.titleMatch(undefined);
            loadedTopic.bodyMatch(loadedTopic.body().replace(replaceRegexp, '<b>$1</b>'));
            this.filteredTopics.push(loadedTopic);
            match = true;
          } else {
            loadedTopic.titleMatch(undefined);
            loadedTopic.bodyMatch(undefined);
          }
          if (match) {
            window.clearTimeout(sortTimeout);
            sortTimeout = window.setTimeout(sortFilteredTopics, 100);
          }
        });

        topic.children.forEach(findInside);
      };

      this.topics().forEach(findInside);

      window.setTimeout(() => {
        // Initial sort deferred for promises to complete
        sortFilteredTopics();
      }, 0);
    });

    const selectedTopicSub = this.selectedTopic.subscribe(() => {
      $(element)
        .find('.assist-docs-details')
        .scrollTop(0);
    });

    const querySub = this.query.subscribe(() => {
      $(element)
        .find('.assist-docs-topics')
        .scrollTop(0);
    });

    const scrollToSelectedTopic = function() {
      const topics = $(element).find('.assist-docs-topics');
      if (topics.find('.blue').length) {
        topics.scrollTop(
          Math.min(
            topics.scrollTop() + topics.find('.blue').position().top - 20,
            topics.find('> ul').height() - topics.height()
          )
        );
      }
    };

    const scrollToAnchor = function(anchorId) {
      if (!anchorId) {
        return;
      }
      const detailsPanel = $(element).find('.assist-docs-details');
      const found = detailsPanel.find('#' + anchorId.split('/').join(' #'));
      if (found.length) {
        detailsPanel.scrollTop(found.position().top - 10);
      }
    };

    huePubSub.subscribe('scroll.test', scrollToSelectedTopic);

    const showTopicSub = huePubSub.subscribe('assist.lang.ref.panel.show.topic', targetTopic => {
      const topicStack = [];
      const findTopic = topics => {
        topics.some(topic => {
          topicStack.push(topic);
          if (topic.ref === targetTopic.ref) {
            while (topicStack.length) {
              topicStack.pop().open(true);
            }
            this.query('');
            this.selectedTopic(topic);
            window.setTimeout(() => {
              scrollToAnchor(targetTopic.anchorId);
              scrollToSelectedTopic();
            }, 0);
            return true;
          } else if (topic.children.length) {
            const inChild = findTopic(topic.children);
            if (inChild) {
              return true;
            }
          }
          topicStack.pop();
        });
      };
      findTopic(this.topics());
    });

    $(element).on('click.langref', event => {
      if (event.target.className === 'hue-doc-internal-link') {
        huePubSub.publish('assist.lang.ref.panel.show.topic', {
          ref: $(event.target).data('doc-ref'),
          anchorId: $(event.target).data('doc-anchor-id')
        });
      }
    });

    this.disposals.push(() => {
      selectedTopicSub.dispose();
      querySub.dispose();
      showTopicSub.remove();
      $(element).off('click.langref');
    });
  }

  dispose() {
    while (this.disposals.length) {
      this.disposals.pop()();
    }
  }
}

componentUtils.registerStaticComponent(
  'assist-language-reference-panel',
  {
    createViewModel: (params, componentInfo) =>
      new AssistLangRefPanel(params, componentInfo.element)
  },
  TEMPLATE
);

export default AssistLangRefPanel;
