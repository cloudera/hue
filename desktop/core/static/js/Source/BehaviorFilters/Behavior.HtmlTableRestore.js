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
description: Makes HtmlTable instances retain their state on refresh.
provides: [Behavior.HtmlTableRestore]
requires: [Widgets/Behavior.HtmlTable]
script: Behavior.HtmlTableRestore.js
...
*/

Behavior.addGlobalPlugin('HtmlTable', 'HtmlTableRestore', function(element, methods){
	var table = element.retrieve('HtmlTable');
	//Get tables in the current frame
	var tables = methods.getContentElement().getElements('[data-filters*=HtmlTable]');
	var tableIndex = tables.indexOf(element);
	var tableState = methods.getBehaviorState().tableState;
	var loadEvent = function(loadOptions) {
		//On load, if there is a previous page and it's the same as the current page, and there's a state array and this state array has the same number of entries as there are tables in the frame, restore the state.
		if(loadOptions.previousPath && loadOptions.previousPath == loadOptions.requestPath && tableState && tableState.length == tables.length && tableState[tableIndex]) {
			table.restore(tableState[tableIndex]);
		} else if(tableState && tableState[tableIndex]) {
			delete tableState;
		}
	};
	methods.addEvent('load', loadEvent);
	var changeEvent = function() {
		//On change, create the tableState array and the particular index needed, if necessary.  Then store the serialized state.
		if(!methods.getBehaviorState().tableState) methods.getBehaviorState().tableState = [];
		tableState = methods.getBehaviorState().tableState;
		if(!tableState[tableIndex]) tableState[tableIndex] = {};
		tableState[tableIndex] = this.serialize();
	};
	table.addEvent('stateChanged', changeEvent);
	this.markForCleanup(element, function() {
		methods.removeEvent('load', loadEvent);
		table.removeEvent('stateChanged', changeEvent);
	});
});
