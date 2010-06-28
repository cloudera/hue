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
description: Makes all links with the css class .prompt_and_post prompt the user with the contents of the url in the link and then send the values they input when they hit ok.
provides: [CCS.JFrame.PromptAndPost]
requires: [/CCS.JFrame, Widgets/ART.Alerts]
script: CCS.JFrame.PromptAndPost.js

...
*/

CCS.JFrame.addGlobalLinkers({

	'.prompt_and_post': function(e, link){
		//for each link with the class .prompt_and_post, prompt the user to fill out a form in a popup
		//with the contents of the link's href, applying delegates to the popup, and handling the 
		//form submission with a Form.Request.
		if (e) e.preventDefault();
		var target = new Element('div', {'class': 'jframe_prompt'});
		this.load({
			target: target,
			suppressLoadComplete: true,
			requestPath: link.get('href'),
			callback: function(data){
				var size = this.content.getSize();
				this.prompt(data.title || 'Enter Details', target, function(){
					target.getElement('form').retrieve('form.request').send();
				}, {
					resizable: true
				});
			}.bind(this)
		});
	}

});