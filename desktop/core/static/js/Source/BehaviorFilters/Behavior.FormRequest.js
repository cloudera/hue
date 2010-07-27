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
description: Creates an instance of Form.Request for every form that JFrame loads.
provides: [CCS.JFrame.FormRequest]
requires: [/CCS.JFrame, More/Form.Request]
script: CCS.JFrame.FormRequest.js

...
*/

CCS.JFrame.addGlobalFilters({

	formRequest: function(element, events){
		// Make forms submit inside the jframe
		container.getElements('form').each(function(form){
			form.set('action', new URI(form.get('action'), {base: this.currentPath}));
			//pass null for the update element argument; JFrame does our updating for us
			var req = new Form.Request(form, null, {
				//we don't want submission of the form to reset it on AJAX success;
				//sometimes JFrame gets an error back in the html; JFrame will replace
				//the form for us.
				resetForm: false
			});
			this._setRequestOptions(req.request, {
				onSuccess: function(nodes, elements, text){
					this._requestSuccessHandler(req.request, text);
				}.bind(this)
			});
		}, this);
	}

});
