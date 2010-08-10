
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

/*
---
description: Deprecated JFrame filters here for backwards compatibility.
provides: [
 CCS.JFrame.DeprecatedFilters,
 CCS.JFrame.ContextMenu,
 CCS.JFrame.ArtButtons,
 CCS.JFrame.FilterInput,
 CCS.JFrame.FitText,
 CCS.JFrame.FormValidator,
 CCS.JFrame.HtmlTable,
 CCS.JFrame.Input,
 CCS.JFrame.OverText,
 CCS.JFrame.SelectWithOther,
 CCS.JFrame.SizeTo,
 CCS.JFrame.SplitView,
 CCS.JFrame.SubmitOnChange,
 CCS.JFrame.Tabs,
 CCS.JFrame.Tips
]
requires: [/CCS.JFrame, Widgets/Element.Data]
script: CCS.JFrame.ArtButtons.js

...
*/

(function(){

	var artInputsRegEx = /ccs-search|ccs-input/;

	CCS.JFrame.addGlobalFilters({

		artButtons: function(container) {
			if (container.get('html').contains('ccs-button_bar')) {
				container.getElements('.ccs-button_bar, .ccs-button_subbar_above, .ccs-button_subbar_below').each(function(element) {
					var above = element.hasClass('ccs-button_subbar_above');
					var below = element.hasClass('ccs-button_subbar_below');
					dbug.warn('you are using a deprecated JFrame filter (ccs-button_bar) on %o, use the ArtButtonBar data-filter instead.', element);
					element.addDataFilter('ArtButtonBar');
					if (above) element.set('data', 'bar-position', 'above');
					if (below) element.set('data', 'bar-position', 'below');
				});
			}

			if (container.get('html').contains('ccs-art_button')) {
				container.getElements('a.ccs-art_button, button.ccs-art_button, input.ccs-art_button').each(function(element){
					dbug.warn('you are using a deprecated JFrame filter (ccs-art_button) on %o, use the ArtButton data-filter instead.', element);
					element.addDataFilter('ArtButton');
				});
			}
		},

		contextMenu: function(container){
			if (!container.get('html').contains('data-context-menu-actions')) return;
			container.getElements('[data-context-menu-actions]').each(function(element) {
				if(!element.hasDataFilter('ContextMenu')) {
					dbug.warn('you are using a deprecated JFrame filter (data-context-menu-actions) on %o, use the ContextMenu data-filter instead.', element);
					element.addDataFilter('ContextMenu');
				}
			});
		},

		filterInput: function(container){
			if (!container.get('html').contains('data-filter-elements')) return;
			container.getElements('[data-filter-elements]').each(function(element){
				if (!element.hasDataFilter('FilterInput')) {
					dbug.warn("you are using a deprecated JFrame filter for filtering the input %o; add FilterInput to the data-filters property.", element);
					element.addDataFilter('FilterInput');
				}
			});
		},

		truncate: function(container) {
			if (!container.get('html').contains('ccs-truncate')) return;
			container.getElements('.ccs-truncate').each(function(element){
				dbug.warn('you are using a deprecated JFrame filter (truncate) on %o, use the FitText data-filter instead.', element);
				element.addDataFilter('FitText');
			});
		},

		truncateChildren: function(container){
			if (!container.get('html').contains('data-fit-text')) return;
			container.getElements('[data-fit-text]').each(function(element){
				if (!element.hasDataFilter('FitText-Children')) {
					dbug.warn('you are using a deprecated JFrame filter (data-fit-text) on %o without the data-filter "FitText-Children".', element);
					element.addDataFilter('FitText-Children');
				}
			});
		},

		form_validator: function(container) {
			if (!container.get('html').contains('form-validator')) return;
			container.getElements('form.form-validator').each(function(element) {
				dbug.warn('you are using a deprecated JFrame filter (form-validator) on %o, use the FormValidator data-filter instead.', element);
				element.addDataFilter('FormValidator');
			});
		},

		htmlTable: function(container){
			container.getElements('table.ccs-data_table').each(function(element){
				dbug.warn('You are using a deprecated JFrameFilter (ccs-data_table) on %o, use the DataTable data-filter instead.', element);
				element.addDataFilter('HtmlTable');	
			});
		},


		artInputs: function(container) {
			if (!container.get('html').match(artInputsRegEx)) return;
			container.getElements('.ccs-search, .ccs-input').each(function(element){
				dbug.warn('you are using a deprecated JFrame filter (ccs-search or ccs-input) on %o, use the ArtInput data-filter instead.', element);
				element.addDataFilter('ArtInput');
				if (element.hasClass('ccs-search')) element.set('data', 'art-input-type', 'search');
			}, this);
		},

		overText: function(container){
			container.getElements('input.overtext, textarea.overtext').map(function(element){
				dbug.warn('you are using a deprecated JFrame filter (overtext) on %o, use the OverText data-filter instead.', element);
				element.addDataFilter('OverText');
			});
		},

		sizeTo: function(container) {
			container.getElements('[data-size-to-width], [data-size-to-height]').each(function(element) {
				if(!element.hasDataFilter('SizeTo')){
					dbug.warn('you are using a deprecated JFrame filter (data-size-to) on %o, use the SizeTo data-filter instead.', element);
					element.addDataFilter('SizeTo');
				}
			}, this);
		},

		splitView: function(container) {
			if (!container.get('html').contains('splitview')) return;
			container.getElements('div.splitview').map(function(element){
				dbug.warn('you are using a deprecated JFrame filter (splitview) on %o, use the SplitView data-filter instead.', element);
				element.addDataFilter('SplitView');
			}, this);
		},

		submitOnChange: function(container) {
			container.getElements('form.submit_on_change').each(function(element) {
				dbug.warn('you are using a deprecated JFrame filter (submit_on_change) on %o, use the SubmitOnChange data-filter instead.', element);
				element.addDataFilter('SubmitOnChange');
			});
		},

		tabs: function(container) {
			if (!container.get('html').test('ccs-tab_ui')) return;
			container.getElements('.ccs-tab_ui').each(function(element){
				dbug.warn('you are using a deprecated JFrame filter (ccs-tab_ui) on %o, use the Tabs data-filter instead.', element);
				element.addDataFilter('Tabs');
				element.getElements('.ccs-tabs').addClass('tabs');
				element.getElements('.ccs-tab_sections').addClass('tab_sections');
			});
		},

		tips: function(container){
			if (!container.get('html').match(/ccs\-pointy_tip/)) return;
			container.getElements('.ccs-pointy_tip').each(function(element){
				dbug.warn('you are using a deprecated JFrame filter (ccs-pointy_tip) on %o, use the PointyTip data-filter instead.', element);
				element.addDataFilter('PointyTip');
			});
		},

		help_tips: function(container) {
			if (!container.get('html').match(/[ccs\-help_text][ccs\-info_text]/)) return;
			container.getElements('.ccs-help_text, .ccs-info_text').each(function(element) {
				var isHelp = element.hasClass('ccs-help_text');
				if (isHelp) {
					dbug.warn('you are using a deprecated JFrame filter (ccs-help_text) on %o, use the HelpTip data-filter instead.', element);
					element.addDataFilter('HelpTip');
				} else {
					dbug.warn('you are using a deprecated JFrame filter (ccs-info_text) on %o, use the HelpTip data-filter instead.', element);
					element.addDataFilter('InfoTip');
				}
			});
		},

                select_with_other: function(container) {
                        if (!container.get('html').contains('ccs-select-with-other')) return;
                        container.getElements('.ccs-select-with-other').each(function(el) {
                                dbug.warn('you are using a deprecated JFrame filter (ccs-select-with-other) on %o, use the SelectWithOther data-fitler instead.', el);
                                el.addDataFilter('SelectWithOther');
                        });
                }
	});

})();
