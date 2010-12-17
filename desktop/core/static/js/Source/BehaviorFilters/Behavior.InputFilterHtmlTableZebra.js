// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.	See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.	 Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.	You may obtain a copy of the License at
//
//		 http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/*
---
description: Makes form validator instances scroll the jframe to the errors.
provides: [Behavior.InputFilterHtmlTableZebra]
requires: [/Behavior.FilterInput]
script: Behavior.InputFilterHtmlTableZebra.js
...
*/

Behavior.addGlobalPlugin('FilterInput', 'InputFilterHtmlTableZebra', function(element, behaviorAPI){
	var update = function(parents){
		if (parents.keys.length) {
			var table = parents.keys[0].getParent('table[data-filters*=HtmlTable]');
			if (table && table.retrieve('HtmlTable')) table.retrieve('HtmlTable').updateZebras();
		}
	}
	element.addEvent('filter', update);
	this.markForCleanup(element, function(){
		element.removeEvent('filter', update);
	});
});
