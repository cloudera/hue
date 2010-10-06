/*
---
description: Any JFrame response that has a root-level child element with the class .alert_popup is displayed in an alert overlaying the previous state which is restored when the alert is closed. If the class .jframe_renders is also applied to that element, the jframe is not restored but displays the remaining portion of the response as normal.
provides: [CCS.JFrame.Alert]
requires: [/CCS.JFrame, Widgets/ART.Alerts]
script: CCS.JFrame.Alert.js

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

	alert: function(content) {
		var options = content.options;
		//if the contents have an element with .alert_popup *at the root*
		//then display those contents in an alert
		var popup = content.elements.filter('.alert_popup')[0];
		if (!popup) return;
		
		//does the jframe still get to render?
		var jframe_renders = popup.hasClass('jframe_renders');

		var target = new Element('div', {'class': 'jframe_alert'}).hide().inject($(this));
		var popupBehavior = new Behavior({
			onError: function(){
				dbug.warn.apply(dbug, arguments);
			}
		});
		var fillAndShow = function() {
			if (!jframe_renders) {
				//if we aren't rendering the jframe, fill the popup
				//and remove the toolbar
				this.fill(target, content, popupBehavior);
				var toolbar = content.elements.filter('.toolbar');
				if (toolbar.length) toolbar.hide();
			} else {
				//otherwise we're going to leave the content object alone and clone
				//the popup, hiding the original
				this.fill(target, {
					elements: $$(popup.clone())
				}, popupBehavior);
				popup.hide();
			}
			target.show();
		}.bind(this);

		//our method to actually show the alert
		var alerter = function(){
			if(!Browser.Engine.trident) fillAndShow();
			if (options.blankWindowWithError) {
				CCS.error(content.title, target);
				if (Browser.Engine.trident) fillAndShow();
				this.getWindow().hide();
			} else {
				var alert = this.alert(content.title, target);
				if (Browser.Engine.trident) fillAndShow();
				target.getElements(":widget").each(function(widget) {
					widget.get("widget").register(widget.getParent(":widget").get("widget"));
				});
				if (options) {
					if (options.blankWindowWithError) {
						alert.addEvent('destroy', function(){
							this.getWindow().hide();
						}.bind(this));
					}
				}
				alert.addEvent('destroy', function() {popupBehavior.cleanup(target);});
				alert.position().show();
				
				//if jframe is rendering we remove this event which we're going to add a few lines down
				if (jframe_renders) this.removeEvent('afterRenderer', alerter);
				if (options.callback) options.callback(data);
			}
		}.bind(this);

		//if jframe is rendering, we need to give it the thread
		//otherwise it trashes the content AFTER we position
		//which throws it off
		if (jframe_renders) this.addEvent('afterRenderer', alerter);
		else alerter();
		
		//if jframe is rendering, return false (so it will continue as if nothing happened)
		return !jframe_renders;
	}

});
