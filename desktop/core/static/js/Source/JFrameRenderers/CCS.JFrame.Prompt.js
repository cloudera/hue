/*
---
description: Any JFrame response that has a root-level child element with the class .prompt_popup is displayed in a prompt overlaying the previous state which is restored when the prompt is canceled.
provides: [CCS.JFrame.Prompt]
requires: [/CCS.JFrame, Widgets/ART.Alerts, Widgets/Behavior]
script: CCS.JFrame.Prompt.js

...
*/
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
CCS.JFrame.addGlobalRenderers({

	prompt: function(content) {
		var options = content.options;
		
		//if the contents have an element with .prompt_popup *at the root*
		//then display those contents in a prompt, submitting the form (if present)
		//when the user clicks "ok"
		var popup = content.elements.filter('.prompt_popup')[0];
		if (!popup) return;
		var target = new Element('div', {'class': 'jframe_prompt'}).hide().inject($(this));
		var popupBehavior = new Behavior({
			onError: function(){
				dbug.warn.apply(dbug, arguments);
			}
		});
		popupBehavior.passMethods({
			getContentElement: $lambda(target),
			configureRequest: this.configureRequest.bind(this)
		});
		var fillAndShow = function() {
			this.fill(target, content, popupBehavior);
			target.show();
		}.bind(this);
		//VML in IE doesn't like being hidden and redisplayed.  Delaying filling and showing the target for 
		if(!Browser.Engine.trident) {
			fillAndShow();
		}
		var toolbar = content.elements.filter('.toolbar');
		if (toolbar.length) toolbar.hide();

		var size = this.content.getSize();
		var form = popup.getElement('form');
		var hasInput = !!popup.getElement('form') && !!popup.getElement('input, textarea, select');
		var prompt = this.prompt(content.title || 'Enter Details', target, function(){
			if (form) form.retrieve('form.request').send();
		}, {
			detectInput: !hasInput,
			resizable: true
		});
		prompt.addEvent('resize', function() {popupBehavior.resize.bind(popupBehavior);});
		prompt.addEvent('destroy', function() {popupBehavior.cleanup(target); });
		
		if(Browser.Engine.trident) {
			fillAndShow();
			prompt.findInputs();
		}
		target.getElements(":widget").each(function(widget) {
			widget.get("widget").register(widget.getParent(":widget").get("widget"));
		});
		if (form) {
			form.addEvent('submit', function(){
				prompt.hide();
			});
			var inputs = form.getElements('input, textarea');
			var focused;
			inputs.some(function(input){
				if (focused) return;
				if (input.isVisible()) {
					focused = true;
					input.select();
				}
			});

		}
		if (options.callback) options.callback(data);

		return true;
	}
});
