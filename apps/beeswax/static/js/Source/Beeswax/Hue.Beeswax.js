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
description: Beeswax (the Hive UI)
provides: [Hue.Beeswax]
requires: [JFrame/JFrame.Browser, clientcide/TabSwapper, More/Form.Validator.Inline, hue-shared/DynamicTextarea, hue-shared/Hue.JFrame.Chooser]
script: Hue.Beeswax.js

...
*/
ART.Sheet.define('window.beeswax.browser', {
	'min-width': 740
});

ART.Sheet.define('splitview.bw-editor', {
	'right-background-color': '#333'
});

(function(){

	Hue.Beeswax = new Class({

		Extends: Hue.JBrowser,

		options: {
			displayHistory: false,
			className: 'art beeswax browser logo_header',
			height: 350,
			jframeOptions: {
				clickRelays: 'a, .relays'
			}
		},

		initialize: function(path, options){
			this.parent(path || '/beeswax/', options);

			this.jframe.addShortcuts({
				'Open Selected': {
					keys: 'enter',
					shortcut: 'enter',
					handler: function(e){
						var table = $(this).getElement('[data-filters*=HtmlTable]');
						if (!table) return;
						hTable = table.retrieve('HtmlTable');
						var selected = hTable.selectedRows[0];
						if (!selected) return;
						Hue.JFrame.doubleClickHandler(this.jframe, e, selected);
					}.bind(this),
					description: 'Open the selected item.'
				}
			});
			this.jframe.addBehaviors({
				// breadcrumb pattern; has to set z-index programatically for layout
				'Breadcrumb': function(element, methods) {
					var items = element.getElements('li');
					items.reverse().each(function(item, i){
						item.setStyle('z-index', i+1);
					});
				},
				//breadcrumb form; displays a breadcrumb that grows as you fill out the form
				'BreadcrumbForm': function(element, methods) {
				/*
					The element is a UL with LI items for each breadcrumb; looks like this:
					<ul data-filters="Breadcrumb, BreadcrumbForm" class="clearfix" data-bc-sections=".hue-bc-section" data-bc-form="form">
						<li><a href="#step1">One</a></li>
						<li><a href="#step2">Two</a></li>
						<li><a href="#step3">Ect</a></li>
					</ul>
					
					it has a data-bc-sections definition which is a selector to select the sections that correlate to the bc links
					it has a data-bc-form selector that correlates to the form for this bc form.
				*/
					container = methods.getContentElement();
					var items = element.getElements('li');
					var form = container.getElement(element.get('data', 'bc-form')) || container.getElement('form');
					var sections = container.getElements(element.get('data', 'bc-sections'));
					//extend tab swapper; we need to manage things like OverText and FormValidator when we change sections
					var TS = new Class({
						Extends: TabSwapper,
						showSection: function(index) {
							//we validate the form when the user pages forward and not on the first display when this.now is still undefined
							//(where this.now is the current index of the TabSwapper; it's undefined on init)
							var validate = index > this.now && this.now != undefined;
							if (!validate) {
								//reset the error state
								form.get('validator').reset();
								if (this.now != undefined) items[this.now].removeClass('hue-bc-error');
							}
							if (!validate || getValidator(form).validate()) {
								//show the section if we're valid
								this.parent(index);
								//show the overtext that might have been hidden
								OverText.update();
							}
							return this;
						}
					});

					//get the form validator and add an event for when elements are validated
					//if the element fails, get the nav item and breadcrumb section and add an error class for styling
					getValidator(form).addEvents({
						elementValidate: function(valid, field){
							var section = field.getParent(element.get('data', 'bc-sections'));
							var nav = items[sections.indexOf(section)];
							if (valid) nav.removeClass('hue-bc-error');
							else nav.addClass('hue-bc-error');
						}
					});

					//create our modified tabswapper
					var tabs = new TS({
						tabs: items,
						sections: sections,
						smooth: true
					});
					//find any sections with an element with the class .hue-multipart-next and make that
					//next button change tabs; note that this is the only way the user can progress forward (for now)
					//todo: add some keyboard love; enter, tab, arrows, etc.
					sections.each(function(section, i) {
						section.getElements('.hue-multipart-next').addEvent('click', function(e){
							e.stop();
							if (getValidator(form).validate()) tabs.show(i+1);
						});
					});
				}
			});
			this.jframe.addBehaviorPlugin('SelectWithOther', 'SelectWithOtherValidation', function(element, methods) {
				//adds validation upon hiding the 'other' field
				var select = element.getElement('select');
				select.addEvent('change', function() {
					if(!select.getSelected()[0].get('value') == '__other__') {
						getValidator(element.getParent('form')).validate();
					}
				});
			});
			this.jframe.addFilters({
				visible: function(container){
					if(!container.get('html').contains('jframe-visible')) return;
					container.getElements('.jframe-visible').setStyle("display", "");
				}
			});
			this.addEvents({
				load: this.setup.bind(this)
			});
			this.jframe.addEvents({
				beforeRenderer: this.stripColumnTemplates.bind(this)
			});
		},

		setup: function(view) {
			switch(view) {
				case 'table-setup':
					this.setupTableForm();
					break;
				case 'execute':
					this.setupEditor();
					break;
				case 'choose-file':
					this.setupChooseFile();
					break;
				case 'choose-delimiter':
					this.setupChooseDelimiter();
					break;
				case 'define-columns':
					this.setupDefineColumns();
					break;
			}
		},

		setupChooseFile: function(){
			var importData = $(this).getElement('.bw-import_data');
			var impLabel = importData.getElement('label');
			var impInput = importData.getElement('input');
			var checkImportData = function(e){
				if (impInput.get('checked')) {
					impLabel.removeClass('hue-bw-selected');
					impInput.setProperty('checked', 'false');
				} else {
					impLabel.addClass('hue-bw-selected');
					impInput.setProperty('checked');
				}
			};
			impLabel.addEvent('click', checkImportData);
			if(impInput.get('checked')) impLabel.addClass('hue-bw-selected');
		},
		
		setupDefineColumns: function(){
			var showHive = $(this).getElement('.bw-show_hive');
			var hiveLabel = showHive.getElement('label');
			var hiveInput = showHive.getElement('input');
			var checkShowHive = function(e){
				if (hiveInput.get('checked')) {
					hiveLabel.addClass('hue-bw-selected');
					hiveInput.setProperty('checked', 'false');
				} else {
					hiveLabel.removeClass('hue-bw-selected');
					hiveInput.setProperty('checked');
				}
			};
			hiveLabel.addEvent('click', checkShowHive);
		},
		setupChooseDelimiter: function(){
			var confirmDelim = $(this).getElement('.bw-confirm_delim');
			var selectDelim = $(this).getElement('.bw-select_delim');
			if(confirmDelim) {
				var yes = confirmDelim.getElement('input[name=Yes]');
				var no = confirmDelim.getElement('input[name=No]');
				confirmDelim.show();
				selectDelim.hide();
				no.addEvent('click', function(){
					confirmDelim.hide();
					selectDelim.show();
				});
			} else {
				selectDelim.show();
			}
			var otherInput = selectDelim.getElement('input[name=delimiter_1]');
			var delimiters = selectDelim.getElement('select[name=delimiter_0]');
			delimiters.addEvent('change', function(e){
				if(delimiters.getProperty('value') !== '__other__')
				{
					var form = delimiters.getParent('form');
					form.retrieve('form.request').setOptions({
						extraData:
							{'submit_preview': 'Preview'}
						}).send();
				}
			});
		},

		setupTableForm: function(){
			/* format inputs */
			var formatSection = $(this).getElement('.bw-format');
			//all the inputs in the format section have custom click behavior
			//to add a css class for styling purposes based on their checked state
			var checkFormSectionInput = function(input, validate) {
				if (input.get('checked')) {
					formatSection.getElements('dt').removeClass('hue-bw-selected');
					input.getParent('dt').addClass('hue-bw-selected');
					if (validate) $(this).getElement('form').validate();
				}
			}.bind(this);
			//when the user clicks, check the input and set up classes, validate the form, etc.
			formatSection.getElements('input').each(function(input) {
				input.addEvent('click', function(){
					checkFormSectionInput(input, true);
				});
				//do this on startup in case the input has a default value
				checkFormSectionInput(input);
				//if the input is checked, we have to invoke the data-group-toggle manually
				//otherwise the next slide shows both the delimited and serde options
				if (input.get('checked')) input.getParent('[data-group-toggle]').fireEvent('click');
			}, this);

			/* file formats */
			var fileSection = $(this).getElement('.bw-file_formats');
			var labels = fileSection.getElements('label');
			var inputFormatDetails = $(this).getElement('.bw-io_formats');
			//fix layout issues; django forces all choice elements to be in a ul
			fileSection.getElement('ul').addClass('clearfix');

			//private method to retrieve an overtext for an input or create one if there isn't one yet
			var getOT = function(input) {
				var ot = input.retrieve('OverText');
				if (!ot) ot = new OverText(input);
				return ot;
			};

			//get the inputs for the file section
			fileSection.getElements('input').each(function(input) {
				//whent he user chooses one, add some selected state for styling
				input.addEvent('click', function(){
					labels.removeClass('hue-bw-selected');
					input.getParent('label').addClass('hue-bw-selected');
					//if the user chooses InputFormat, show the details for that input
					//and configure them to be validated
					if (input.get('value') == 'InputFormat') {
						inputFormatDetails.reveal().get('reveal').chain(function(){
							inputFormatDetails.getElements('input').each(function(input){
								getOT(input).enable();
								input.removeClass('ignoreValidation').addClass('required');
							});
						});
					} else {
						//else hide the input format details and disable the validation
						inputFormatDetails.dissolve().getElements('input').each(function(input){
							getOT(input).disable();
							input.addClass('ignoreValidation');
							getValidator(input.getParent('form')).validate();
						});
					}
				});
			});

			/* file location */
			var fileLocation = $(this).getElement('.bw-file_location');
			var defLabel = fileLocation.getElement('.bw-default_location label');
			var fileLoc = fileLocation.getElement('.bw-external_loc');
			var fileLocInput = fileLoc.getElement('input').addClass('reqiured');
			var input = fileLocation.getElement('.bw-default_location input').set('checked', true);
			//private method to toggle style state, validation, and the file location input
			var checkFileLoc = function(e){
				if (input.get('checked')) {
					defLabel.addClass('hue-bw-selected');
					getOT(fileLocInput).disable();
					fileLocInput.addClass('ignoreValidation');
					fileLoc.dissolve();
					//only validate if this was a user-initiated event
					if (e) getValidator(input.getParent('form')).validate();
				} else {
					defLabel.removeClass('hue-bw-selected');
					fileLoc.removeClass('ignoreValidation').reveal().get('reveal').chain(function(){
						getOT(fileLocInput).enable();
					});
				}
			};
			//check the file state when the user changes the input value
			input.addEvent('click', checkFileLoc);
			//call it now to set it up.
			checkFileLoc();
			
			/* column tables */
			var columns = $(this).getElements('div.bw-column');
			var columnHeaders = $(this).getElements('.bw-columns dt.bw-column_header');
			var columnSections = $(this).getElements('.bw-columns dd.bw-column');
			//the column layout is an accordion; starts off with all closed.
			this.columnAccordion = new Fx.Accordion(columnHeaders, columnSections, {
				onActive: function(toggler, section) {
					toggler.addClass('bw-active').removeClass('bw-inactive');
				},
				onBackground: function(toggler, section) {
					toggler.removeClass('bw-active').addClass('bw-inactive');
				},
				display: -1
			});
			
			//create a column form instance for each column form.
			columns.each(function(column, i) {
				new ColumnForm(column, this.columnAccordion, {
					onRemove: this.removeColumn.bind(this)
				});
			}, this);
			//create buttons to add new columns
			['column', 'partition'].each(function(type) {
				$(this).getElement('.bw-add_' + type + ' button').addEvent('click', function(e) {
					e.stop();
					this.addColumn(type, this.columnAccordion);
				}.bind(this));
			}, this);
			
		},

		/*
			finds the column templates in the jframe response and removes them before
			jframe sets them up like all the other forms
			container - (object) see JFrame's beforeRender event
			options - (object) ditto
		*/
		stripColumnTemplates: function(container, options){
			this.columnTemplates = {};
			['column', 'partition'].each(function(type) {
				var el;
				container.elements.some(function(section) {
					if (!el) el = section.getElement('.beeswax_' + type + '_form_template');
					return el;
				});
				if (el) {
					this.columnTemplates[type] = el.get('html');
					el.destroy();
				}
			}, this);
		},

		/*
			adds a new column form
			type - either "column" or "partition"
			accordion - the accordion that the column is controlled by
		*/
		addColumn: function(type, accordion){
			//find the current count
			var count_input = $(this).getElement('input[name=' + type +'s-next_form_id]');
			//increment it and store it back into the input (as we're adding here)
			var count = count_input.get('value').toInt();
			count_input.set('value', count + 1);
			//create a new column from the template
			var column = Elements.from(this.columnTemplates[type].replace(/TEMPLATE/g, count))[0];
			//store some metadata about it, inject it into the list.
			column.store('bw:col-type', type).store('bw:col-count', count);
			column.hide().inject($(this).getElement('.bw-' + type + '-forms'));
			//apply JFrame magic
			this.jframe.applyFilters(column);
			//get the header and then add it to the accordion
			var columnHeader = column.getElement('dt.bw-column_header');
			accordion.addSection(columnHeader, column.getElement('dd.bw-column'));
			//expose the new section
			column.reveal();
			//get the header in that column and, now that it's visible, show its overtext
			var input = column.getElement('dt.bw-column_header input');
			var ot = input.retrieve('OverText');
			if (!ot) ot = new OverText(input);
			ot.enable();
			//create a new instance of ColumnForm with our new column
			new ColumnForm(column, accordion, {
				onRemove: this.removeColumn.bind(this)
			});
			//add the fields in our column to the validator for the form.
			getValidator(column.getParent('form')).watchFields(column.getElements('input, textarea, select'));
		},
		
		removeColumn: function(column){
			column.getElements('input, select, textarea').addClass('ignoreValidation');
			column.getParent('form').validate();
			column.dissolve();
                        var column_id = column.retrieve('bw:col-count');
			new Element('input', {
				'type': 'hidden',
				'name': 'columns-' + (column_id == null ? "0" : column_id)  + '-_deleted',
				'value': 'True'
			}).inject(column);
		},

		setupEditor: function(){
			//get the editor area, textarea input, & header
			var editor = $(this).getElement('.bw-query_bottom');
			var ta = editor.getElement('textarea');
			//this resizer method resizes the editor area to fill the remaining space below the header
			//the shade event is passed true/false if the shade is engaged or not
			var resizer = function(){
				var header = $(this).getElement('.bw-query_header').getSize().y;
				editor.setStyle('height', this.contentSize.y - header - 2);
				ta.setStyle('height', this.contentSize.y - header - 2);
			}.bind(this);
			//do so at startup
			resizer();
			//and any time the window is resized
			this.addEvent('unshade', resizer);
			//remove this resize handler on unload
			this.jframe.markForCleanup(function(){
				this.removeEvent('unshade', resizer);
			}.bind(this));
			//when the user clicks the save as link, show a popup with the save as form
			//when we fire the click manually, it means we want to submit the form
			var saveAs = $(this).getElement('.bw-query_save_as');
			var saver = $(this).getElement('.bw-query_save_form');
			var saveIt = function(){
				//grab the container of the save as inputs and clone them
				//(clone them because our windows destroy themselves on hide)
				//Hide on clone to ensure that display property is set to none.
				var form = saver.clone().hide();
				//prompt the user w/ the form
				var prompt = this.prompt('Save This Query', form.show(), function(){
					//replace the saver form with the one the user filled out
					form.replaces(saver).hide();
					//now we're ready to submit the form
					saving = true;
					//and submit the form
					saveAs.click();
					//back to showing the popup
					saving = false;
				});
			}.bind(this);
			var saving;
			saveAs.addEvent('click', function(e){
				//if we aren't trying to submit the form, show the popup
				if (!saving) {
					//this is the callback for when the user hits the "ok" button
					//TODO add some keyboard love for the enter button in fields?
					e.stop();
					saveIt();
				}
			}.bind(this));
			if (saver.getElements('.beeswax_error li').length) saveIt();
			
			//add the settings toggle
			var splitEl = $(this).getElement('div[data-filters*=SplitView]');
			if (splitEl) {
				//get the instance of splitview
				var split = splitEl.get('widget');
				if (split) {
					//let's not show the scrollbar over on the left side
					split.left.setStyle('overflow-x', 'hidden');
					split.addClass('bw-editor');
					//when the user clicks the toggle
					$(this).getElement('.bw-query_settings_toggle').addEvent('click', function(e){
						e.preventDefault();
						//expose or hide the left column
						split.chain(resizer).fold('left', split.left.getSize().x > 0 ? 0 : 230);
					}.bind(this));
				}
			}
			
		}

	});

	//returns an inline form validator for a form or creates one if there isn't one yet
	var getValidator = function(form) {
		var validator = form.retrieve('validator');
		if (!validator) {
			validator = new Form.Validator.Inline(form, {
				useTitles: true
			});

			var bwValidateNameRE = /^[a-zA-Z_]\w*/;
			validator.add('bw-validate-name', {
				errorMsg: 'Please enter a value only containing numbers, letters, underscores - the value cannot begin with a number.',
				test: function(element){
					return Form.Validator.getValidator('IsEmpty').test(element) ||
						(bwValidateNameRE).test(element.get('value'));
				}
			});

		}

		return validator;
	};

	/*
		column form class; needed because we add these dynamically
		column - the container of the form
		header - the header of the section
	*/
	var ColumnForm = new Class({
		Implements: [Options, Events],
		initialize: function(column, accordion, options) {
			this.column = column;
			this.header = column.getElement('dt.bw-column_header');
			this.accordion = accordion;
			this.setOptions(options);
			this.setupHeader();
			this.setupMapData();
			column.getElement('.bw-remove_column button').addEvent('click', function(e){
				e.stop();
				this.fireEvent('remove', column);
			}.bind(this));
		},
		setupHeader: function(){
			//get the header and style it's input behaviors
			var input = this.header.getElement('input');
			input.addEvents({
				focus: function(){
					this.header.removeClass('bw-filled');
					input.addClass('bw-focused').select();
					this.accordion.display(this.accordion.togglers.indexOf(this.header));
				}.bind(this),
				blur: function(){
					if (input.get('value')) this.header.addClass('bw-filled');
					else this.header.removeClass('bw-filled');
					input.removeClass('bw-focused');
				}.bind(this)
			});
			this.header.getElement('label').addEvents({
				mouseover: function(){
					input.addClass('bw-focused');
				}.bind(this),
				mouseleave: function(){
					input.removeClass('bw-focused');
				}.bind(this)
			});
		},
		setupMapData: function(){
			var mapSection = this.column.getElement('.bw-map_data');
			if (!mapSection) return; //partition tables don't have these
			var arrayTypeSection = this.column.getElement('.bw-array_type');

			var typeSelect = this.column.getElement('.bw-col_type select');
			var arrayTypeSelect = this.column.getElement('.bw-array_type select');

			var checkType = function(){
				if (typeSelect.getSelected()[0].get('value') == 'array') arrayTypeSection.fade('in');
				else arrayTypeSection.fade('out');
				
				if (typeSelect.getSelected()[0].get('value') == 'map') mapSection.reveal();
				else mapSection.dissolve();
			};
			//for each column table, hide its mapdata config unless the user selects that in the array type
			arrayTypeSelect.addEvent('change', checkType.pass(true));
			typeSelect.addEvent('change', checkType.pass(true));
			checkType();
		}
	});

})();
