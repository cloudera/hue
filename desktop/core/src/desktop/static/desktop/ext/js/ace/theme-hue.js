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

ace.define("ace/theme/hue",["require","exports","module","ace/lib/dom"], function(require, exports, module) {

exports.isDark = false;
exports.cssClass = "ace-hue";
exports.cssText = ".ace-hue .ace_gutter {\
background: #f6f6f6;\
color: #4D4D4C\
}\
.ace-hue .ace_print-margin {\
width: 1px;\
background: #f6f6f6\
}\
.ace-hue {\
background-color: #FFFFFF;\
color: #4D4D4C\
}\
.ace-hue .ace_cursor {\
color: #AEAFAD\
}\
.ace-hue .ace_marker-layer .ace_selection {\
background: #D6D6D6\
}\
.ace-tomorrow.ace_multiselect .ace_selection.ace_start {\
box-shadow: 0 0 3px 0px #FFFFFF;\
border-radius: 2px\
}\
.ace-hue .ace_marker-layer .ace_step {\
background: rgb(255, 255, 0)\
}\
.ace-hue .ace_marker-layer .ace_bracket {\
margin: -1px 0 0 -1px;\
border: 1px solid #D1D1D1\
}\
.ace-hue .ace_marker-layer .ace_active-line {\
background: #EFEFEF\
}\
.ace-hue .ace_marker-layer .ace_error-line {\
background: #F2DEDE\
}\
.ace-hue .ace_gutter-active-line {\
background-color : #dcdcdc\
}\
.ace-hue .ace_marker-layer .ace_selected-word {\
border: 1px solid #D6D6D6\
}\
.ace-hue .ace_invisible {\
color: #D1D1D1\
}\
.ace-hue .ace_keyword,\
.ace-hue .ace_meta,\
.ace-hue .ace_storage,\
.ace-hue .ace_storage.ace_type,\
.ace-hue .ace_support.ace_type {\
color: #8959A8\
}\
.ace-hue .ace_keyword.ace_operator {\
color: #3E999F\
}\
.ace-hue .ace_constant.ace_character,\
.ace-hue .ace_constant.ace_language,\
.ace-hue .ace_constant.ace_numeric,\
.ace-hue .ace_keyword.ace_other.ace_unit,\
.ace-hue .ace_support.ace_constant,\
.ace-hue .ace_variable.ace_parameter {\
color: #F5871F\
}\
.ace-hue .ace_constant.ace_other {\
color: #666969\
}\
.ace-hue .ace_invalid {\
color: #FFFFFF;\
background-color: #C82829\
}\
.ace-hue .ace_invalid.ace_deprecated {\
color: #FFFFFF;\
background-color: #8959A8\
}\
.ace-hue .ace_fold {\
background-color: #4271AE;\
border-color: #4D4D4C\
}\
.ace-hue .ace_entity.ace_name.ace_function,\
.ace-hue .ace_support.ace_function,\
.ace-hue .ace_variable {\
color: #4271AE\
}\
.ace-hue .ace_support.ace_class,\
.ace-hue .ace_support.ace_type {\
color: #C99E00\
}\
.ace-hue .ace_heading,\
.ace-hue .ace_markup.ace_heading,\
.ace-hue .ace_string {\
color: #718C00\
}\
.ace-hue .ace_entity.ace_name.ace_tag,\
.ace-hue .ace_entity.ace_other.ace_attribute-name,\
.ace-hue .ace_meta.ace_tag,\
.ace-hue .ace_string.ace_regexp,\
.ace-hue .ace_variable {\
color: #C82829\
}\
.ace-hue .ace_comment {\
color: #8E908C\
}\
.ace-hue .ace_indent-guide {\
background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAAE0lEQVQImWP4////f4bdu3f/BwAlfgctduB85QAAAABJRU5ErkJggg==) right repeat-y\
}\
.ace-spinner, .ace-inline-button {\
  position: absolute;\
  z-index: 1030;\
}\
.ace-inline-button {\
  opacity: 0.7;\
}\
.ace-inline-button:hover {\
  opacity: 1;\
}";

var dom = require("../lib/dom");
dom.importCssString(exports.cssText, exports.cssClass);
});
