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
description: Adds an instance of Form.Validator.Inline to any form with the class .form-validator.
provides: [CCS.JFrame.FormValidator]
requires: [/CCS.JFrame, More/Form.Validator.Inline]
script: CCS.JFrame.FormValidator.js

...
*/

CCS.JFrame.addGlobalFilters({

	//validates any form with the .form-validator class
	form_validator: function(container) {
		if (!container.get('html').contains('form-validator')) return;
		container.getElements('form.form-validator').each(function(form) {
			//instantiate the form validator
			var validator = form.retrieve('validator');
			if (!validator) {
				validator = new Form.Validator.Inline(form, {
					useTitles: true
				});
			}
			//stupid monkey patch, for now. TODO(nutron)
			validator.insertAdvice = function(advice, field){
				//look for a .ccs-errors advice element that is a sibling of the field and inject errors there
				var target = field.getParent().getElement('.ccs-errors');
				if (target) target.adopt(advice);
				//otherwise inject them as siblings.
				else field.getParent().adopt(advice);
			};
			validator.setOptions({
				onShow: function(input, advice, className) {
					//scroll to errors within the jframe
					this.jframe.scroller.toElement(input);
				}.bind(this),
				//not the window
				scrollToErrorsOnSubmit: false
			});
		}, this);
	}

});