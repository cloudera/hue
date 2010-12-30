
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
 CCS.JFrame.Collapsible,
 CCS.JFrame.ContextMenu,
 CCS.JFrame.ArtButtons,
 CCS.JFrame.DataGroupToggle,
 CCS.JFrame.FilterInput,
 CCS.JFrame.FitText,
 CCS.JFrame.FormValidator,
 CCS.JFrame.HtmlTable,
 CCS.JFrame.Input,
 CCS.JFrame.OverText,
 CCS.JFrame.SelectWithOther,
 CCS.JFrame.SideBySideSelect,
 CCS.JFrame.SizeTo,
 CCS.JFrame.SplitView,
 CCS.JFrame.SubmitOnChange,
 CCS.JFrame.Tabs,
 CCS.JFrame.Tips,
 Hue.JFrame.DeprecatedFilters,
 Hue.JFrame.Collapsible,
 Hue.JFrame.ContextMenu,
 Hue.JFrame.ArtButtons,
 Hue.JFrame.DataGroupToggle,
 Hue.JFrame.FilterInput,
 Hue.JFrame.FitText,
 Hue.JFrame.FormValidator,
 Hue.JFrame.HtmlTable,
 Hue.JFrame.Input,
 Hue.JFrame.OverText,
 Hue.JFrame.SelectWithOther,
 Hue.JFrame.SideBySideSelect,
 Hue.JFrame.SizeTo,
 Hue.JFrame.SplitView,
 Hue.JFrame.SubmitOnChange,
 Hue.JFrame.Tabs,
 Hue.JFrame.Tips
]
requires: [/Hue.JFrame, Widgets/Element.Data]
script: Hue.JFrame.ArtButtons.js

...
*/

(function(){

	var artInputsRegEx = /hue-search|hue-input/;

	Hue.JFrame.addGlobalFilters({

		artButtons: function(container) {
			if (container.get('html').contains('jframe-button_bar')) {
				container.getElements('.jframe-button_bar, .jframe-button_subbar_above, .jframe-button_subbar_below').each(function(element) {
					var above = element.hasClass('jframe-button_subbar_above');
					var below = element.hasClass('jframe-button_subbar_below');
					dbug.warn('you are using a deprecated JFrame filter (jframe-button_bar) on %o, use the ArtButtonBar data-filter instead.', element);
					element.addDataFilter('ArtButtonBar');
					if (above) element.set('data', 'bar-position', 'above');
					if (below) element.set('data', 'bar-position', 'below');
				});
			}

			if (container.get('html').contains('hue-art_button')) {
				container.getElements('a.hue-art_button, button.hue-art_button, input.hue-art_button').each(function(element){
					dbug.warn('you are using a deprecated JFrame filter (hue-art_button) on %o, use the ArtButton data-filter instead.', element);
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
			if (!container.get('html').contains('hue-truncate')) return;
			container.getElements('.hue-truncate').each(function(element){
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
			container.getElements('table.hue-data_table').each(function(element){
				dbug.warn('You are using a deprecated JFrameFilter (hue-data_table) on %o, use the DataTable data-filter instead.', element);
				element.addDataFilter('HtmlTable');	
			});
		},


		artInputs: function(container) {
			if (!container.get('html').match(artInputsRegEx)) return;
			container.getElements('.hue-search, .hue-input').each(function(element){
				dbug.warn('you are using a deprecated JFrame filter (hue-search or hue-input) on %o, use the ArtInput data-filter instead.', element);
				element.addDataFilter('ArtInput');
				if (element.hasClass('hue-search')) element.set('data', 'art-input-type', 'search');
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
			if (!container.get('html').test('hue-tab_ui')) return;
			container.getElements('.hue-tab_ui').each(function(element){
				dbug.warn('you are using a deprecated JFrame filter (hue-tab_ui) on %o, use the Tabs data-filter instead.', element);
				element.addDataFilter('Tabs');
				element.getElements('.hue-tabs').addClass('tabs');
				element.getElements('.hue-tab_sections').addClass('tab_sections');
			});
		},

		tips: function(container){
			if (!container.get('html').match(/hue\-pointy_tip/)) return;
			container.getElements('.hue-pointy_tip').each(function(element){
				dbug.warn('you are using a deprecated JFrame filter (hue-pointy_tip) on %o, use the PointyTip data-filter instead.', element);
				element.addDataFilter('PointyTip');
			});
		},

		help_tips: function(container) {
			if (!container.get('html').match(/[hue\-help_text][hue\-info_text]/)) return;
			container.getElements('.hue-help_text, .hue-info_text').each(function(element) {
				var isHelp = element.hasClass('hue-help_text');
				if (isHelp) {
					dbug.warn('you are using a deprecated JFrame filter (hue-help_text) on %o, use the HelpTip data-filter instead.', element);
					element.addDataFilter('HelpTip');
				} else {
					dbug.warn('you are using a deprecated JFrame filter (hue-info_text) on %o, use the HelpTip data-filter instead.', element);
					element.addDataFilter('InfoTip');
				}
			});
		},

                select_with_other: function(container) {
                        if (!container.get('html').contains('hue-select-with-other')) return;
                        container.getElements('.hue-select-with-other').each(function(el) {
                                dbug.warn('you are using a deprecated JFrame filter (hue-select-with-other) on %o, use the SelectWithOther data-fitler instead.', el);
                                el.addDataFilter('SelectWithOther');
                        });
                },

                side_by_side_select: function(container) {
                        if (!container.get('html').contains('side_by_side_select')) return;
                        //get the side by side containers
                        container.getElements('.side_by_side_select').each(function(select) {
                                //if the element with the side_by_side class is the container of the select, get the 
                                //select element within it.
                                if (select && select.get('tag') != "select") select = select.getElement('select');
                                dbug.warn('you are using a deprecated JFrame filter (side_by_side_select) on %o, use the SideBySideSelect data-filter instead.', select);
                                select.addDataFilter('SideBySideSelect');
                        });
                },

                data_group_toggle : function(container){
                        if(!container.get('html').contains('hue-group_toggle')) return;
                        var toggles = container.getElements('.hue-group_toggle');
                        toggles.each(function(toggle) {
                                dbug.warn("you are using a deprecated JFrameFilter (hue-group_toggle) on %o, use the DataGroupToggle data-filters propery instead.", toggle);
                                toggle.addDataFilter('DataGroupToggle');
                        });
                },

                collapsible: function(container) {
                        if (!container.get('html').contains('collapser')) return;
                        //make collapsibles for each .collapser/.collapsible pair (kind of like accordion)
                        var togglers = container.getElements('.collapser');
                        var sections = container.getElements('.collapsible');
                        togglers.each(function(toggler, i) {
                                //This message is uniquely strong because there's no reasonable way to add the functionality,
                                //as every case is unique.  In order to get the functionality, you MUST add the CollapsingElements
                                //data-filter property.
                                if(!toggler.getParent('[data-filters*=CollapsingElements]'))
                                {
                                        dbug.warn("you are using a deprecated JFrame pattern (collapser) on %o, you must add the CollapsingElements data-filter property to a mutual parent of the collapser and collapsible to get the collapsible functionality.", toggler);
                                }
                        });
                }



	});

})();
