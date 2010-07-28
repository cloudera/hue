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
description: Configures every form to use the Form.Request behavior.
provides: [CCS.JFrame.FormRequest]
requires: [/CCS.JFrame, More/Form.Request]
script: CCS.JFrame.FormRequest.js

...
*/

CCS.JFrame.addGlobalFilters({

	//this runs BEFORE Behavior.FormRequest
	formRequest: function(container){
		//get all forms in the response
		container.getElements('form').each(function(form){
			//set their action url and add the FormRequest filter
			form.set('action', new URI(form.get('action'), {base: this.currentPath})).addDataFilter("FormRequest");
		}, this);
	}

});

//this runs AFTER Behavior.FormRequest
Behavior.addGlobalPlugin('FormRequest', 'JFrameFormRequest', function(element, methods){
	//get the Form.Request instance
	var req = element.get('formRequest');
	//tell it not to update anything
	req.update = null;
	//configure its request to use JFrame's response handler
	methods.configureRequest(req.request);
});