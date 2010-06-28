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
description: Handles the basic functionality of submitting a form and recieving JSON as a result.
provides: [Form.Request.JSON]
requires: [Core/Request.JSON, More/Form.Request]
script: Form.Request.JSON.js

...
*/
Form.Request.JSON = new Class({

	Extends: Form.Request,

	initialize: function(form, options){
		this.parent(form, form, options);
	},

	makeRequest: function(){
		this.request = new Request.JSON($merge({
				url: this.element.get('action'),
				emulation: false,
				spinnerTarget: this.element,
				method: this.element.get('method') || 'post'
		}, this.options.requestOptions)).addEvents({
			success: function(obj, text){
				['success', 'complete'].each(function(evt){
					this.fireEvent(evt, [obj, text]);
				}, this);
			}.bind(this),
			failure: function(xhr){
				this.fireEvent('failure', xhr);
			}.bind(this),
			exception: function(){
				this.fireEvent('failure', xhr);
			}.bind(this)
		});
	}

});
