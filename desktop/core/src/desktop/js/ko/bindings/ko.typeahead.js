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

ko.bindingHandlers.typeahead = {
  init: function(element, valueAccessor) {
    const elem = $(element);
    const options = valueAccessor();

    let source = options.nonBindableSource
      ? options.nonBindableSource
      : function() {
          let _source = ko.utils.unwrapObservable(valueAccessor.source);
          if (options.extraKeywords) {
            _source = _source.concat(options.extraKeywords.split(' '));
          }

          if (options.sourceSuffix && _source) {
            const _tmp = [];
            _source.forEach(item => {
              _tmp.push(item + options.sourceSuffix);
            });
            _source = _tmp;
          }
          return _source;
        };

    if (options.nonBindableSource && options.displayProperty) {
      source = ko.utils.arrayMap(options.nonBindableSource(), item => {
        return item[options.displayProperty]();
      });
    }

    const _options = {
      source: source,
      onselect: function(val) {
        if (typeof options.target == 'function') {
          options.target(val);
        } else {
          options.target = val;
        }
      }
    };

    function extractor(query, extractorSeparator) {
      let result = /([^ ]+)$/.exec(query);
      if (extractorSeparator) {
        result = new RegExp('([^\\' + extractorSeparator + ']+)$').exec(query);
      }
      if (result && result[1]) {
        return result[1].trim();
      }
      return '';
    }

    if (options.multipleValues) {
      let _extractorFound = null;

      const updateExtractors = () => {
        const _val = elem.val();
        _extractorFound = null;
        const _extractors =
          typeof options.multipleValuesExtractors == 'undefined' ||
          options.multipleValuesExtractors == null
            ? [' ']
            : options.multipleValuesExtractors;
        let _extractorFoundLastIndex = -1;
        _extractors.forEach(extractor => {
          if (_val.indexOf(extractor) > -1) {
            if (_val.indexOf(extractor) >= _extractorFoundLastIndex) {
              _extractorFound = extractor;
              _extractorFoundLastIndex = _val.indexOf(extractor);
            }
          }
        });
      };

      _options.updater = function(item) {
        const _val = this.$element.val();
        let _separator =
          typeof options.multipleValuesSeparator == 'undefined' ||
          options.multipleValuesSeparator == null
            ? ':'
            : options.multipleValuesSeparator;
        if (options.extraKeywords && options.extraKeywords.split(' ').indexOf(item) > -1) {
          _separator = '';
        }
        let isSpecialResult = false;
        if (item.indexOf('<i ') > -1) {
          _separator = '';
          isSpecialResult = true;
        }
        updateExtractors();
        if (_extractorFound != null) {
          return (
            (isSpecialResult ? '"' : '') +
            _val.substring(0, _val.lastIndexOf(_extractorFound)) +
            _extractorFound +
            $.trim(item.replace(/<[^>]*>/gi, '')) +
            (isSpecialResult ? '"' : '') +
            _separator
          );
        } else {
          return (
            (isSpecialResult ? '"' : '') +
            $.trim(item.replace(/<[^>]*>/gi, '')) +
            (isSpecialResult ? '"' : '') +
            _separator
          );
        }
      };

      _options.matcher = function(item) {
        updateExtractors();
        const _tquery = extractor(this.query, _extractorFound);
        if (!_tquery) {
          return false;
        }
        return ~item.toLowerCase().indexOf(_tquery.toLowerCase());
      };

      _options.highlighter = function(item) {
        updateExtractors();
        const _query = extractor(this.query, _extractorFound).replace(
          /[\-\[\]{}()*+?.:\\\^$|#\s]/g,
          '\\$&'
        );
        let _result = $.trim(item.replace(/<[^>]*>/gi, '')).replace(
          new RegExp('(' + _query + ')', 'ig'),
          ($1, match) => {
            return '<strong>' + match + '</strong>';
          }
        );
        if (item.indexOf('<i ') > -1) {
          _result += ' ' + item.substr(item.indexOf('<i '));
        }
        return _result;
      };
    }

    if (options.completeSolrRanges) {
      elem.on('keyup', e => {
        if (
          e.keyCode !== 8 &&
          e.which !== 8 &&
          elem.val() &&
          (elem.val().slice(-1) === '[' || elem.val().slice(-1) === '{')
        ) {
          const _index = elem.val().length;
          elem.val(elem.val() + ' TO ' + (elem.val().slice(-1) === '[' ? ']' : '}'));

          if (element.createTextRange) {
            const range = element.createTextRange();
            range.move('character', _index);
            range.select();
          } else if (element.selectionStart != null) {
            element.focus();
            element.setSelectionRange(_index, _index);
          }
        }
      });
    }

    if (options.triggerOnFocus) {
      _options.minLength = 0;
    }

    element.typeahead = elem.typeahead(_options);

    if (options.triggerOnFocus) {
      elem.on('focus', () => {
        elem.trigger('keyup');
      });
    }

    elem.blur(() => {
      if (typeof options.target == 'function') {
        options.target(elem.val());
      } else {
        options.target = elem.val();
      }
    });
  },
  update: function(element, valueAccessor) {
    const elem = $(element);
    const options = valueAccessor();
    if (typeof options.completeSolrRanges === 'undefined') {
      if (typeof options.target == 'function') {
        elem.val(options.target());
      } else {
        elem.val(options.target);
      }
    }
    if (options.forceUpdateSource) {
      element.typeahead.data('typeahead').source = function() {
        let _source = ko.utils.unwrapObservable(options.source);
        if (options.extraKeywords) {
          _source = _source.concat(options.extraKeywords.split(' '));
        }

        if (options.sourceSuffix && _source) {
          const _tmp = [];
          _source.forEach(item => {
            _tmp.push(item + options.sourceSuffix);
          });
          _source = _tmp;
        }
        return _source;
      };
    }
  }
};
