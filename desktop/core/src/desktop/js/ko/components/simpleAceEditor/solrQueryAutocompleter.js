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

import apiHelper from 'api/apiHelper';
import HueColors from 'utils/hueColors';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import solrQueryParser from 'parse/solrQueryParser';
import sqlUtils from 'sql/sqlUtils';

const DEFAULT_POPULAR = ko.observable(false);
const KEYWORD_I18n = I18n('keyword');
const SAMPLE_I18n = I18n('sample');
const SAMPLE_LIMIT = 100;

const normalizedColors = HueColors.getNormalizedColors();

// TODO: Autocomplete colors should be global
const COLORS = {
  ALL: HueColors.BLUE,
  FIELD: normalizedColors['green'][2],
  FUNCTION: normalizedColors['purple-gray'][3],
  KEYWORD: normalizedColors['blue'][4],
  SAMPLE: normalizedColors['purple'][5]
};

const CATEGORIES = {
  ALL: { id: 'all', color: COLORS.ALL, label: I18n('All') },
  FIELD: {
    id: 'field',
    weight: 1000,
    color: COLORS.FIELD,
    label: I18n('Fields'),
    detailsTemplate: 'solr-field'
  },
  KEYWORD: {
    id: 'keyword',
    weight: 0,
    color: COLORS.KEYWORD,
    label: I18n('Keywords'),
    detailsTemplate: 'keyword'
  },
  SAMPLE: {
    id: 'sample',
    weight: 900,
    color: COLORS.SAMPLE,
    label: I18n('Samples'),
    detailsTemplate: 'value'
  }
};

class SolrQuerySuggestions {
  constructor(collection, editor) {
    const self = this;
    self.entries = ko.observableArray();
    self.editor = editor;
    self.collection = collection;

    self.lastNonSampleSuggestions = [];
    self.parseResult = {};

    self.filtered = ko.pureComputed(() => {
      let result = self.entries();

      if (self.filter()) {
        result = sqlUtils.autocompleteFilter(self.filter(), result);
        huePubSub.publish('hue.ace.autocompleter.match.updated');
      }

      sqlUtils.sortSuggestions(result, self.filter(), self.sortOverride);

      return result;
    });

    self.availableCategories = ko.pureComputed(() => {
      // TODO: Implement autocomplete logic
      return [CATEGORIES.ALL];
    });

    self.loading = ko.observable(false);
    self.filter = ko.observable();
    self.cancelRequests = function() {};
  }

  update(parseResult) {
    const self = this;
    self.lastNonSampleSuggestions = [];
    self.parseResult = parseResult;

    if (self.parseResult.suggestFields) {
      self.collection.template.fieldsAttributes().forEach(field => {
        self.lastNonSampleSuggestions.push({
          category: CATEGORIES.FIELD,
          value: field.name() + (parseResult.suggestFields.appendColon ? ':' : ''),
          meta: field.type(),
          weightAdjust: 0,
          popular: DEFAULT_POPULAR,
          details: field
        });
      });
    }

    if (self.parseResult.suggestKeywords) {
      parseResult.suggestKeywords.forEach(keyword => {
        self.lastNonSampleSuggestions.push({
          category: CATEGORIES.KEYWORD,
          value: keyword,
          meta: KEYWORD_I18n,
          weightAdjust: 0,
          popular: DEFAULT_POPULAR,
          details: null
        });
      });
    }

    self.entries(self.lastNonSampleSuggestions);

    if (self.parseResult.suggestValues) {
      const aceUtil = ace.require('ace/autocomplete/util');
      const pos = self.editor.getCursorPosition();
      let partial = aceUtil.retrievePrecedingIdentifier(
        self.editor.session.getLine(pos.row),
        pos.column
      );
      if (self.parseResult.suggestValues.partial) {
        partial = self.parseResult.suggestValues.partial + partial;
      }

      const valuesPromise = self.handleSampleSuggestions(partial);
      self.loading(true);
      valuesPromise.done(suggestions => {
        if (suggestions.length) {
          self.entries(self.lastNonSampleSuggestions.concat(suggestions));
        }
        self.loading(false);
      });
    }
  }

  handleSampleSuggestions(prefix) {
    const self = this;
    const promise = $.Deferred();
    const fieldName = self.parseResult.suggestValues.field;
    const hasField = self.collection.template.fieldsAttributes().some(field => {
      return field.name() === fieldName;
    });
    if (hasField) {
      apiHelper.fetchDashboardTerms({
        collectionName: self.collection.name(),
        fieldName: fieldName,
        prefix: prefix || '',
        silenceErrors: true,
        successCallback: function(result) {
          const sampleSuggestions = [];
          if (result && result.terms && result.terms.length) {
            let maxCount = 1;
            for (let i = 0; i < Math.min(SAMPLE_LIMIT, result.terms.length); i++) {
              const sampleValue = result.terms[i].value;
              const shouldQuote =
                !self.parseResult.suggestValues.quotePresent &&
                /[\s\u3000!():"'^+\-\[\]{}~*?/]/.test(sampleValue);
              if (maxCount < result.terms[i].count) {
                maxCount = result.terms[i].count;
              }
              let value = '';
              if (
                self.parseResult.suggestValues.partial &&
                !shouldQuote &&
                sampleValue
                  .toLowerCase()
                  .indexOf(self.parseResult.suggestValues.partial.toLowerCase()) === 0
              ) {
                value = sampleValue.substring(self.parseResult.suggestValues.partial.length);
              } else {
                value = shouldQuote ? '"' + sampleValue + '"' : sampleValue;
              }
              sampleSuggestions.push({
                value: value,
                meta: SAMPLE_I18n,
                category: CATEGORIES.SAMPLE,
                popular: DEFAULT_POPULAR,
                details: result.terms[i]
              });
            }
            sampleSuggestions.forEach(sampleSuggestion => {
              sampleSuggestion.weightAdjust = sampleSuggestion.details.count / maxCount;
            });
          }
          promise.resolve(sampleSuggestions);
        },
        errorCallback: function() {
          promise.resolve([]);
        }
      });
    } else {
      promise.resolve([]);
    }

    return promise;
  }

  onPartial(partial) {
    const self = this;
    if (self.parseResult.suggestValues) {
      const promise = self.handleSampleSuggestions(partial);
      promise.done(suggestions => {
        if (suggestions.length) {
          self.entries(self.lastNonSampleSuggestions.concat(suggestions));
        } else {
          self.entries(self.lastNonSampleSuggestions);
        }
      });
    }
  }
}

class SolrQueryAutocompleter {
  /**
   * @param {Object} options
   * @param {Ace} options.editor
   * @param {Object} options.support
   * @param {function} options.support.fields - The observable/function containing the fields
   * @param {function} options.support.collection - The observable/function containing the active collection
   * @constructor
   */
  constructor(options) {
    const self = this;
    self.editor = options.editor();
    self.suggestions = new SolrQuerySuggestions(options.support.collection, self.editor);
  }

  autocomplete() {
    const self = this;
    const parseResult = solrQueryParser.autocompleteSolrQuery(
      self.editor.getTextBeforeCursor(),
      self.editor.getTextAfterCursor()
    );
    self.suggestions.update(parseResult);
  }

  onPartial(partial) {
    const self = this;
    self.suggestions.onPartial(partial);
  }
}

export default SolrQueryAutocompleter;
