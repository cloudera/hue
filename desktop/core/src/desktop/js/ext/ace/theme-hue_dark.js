ace.define("ace/theme/hue_dark",["require","exports","module","ace/lib/dom"], function(require, exports, module) {

  exports.isDark = true;
  exports.cssClass = "ace-hue-dark";
  exports.cssText = "\
.ace-hue-dark .ace_hidden-cursors .ace_cursor {\
opacity: 0;\
}\
.ace-hue-dark .ace_print-margin {\
width: 1px;\
background: #232323;\
}\
.ace-hue-dark {\
background-color: #141414;\
color: #E7E7E7;\
}\
.ace-hue-dark .ace_cursor {\
color: #A7A7A7;\
}\
.ace-hue-dark .ace_marker-layer .ace_selection {\
background: rgba(221, 240, 255, 0.20);\
}\
.ace-hue-dark.ace_multiselect .ace_selection.ace_start {\
box-shadow: 0 0 3px 0 #141414;\
}\
.ace-hue-dark .ace_marker-layer .ace_step {\
background: rgb(102, 82, 0);\
}\
.ace-hue-dark .ace_marker-layer .ace_bracket {\
margin: -1px 0 0 -1px;\
border: 1px solid rgba(255, 255, 255, 0.25);\
}\
.ace-hue-dark .ace_marker-layer .ace_selected-word {\
border: 1px solid rgba(221, 240, 255, 0.20);\
}\
.ace-hue-dark .ace_marker-layer .ace_error-line {\
position: absolute;\
background-color: #FFB2B2;\
width: 100% !important;\
margin-left: -3px;\
border-radius: 0 !important;\
}\
.ace-hue-dark .ace_marker-layer .ace_warning-line {\
position: absolute;\
background-color: #fcf8e3;\
width: 100% !important;\
margin-left: -3px;\
border-radius: 0 !important;\
}\
.ace-hue-dark .ace_invisible {\
color: rgba(255, 255, 255, 0.25);\
}\
.ace-hue-dark .ace_keyword,\
.ace-hue-dark .ace_meta,\
.ace-hue-dark .ace_storage,\
.ace-hue-dark .ace_storage.ace_type,\
.ace-hue-dark .ace_support.ace_type {\
color: #B294BB;\
}\
.ace-hue .ace_keyword.ace_operator {\
color: #8ABEB7;\
}\
.ace-hue-dark .ace_gutter {\
background: #232323;\
color: #E2E2E2;\
}\
.ace-hue-dark .ace_gutter > .ace_layer {\
border-left: 1px solid #DBE8F1;\
color: #737373;\
}\
.ace-hue-dark .ace_gutter-cell.ace_error {\
background-color: #916062;\
border-left:1px solid #916062;\
background-image: none !important;\
}\
.ace-hue-dark .ace_gutter-cell.ace_warning {\
background-color: #fcf8e3;\
border-left:1px solid #f0c36d;\
background-image: none !important;\
}\
.ace-hue-dark .ace_gutter-cell {\
padding-left: 0 !important;\
padding-right: 3px !important;\
}\
.ace-hue-dark .ace_constant.ace_character,\
.ace-hue-dark .ace_constant.ace_language,\
.ace-hue-dark .ace_constant.ace_numeric,\
.ace-hue-dark .ace_keyword.ace_other.ace_unit,\
.ace-hue-dark .ace_support.ace_constant,\
.ace-hue-dark .ace_variable.ace_parameter  {\
color: #7ECAEB;\
}\
.ace-hue-dark .ace_constant.ace_other {\
color: #666969;\
}\
.ace-hue-dark .ace_invalid {\
color: #E7E7E7;\
background-color: rgba(86, 45, 86, 0.75);\
}\
.ace-hue-dark .ace_invalid.ace_deprecated {\
color: #E7E7E7;\
background-color: rgba(86, 45, 86, 0.75);\
}\
.ace-hue-dark .ace_fold {\
background-color: #AC885B;\
border-color: #E7E7E7;\
}\
.ace-hue-dark .ace_entity.ace_name.ace_function,\
.ace-hue-dark .ace_support.ace_function,\
.ace-hue-dark .ace_variable {\
color: #81A2BE;\
}\
.ace-hue-dark .ace_support.ace_class,\
.ace-hue-dark .ace_support.ace_type {\
color: #9B859D;\
}\
.ace-hue-dark .ace_heading,\
.ace-hue-dark .ace_markup.ace_heading,\
.ace-hue-dark .ace_string {\
color: #8F9D6A;\
}\
.ace-hue-dark .ace_entity.ace_name.ace_tag,\
.ace-hue-dark .ace_entity.ace_other.ace_attribute-name,\
.ace-hue-dark .ace_meta.ace_tag,\
.ace-hue-dark .ace_string.ace_regexp,\
.ace-hue-dark .ace_variable {\
color: #AC885B;\
}\
.ace-hue-dark .ace_comment {\
color: #5F5A60;\
}\
.ace-hue-dark .ace_indent-guide {\
background: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAAEklEQVQImWMQERFpYLC1tf0PAAgOAnPnhxyiAAAAAElFTkSuQmCC) right repeat-y;\
}\
.ace-hue-dark .ace-spinner, .ace-inline-button {\
position: absolute;\
z-index: 1030;\
}\
.ace-hue-dark .ace-inline-button {\
opacity: 0.7;\
}\
.ace-hue-dark .ace-inline-button:hover {\
opacity: 1;\
}\
.ace-hue-dark .ace_tooltip {\
background: #DCDCDC !important;\
border: none !important;\
color: #333;\
padding: 3px !important;\
}\
.ace-hue-dark .ace_tooltip hr {\
margin: 3px !important;\
}\
.ace-hue-dark .ace_editor.ace_autocomplete .ace_marker-layer .ace_active-line,\
.ace-hue-dark .ace_editor.ace_autocomplete .ace_marker-layer .ace_line-hover {\
background-color: #DBE8F1;\
z-index: 1;\
}";

  var dom = require("../lib/dom");
  dom.importCssString(exports.cssText, exports.cssClass);
});
