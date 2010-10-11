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
description: Adds a timer that counts forward from zero or a given value.
provides: [Behavior.Timer]
requires: [Widgets/Behavior, More/Date.Extras]
script: Behavior.Timer.js

...
*/

Behavior.addGlobalFilters({

	Timer: function(element, methods){
		var start = element.getData('start-time');
		if (start) start = Date.parse(start);
		else start = new Date();
		var timer = (function(){
			var now = new Date();
			var diff = start.diff(now, 'second');
			if (diff > 60) element.set('html', start.timeDiffInWords());
			else element.set('html', diff + ' sec');
		}).periodical(100);
		this.markForCleanup(element, function(){
			$clear(timer);
		});
	}

});