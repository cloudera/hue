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

define(function(require, exports, module) {
"use strict";

var oop = require("../lib/oop");
var TextMode = require("./text").Mode;
var SolrHighlightRules = require("./solr_highlight_rules").SolrHighlightRules;

var Mode = function() {
    this.HighlightRules = SolrHighlightRules;
};
oop.inherits(Mode, TextMode);

(function() {
    this.$id = "ace/mode/solr";

    this.getCompletions = function(state, session, pos, prefix) {
        var keywords = this.$keywordList || this.$createKeywordList();
        return keywords.map(function (word) {
            return {
                ignoreCase: false,
                name: word,
                value: word,
                upperCaseValue: word.toUpperCase(),
                score: 1,
                meta: "keyword"
            };
        });
    };
}).call(Mode.prototype);

exports.Mode = Mode;
});