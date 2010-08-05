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
description: Makes form validator instances scroll the jframe to the errors.
provides: [Behavior.FormValidatorScroller]
requires: [Widgets/Behavior.FormValidator]
script: Behavior.FormValidatorScroller.js
...
*/

Behavior.addGlobalPlugin('FormValidator', 'FormValidatorScroller', function(element, methods){
	var validator = element.retrieve('validator');
	validator.setOptions({
		onShow: function(input, advice, className) {
			//scroll to errors within the jframe
			/*JFrame Reference */
			methods.getScroller().toElement(input);
		},
		//not the window
		scrollToErrorsOnSubmit: false
	});
});
