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

import HueColors from 'utils/hueColors';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import solrFormulaParser from 'parse/solrFormulaParser';
import sqlUtils from 'sql/sqlUtils';

const normalizedColors = HueColors.getNormalizedColors();

// TODO: Autocomplete colors should be global
const COLORS = {
  ALL: HueColors.BLUE,
  FIELD: normalizedColors['green'][2],
  FUNCTION: normalizedColors['purple-gray'][3],
  KEYWORD: normalizedColors['blue'][4],
  SAMPLE: normalizedColors['purple'][5]
};

const SOLR_FUNCTIONS = {
  abs: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'abs(x)',
    draggable: 'abs()',
    description: 'Returns the absolute value of the specified value or function.'
  },
  and: {
    returnTypes: ['boolean'],
    arguments: [[{ type: 'boolean', multiple: true }]],
    signature: 'and(x, y, ...)',
    draggable: 'and()',
    description: 'Returns a value of true if and only if all of its operands evaluate to true.'
  },
  childfield: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'childfield(x)',
    draggable: 'childfield()',
    description:
      'Returns the value of the given field for one of the matched child docs when searching by {!parent}. It can be used only in sort parameter.'
  },
  def: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'def(field, default)',
    draggable: 'def()',
    description:
      'def is short for default. Returns the value of field "field", or if the field does not exist, returns the default value specified. and yields the first value where exists()==true.)'
  },
  div: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'div(x, y)',
    draggable: 'div()',
    description: 'Divides one value or function by another. div(x,y) divides x by y.'
  },
  dist: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'dist(power, x, y, 0, 0)',
    draggable: 'dist()',
    description:
      'Return the distance between two vectors (points) in an n-dimensional space. Takes in the power, plus two or more ValueSource instances and calculates the distances between the two vectors. Each ValueSource must be a number. There must be an even number of ValueSource instances passed in and the method assumes that the first half represent the first vector and the second half represent the second vector.'
  },
  docfreq: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'docfreq(field, value)',
    draggable: 'docfreq()',
    description:
      "Returns the number of documents that contain the term in the field. This is a constant (the same value for all documents in the index).\n\n You can quote the term if it's more complex, or do parameter substitution for the term value."
  },
  exists: {
    returnTypes: ['boolean'],
    arguments: [[{ type: 'T' }]],
    signature: 'exists(x)',
    draggable: 'exists()',
    description: 'Returns TRUE if any member of the field exists.'
  },
  eq: {
    returnTypes: ['boolean'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'eq(x, y)',
    draggable: 'eq()',
    description: 'Equal, returns TRUE if x is equal to y'
  },
  field: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T', optional: true }]],
    signature: 'field(field, minOrMax)',
    draggable: 'field()',
    description:
      'Returns the numeric docValues or indexed value of the field with the specified name. In its simplest (single argument) form, this function can only be used on single valued fields, and can be called using the name of the field as a string, or for most conventional field names simply use the field name by itself with out using the field(...) syntax.\n\nWhen using docValues, an optional 2nd argument can be specified to select the "min" or "max" value of multivalued fields.\n\n0 is returned for documents without a value in the field.'
  },
  gt: {
    returnTypes: ['boolean'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'gt(x, y)',
    draggable: 'gt()',
    description: 'Greater than, returns TRUE if x is greater than y'
  },
  gte: {
    returnTypes: ['boolean'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'gte(x, y)',
    draggable: 'gte()',
    description: 'Greater than or equal, returns TRUE if x is greater than or equal to y'
  },
  hsin: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'hsin(2, true, x, y, 0, 0)',
    draggable: 'hsin()',
    description:
      'The Haversine distance calculates the distance between two points on a sphere when traveling along the sphere. The values must be in radians. hsin also take a Boolean argument to specify whether the function should convert its output to radians.'
  },
  idf: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'idf(field, str)',
    draggable: 'idf()',
    description:
      'Inverse document frequency; a measure of whether the term is common or rare across all documents. Obtained by dividing the total number of documents by the number of documents containing the term, and then taking the logarithm of that quotient. See also tf.'
  },
  if: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }, { type: 'T' }]],
    signature: 'if(test, val1, val2)',
    draggable: 'if()',
    description:
      'Enables conditional function queries. In if(test,value1,value2): \n- test is or refers to a logical value or expression that returns a logical value (TRUE or FALSE).\n- value1 is the value that is returned by the function if test yields TRUE.\n -value2 is the value that is returned by the function if test yields FALSE.\n\nAn expression can be any function which outputs boolean values, or even functions returning numeric values, in which case value 0 will be interpreted as false, or strings, in which case empty string is interpreted as false.'
  },
  linear: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }, { type: 'T' }]],
    signature: 'linear(x, m, c)',
    draggable: 'linear()',
    description:
      'Implements m*x+c where m and c are constants and x is an arbitrary function. This is equivalent to sum(product(m,x),c), but slightly more efficient as it is implemented as a single function.'
  },
  log: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'log(x)',
    draggable: 'log()',
    description: 'Returns the log base 10 of the specified function.'
  },
  lt: {
    returnTypes: ['boolean'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'lt(x, y)',
    draggable: 'lt()',
    description: 'Less than, returns TRUE if x is less than y'
  },
  lte: {
    returnTypes: ['boolean'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'lte(x, y)',
    draggable: 'lte()',
    description: 'Less than or equal, returns TRUE if x is less than or equal to y'
  },
  map: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'map(x, min, max, target)',
    draggable: 'map()',
    description:
      'Maps any values of an input function x that fall within min and max inclusive to the specified target. The arguments min and max must be constants. The arguments target and default can be constants or functions. If the value of x does not fall between min and max, then either the value of x is returned, or a default value is returned if specified as a 5th argument.'
  },
  max: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'max(x, y, ...)',
    draggable: 'max()',
    description:
      'Returns the maximum numeric value of multiple nested functions or constants, which are specified as arguments: max(x,y,...). The max function can also be useful for "bottoming out" another function or field at some specified constant.'
  },
  maxdoc: {
    returnTypes: ['T'],
    arguments: [],
    signature: 'maxdoc()',
    draggable: 'maxdoc()',
    description:
      'Returns the number of documents in the index, including those that are marked as deleted but have not yet been purged. This is a constant (the same value for all documents in the index).'
  },
  min: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'min(x, y, ...)',
    draggable: 'min()',
    description:
      'Returns the minimum numeric value of multiple nested functions of constants, which are specified as arguments: min(x,y,...). The min function can also be useful for providing an "upper bound" on a function using a constant.'
  },
  ms: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'ms(x, y, ...)',
    draggable: 'ms()',
    description:
      'Returns milliseconds of difference between its arguments. Dates are relative to the Unix or POSIX time epoch, midnight, January 1, 1970 UTC. Arguments may be the name of an indexed TrieDateField, or date math based on a constant date or NOW.\n\n- ms(): Equivalent to ms(NOW), number of milliseconds since the epoch.\n- ms(a): Returns the number of milliseconds since the epoch that the argument represents.\n- ms(a,b) : Returns the number of milliseconds that b occurs before a (that is, a - b)'
  },
  mul: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'mul(x, y, ...)',
    draggable: 'mul()',
    description:
      'Returns the product of multiple values or functions, which are specified in a comma-separated list. Same as the product function.'
  },
  norm: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'norm(field)',
    draggable: 'norm()',
    description:
      'Returns the "norm" stored in the index for the specified field. This is the product of the index time boost and the length normalization factor, according to the Similarity for the field.'
  },
  not: {
    returnTypes: ['boolean'],
    arguments: [[{ type: 'boolean' }]],
    signature: 'not(x)',
    draggable: 'not()',
    description: 'The logically negated value of the wrapped function.'
  },
  numdocs: {
    returnTypes: ['T'],
    arguments: [],
    signature: 'numdocs()',
    draggable: 'numdocs()',
    description:
      'Returns the number of documents in the index, not including those that are marked as deleted but have not yet been purged. This is a constant (the same value for all documents in the index).'
  },
  or: {
    returnTypes: ['boolean'],
    arguments: [[{ type: 'boolean', multiple: true }]],
    signature: 'or(x, y)',
    draggable: 'or()',
    description: 'A logical disjunction.'
  },
  ord: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'ord(field)',
    draggable: 'ord()',
    description:
      'Returns the ordinal of the indexed field value within the indexed list of terms for that field in Lucene index order (lexicographically ordered by unicode value), starting at 1. In other words, for a given field, all values are ordered lexicographically; this function then returns the offset of a particular value in that ordering. The field must have a maximum of one value per document (not multi-valued). 0 is returned for documents without a value in the field.'
  },
  payload: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'payload(payloaded_field_dpf, term, 0.0, first)',
    draggable: 'payload()',
    description:
      'Returns the float value computed from the decoded payloads of the term specified. The return value is computed using the min, max, or average of the decoded payloads. A special first function can be used instead of the others, to short-circuit term enumeration and return only the decoded payload of the first term. The field specified must have float or integer payload encoding capability (via DelimitedPayloadTokenFilter or NumericPayloadTokenFilter). If no payload is found for the term, the default value is returned.'
  },
  pow: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'pow(x, y)',
    draggable: 'pow()',
    description:
      'Raises the specified base to the specified power. pow(x,y) raises x to the power of y.'
  },
  product: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'product(x, y, ...)',
    draggable: 'product()',
    description:
      'Returns the product of multiple values or functions, which are specified in a comma-separated list. mul(...) may also be used as an alias for this function.'
  },
  query: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T', optional: true }]],
    signature: 'query(subquery, default)',
    draggable: 'query()',
    description:
      'Returns the score for the given subquery, or the default value for documents not matching the query. Any type of subquery is supported through either parameter de-referencing $otherparam or direct specification of the query string in the Local Parameters through the v key.'
  },
  recip: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }, { type: 'T' }, { type: 'T' }]],
    signature: 'recip(x, m, a, b)',
    draggable: 'recip()',
    description:
      'Performs a reciprocal function with recip(x,m,a,b) implementing a/(m*x+b) where m,a,b are constants, and x is any arbitrarily complex function.\n\nWhen a and b are equal, and x>=0, this function has a maximum value of 1 that drops as x increases. Increasing the value of a and b together results in a movement of the entire function to a flatter part of the curve. These properties can make this an ideal function for boosting more recent documents when x is rord(datefield).'
  },
  rord: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'rord(x)',
    draggable: 'rord()',
    description: 'Returns the reverse ordering of that returned by ord.'
  },
  scale: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }, { type: 'T' }]],
    signature: 'scale(x, minTarget, maxTarget)',
    draggable: 'scale()',
    description:
      'Scales values of the function x such that they fall between the specified minTarget and maxTarget inclusive. The current implementation traverses all of the function values to obtain the min and max, so it can pick the correct scale.\n\nThe current implementation cannot distinguish when documents have been deleted or documents that have no value. It uses 0.0 values for these cases. This means that if values are normally all greater than 0.0, one can still end up with 0.0 as the min value to map from. In these cases, an appropriate map() function could be used as a workaround to change 0.0 to a value in the real range, as shown here: scale(map(x,0,0,5),1,2).'
  },
  sqedist: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'sqedist(x_td, y_td, 0, 0)',
    draggable: 'sqedist()',
    description:
      'The Square Euclidean distance calculates the 2-norm (Euclidean distance) but does not take the square root, thus saving a fairly expensive operation. It is often the case that applications that care about Euclidean distance do not need the actual distance, but instead can use the square of the distance. There must be an even number of ValueSource instances passed in and the method assumes that the first half represent the first vector and the second half represent the second vector.'
  },
  sqrt: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sqrt(x)',
    draggable: 'sqrt()',
    description: 'Returns the square root of the specified value or function.'
  },
  strdist: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'strdist(string1, string2, distance_measure)',
    draggable: 'strdist()',
    description:
      "Calculate the distance between two strings. Uses the Lucene spell checker StringDistance interface and supports all of the implementations available in that package, plus allows applications to plug in their own via Solr's resource loading capabilities. strdist takes (string1, string2, distance measure).\n\nPossible values for distance measure are:\n- jw: Jaro-Winkler\n- edit: Levenstein or Edit distance\n- ngram: The NGramDistance, if specified, can optionally pass in the ngram size too. Default is 2.\n- FQN: Fully Qualified class Name for an implementation of the StringDistance interface. Must have a no-arg constructor."
  },
  sub: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'sub(x, y)',
    draggable: 'sub()',
    description: 'Returns x-y from sub(x,y).'
  },
  sum: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'sum(x, y, ...)',
    draggable: 'sum()',
    description:
      'Returns the sum of multiple values or functions, which are specified in a comma-separated list. add(...) may be used as an alias for this function'
  },
  sumtotaltermfreq: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sumtotaltermfreq(field)',
    draggable: 'sumtotaltermfreq()',
    description:
      'Returns the sum of totaltermfreq values for all terms in the field in the entire index (i.e., the number of indexed tokens for that field). (Aliases sumtotaltermfreq to sttf.)'
  },
  termfreq: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'termfreq(field, term)',
    draggable: 'termfreq()',
    description: 'Returns the number of times the term appears in the field for that document.'
  },
  tf: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'tf(field, term)',
    draggable: 'tf()',
    description:
      'Term frequency; returns the term frequency factor for the given term, using the Similarity for the field. The tf-idf value increases proportionally to the number of times a word appears in the document, but is offset by the frequency of the word in the document, which helps to control for the fact that some words are generally more common than others. See also idf.'
  },
  top: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'top(x)',
    draggable: 'top()',
    description:
      'Causes the function query argument to derive its values from the top-level IndexReader containing all parts of an index. For example, the ordinal of a value in a single segment will be different from the ordinal of that same value in the complete index.'
  },
  totaltermfreq: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }, { type: 'T' }]],
    signature: 'totaltermfreq(field, term)',
    draggable: 'totaltermfreq()',
    description:
      'Returns the number of times the term appears in the field in the entire index. (Aliases totaltermfreq to ttf.)'
  },
  xor: {
    returnTypes: ['boolean'],
    arguments: [[{ type: 'boolean', multiple: true }]],
    signature: 'xor(x, y)',
    draggable: 'xor()',
    description: 'Logical exclusive disjunction, or one or the other but not both.'
  }
};

const SOLR_AGGREGATE_FUNCTIONS = {
  avg: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'avg(x)',
    draggable: 'avg()',
    description: 'Average of numeric values.'
  },
  hll: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'hll(x)',
    draggable: 'hll()',
    description: 'The number of unique values using the HyperLogLog algorithm.'
  },
  max: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'max(x)',
    draggable: 'max()',
    description: 'The maximum value.'
  },
  min: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'min(x)',
    draggable: 'min()',
    description: 'The minimum value.'
  },
  percentile: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T', multiple: true }]],
    signature: 'percentile(x, y, z, ...)',
    draggable: 'percentile()',
    description: 'Calculates the percentiles.'
  },
  stddev: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'stddev(x)',
    draggable: 'stddev()',
    description: 'Calculates standard deviation (Solr 6.6+).'
  },
  sum: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sum(x)',
    draggable: 'sum()',
    description: 'The sum of numeric values.'
  },
  sumsq: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'sumsq(x)',
    draggable: 'sumsq()',
    description: 'The sum of squares.'
  },
  unique: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'unique(x)',
    draggable: 'unique()',
    description: 'The number of unique values (count distinct).'
  },
  variance: {
    returnTypes: ['T'],
    arguments: [[{ type: 'T' }]],
    signature: 'variance(x)',
    draggable: 'variance()',
    description: 'Calculates variance (Solr 6.6+).'
  }
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
  FUNCTION: {
    id: 'function',
    weight: 900,
    color: COLORS.FUNCTION,
    label: I18n('Functions'),
    detailsTemplate: 'udf'
  }
};

class SolrFormulaSuggestions {
  constructor(fieldAccessor) {
    const self = this;
    self.entries = ko.observableArray();
    self.fieldAccessor = fieldAccessor;

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
    const syncEntries = [];

    if (parseResult.suggestFields) {
      self.fieldAccessor().forEach(field => {
        let type = field.type();
        if (type.indexOf('<') !== -1) {
          type = type.substring(0, type.indexOf('<'));
        }
        syncEntries.push({
          category: CATEGORIES.FIELD,
          value: field.name(),
          meta: type,
          weightAdjust: 0,
          popular: ko.observable(false),
          details: field
        });
      });
    }

    if (parseResult.suggestFunctions) {
      Object.keys(SOLR_FUNCTIONS).forEach(name => {
        syncEntries.push({
          category: CATEGORIES.FUNCTION,
          value: name + '()',
          meta: SOLR_FUNCTIONS[name].returnTypes.join('|'),
          weightAdjust: 0, // Add when we type aware
          popular: ko.observable(false),
          details: SOLR_FUNCTIONS[name]
        });
      });
    }

    if (parseResult.suggestAggregateFunctions) {
      Object.keys(SOLR_AGGREGATE_FUNCTIONS).forEach(name => {
        syncEntries.push({
          category: CATEGORIES.FUNCTION,
          value: name + '()',
          meta: SOLR_AGGREGATE_FUNCTIONS[name].returnTypes.join('|'),
          weightAdjust: 0, // Add when we type aware
          popular: ko.observable(false),
          details: SOLR_AGGREGATE_FUNCTIONS[name]
        });
      });
    }

    self.entries(syncEntries);
  }
}

class SolrFormulaAutocompleter {
  /**
   * @param {Object} options
   * @param {Ace} options.editor
   * @param {Object} options.support
   * @param {function} options.support.fields - The observable/function containing the fields
   * @constructor
   */
  constructor(options) {
    const self = this;
    self.editor = options.editor();
    self.suggestions = new SolrFormulaSuggestions(options.support.fields);
  }

  autocomplete() {
    const self = this;
    const parseResult = solrFormulaParser.autocompleteSolrFormula(
      self.editor.getTextBeforeCursor(),
      self.editor.getTextAfterCursor()
    );
    self.suggestions.update(parseResult);
  }

  parse(value) {
    return solrFormulaParser.parseSolrFormula(value);
  }
}

export default SolrFormulaAutocompleter;
