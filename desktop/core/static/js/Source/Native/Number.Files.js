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
description: Extends Number to understand unix permissions scheme.
provides: [Number.Files]
requires: [Core/Number]
script: Number.Files.js

...
*/
//permission parser
Number.implement({
	parsePermissions: function() {
		var perms = {};
		$H({
			user_read: 0400,
			user_write: 0200,
			user_execute: 0100,
			group_read: 0040,
			group_write: 0020,
			group_execute: 0010,
			other_read: 0004,
			other_write: 0002,
			other_execute: 0001
		}).each(function(value, key) {
			perms[key] = !!(this & value);
		}, this);
		return perms;
	},
	convertFileSize: function() {
		if (this < 1024*2) return this + ' B';
		if (this < 1048576) return (this/1024).round(1) + ' KB';
		if (this < 1073741824) return (this/1048576).round(1) + ' MB';
		if (this < 1099511627776) return (this/1073741824).round(1) + ' GB';
		if (this < (1099511627776*1024)) return (this/1099511627776).round(1) + ' TB';
		return (this/(1099511627776*1024)).round(1) + ' PB'; //hey, it could happen
	},
	
	//From: http://snipplr.com/view/7345/format-number-with-commas-every-3-decimal-places/
	convertWithCommas: function(){
		var pieces = this.toString().split('.');
		var p1 = pieces[0];
		var p2 = pieces.length > 1 ? '.' + pieces[1] : '';
		var regex = /(\d+)(\d{3})/;
		while (regex.test(p1)) {
			p1 = p1.replace(regex, '$1' + ',' + '$2');
		}
		return p1 + p2;
	}
});
