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
description: Updates HtmlTable states when the JFrame contents are updated (via Ajax/partial refresh).
provides: [Behavior.HtmlTableUpdate]
requires: [Widgets/Behavior.HtmlTable]
script: Behavior.HtmlTableUpdate.js
...
*/

Behavior.addGlobalPlugin('HtmlTable', 'HtmlTableUpdate', function(element, methods){
	var table = element.retrieve('HtmlTable');
	var refresh = function(data, options){
		var refresh;
		data.elements.each(function(element){
			if (!refresh && ['td','th','tbody','tr','thead','tfoot'].contains(element.get('tag')) && $(table).hasChild(element)) {
				refresh = true;
			}
		});
		if (refresh) table.refresh();
		$(table).getElements('.table-expanded a.expand').addClass('jframe_ignore');
	};
	methods.addEvent('update', refresh);
	this.markForCleanup(element, function(){
		methods.removeEvent('update', refresh);
	});
});