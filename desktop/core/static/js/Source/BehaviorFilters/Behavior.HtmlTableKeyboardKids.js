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
description: Adds support for children of an HtmlTable to declare keyboard shortcuts
provides: [Behavior.HtmlTableKeyboardKids]
requires: [Widgets/Behavior.HtmlTable]
script: Behavior.HtmlTableKeyboardKids.js
...
*/
;(function(){

function buildShortcutForElement(shortcutElement, attrMap, shortcutMap){
	/*
		shortcutElement     -- the element that defines this shortcut
		attrMap             -- object that maps the attribute to get the keys value from
		attrMap.keys        -- string to use to lookup the `keys` attribute for ths shortcut
		attrMap.description -- string to use to lookup the `description` attribute for ths shortcut
		attrMap.handler     -- function to call when the shortcut event gets triggered.
		                         function(event, shortcutElement){ Cf. Keyboard for more info }
		                         Note: This function is loosely referenced by key,
		                           Changing attrMap.handler instantly updates the shortcut handler.
		shortcutMap         -- (optional) an existing object to append to
	*/
	if (!shortcutMap) shortcutMap = {};
	var shortcutObject = {};
	shortcutObject.keys = shortcutElement.get(attrMap.keys || 'data-accesskey');
	// Don't add this shortcut if there's no `keys`
	if (!shortcutObject.keys) return shortcutMap;
	shortcutObject.description = shortcutElement.get(attrMap.description || 'title') || shortcutElement.get('alt');
	shortcutObject.handler = function(event){
		// delay to work around an issue where...
		//   keydown triggers this & another action
		//   keyup then may trigger a third action unexpectedly
		//   this delay works around unintentionally triggering that third action
		//   by allowing some time for the first action to be completely handled
		attrMap.handler.delay(100, this, [event, shortcutElement]);
	};
	shortcutMap[shortcutElement.get(attrMap.name || 'text')] = shortcutObject;
	return shortcutMap;
}

function buildShortcuts(shortcutElements, attrMap, shortcutMap){
	// Same as buildShortcutForElement,
	//   but it takes an array-like object of elements instead of a single element
	if (!shortcutMap) shortcutMap = {};
	for (var i = -1, el; el = shortcutElements[++i];){
		buildShortcutForElement(el, attrMap, shortcutMap)
	}
	return shortcutMap;
}

Behavior.addGlobalPlugin('HtmlTable', 'HtmlTableKeyboardKids', function(htmlTableElement, behaviorAPI){
	// Since every HtmlTable Behavior GlobalPlugin runs for every HtmlTable instance,
	//   we need to limit this plugin to only those instances that opt-in
	if (!(htmlTableElement && htmlTableElement.hasClass('keyboardkids'))) return;
	var htmlTable = htmlTableElement.retrieve('HtmlTable');
	if (!htmlTable) return;
	var keyboard = htmlTable.keyboard;
	if (!keyboard) return;

	keyboard.addShortcuts(
		buildShortcuts(
			htmlTableElement.getElements('thead [data-accesskey]'),
			{
				name: 'text',
				keys: 'data-accesskey',
				description: 'title',
				handler: function(event, shortcutElement) {
					behaviorAPI.callClick(event, shortcutElement, true);
				}
			}
		)
	);
});

}());
