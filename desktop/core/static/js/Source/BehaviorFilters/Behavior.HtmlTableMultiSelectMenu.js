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
description: Adds support for HtmlTable context menus for multiple selected rows.
provides: [Behavior.HtmlTableMultiSelectMenu]
requires: [Widgets/Behavior.HtmlTable, /Behavior.ContextMenu]
script: Behavior.HtmlTableMultiSelectMenu.js
...
*/
Behavior.addGlobalPlugin('HtmlTable', 'HtmlTableMutiSelect', function(element, methods){
	var table = element.retrieve('HtmlTable');
	var previousSelected;
	//check if the table has a context menu for bulk edits
	//and we can multi-select things
	if (table.options.allowMultiSelect && element.hasDataFilter('ContextMenu')) {
		//wait for a short period to get the table's context menu; we have no guarantee
		//that its been created before this filter runs
		var tableMenu;
		(function(){
			tableMenu = element.retrieve('ContextMenu');
			if (tableMenu) tableMenu.disable();
		}).delay(10);
		//when the user selects a row
		table.addEvent('rowFocus', function(row, selectedRows){
			//if there is no context menu on the table, then exit
			if (!tableMenu) return;
			var action;
			//if there was a previously selected group of menus, re-enable them.
			if (previousSelected) {
				previousSelected.each(function(trMenu){
					trMenu.enable();
				});
				previousSelected.empty();
			}
			//if the user has selected more than one row
			if (selectedRows.length > 1) {
				//enable the table's menu
				tableMenu.enable();
				//loop through the selected rows and disable their menus
				//this allows the right click event to travel past the table row level and up to the table
				//so the bulk action menu is displayed
				previousSelected = selectedRows.map(function(tr){
					var trMenu = tr.retrieve('ContextMenu');
					if (trMenu) trMenu.disable();
					return trMenu;
				}).clean();
			} else {
				if (row.hasDataFilter('ContextMenu')) tableMenu.disable();
				//otherwise, if there aren't multiple rows selected, disable the table's menu
				else tableMenu.enable();
			}
		});
	}

});