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
description: Alters classes in Hue to output profiling data.
provides: [Hue.Profiler]
requires: [
  JFrame/JFrame,
  clientcide/dbug,
  Behavior/Behavior,
]
script: Hue.Profiler.js

...
*/

(function(){

	$extend(dbug, {

		//resets the timer values for a given group/name report
		resetReport: function(group, name){
			delete getGroup(group)[name];
		},

		//resets the timer values for all reports in a group
		resetReports: function(group){
			if (group) delete groups[group];
			else groups = {};
		},

		//start a group/name report
		reportStart: function(group, name){
			var report = getReport(group, name);
			if (!report.timer) report.timer = new Date().getTime();
			report.count++;
		},

		//end a group/name report
		reportEnd: function(group, name){
			var report = getReport(group, name);
			if (report.timer){
				var end = new Date().getTime() - report.timer;
				report.timer = null;
				report.duration += end;
			} else dbug.log('no such timer: %s in group %s', group, name || 'defaultGroup');
		},

		//output a current group/name report total
		logReport: function(group, name){
			var report = getReport(group, name);
			dbug.log('%s: count: %s, duration: %s ms', name, report.count, report.duration);
		},

		//log all reports in a given group; optional 2nd argument to reset the report afterwards.
		logAllReports: function(group, reset){
			var grp = getGroup(group);
			dbug.groupCollapsed('~~~~~ profile group: %s ~~~~~~', group || 'defaultGroup');
			for (var name in grp){
				dbug.logReport(group, name);
			}
			var totals = getReportTotals(group);
			dbug.groupEnd('~~~~~ profile group: %s ~~~~~~', group || 'defaultGroup');
			dbug.log('TOTAL TIME: %s: count: %s, duration: %s ms', group, totals.count, totals.duration);
			if (reset) dbug.resetReports(group);
		},

		//enable profiling
		enableProfiler: function(){
			if (!dbug.profileEnabled){
				if (!dbug.enabled) dbug.enable();
				dbug.profileEnabled = true;
				dbug.log('setting profile cookie (reload required)');
				var date = new Date();
				date.setTime(date.getTime()+(24*60*60*1000));
				document.cookie = 'dbugProfile=true;expires='+date.toGMTString()+';path=/;';
			}
		},

		//disable profiling
		disableProfiler: function(){
			dbug.log('disabling debugging cookie (reload required)');
			document.cookie = 'dbugProfile=false;path=/;';
		}

	});

	//on load, enable the profiler if the cookie is present
	var value = document.cookie.match('(?:^|;)\\s*dbugProfile=([^;]*)');
	var profileCookie = value ? unescape(value[1]) : false;
	if (profileCookie) dbug.enableProfiler();

	//if profiling is enalbed, instrument Behavior and JFrame to log their work
	if (dbug.profileEnabled){
		Behavior = Class.refactor(Behavior, {
			apply: function(container, force){
				var result = this.previous.apply(this, arguments);
				dbug.logAllReports('behavior filters', true);
				return result;
			},
			applyFilter: function(element, filter, force){
				dbug.reportStart('behavior filters', filter.name);
				var result = this.previous.apply(this, arguments);
				dbug.reportEnd('behavior filters', filter.name);
				return result;
			}
		});

		JFrame = Class.refactor(JFrame, {

			applyFilters: function(container, content, behavior){
				var result = this.previous.apply(this, arguments);
				dbug.logAllReports('jframe filters', true);
				return result;
			},

			applyFilter: function(name, container, content){
				dbug.reportStart('jframe filters', name);
				var result = this.previous.apply(this, arguments);
				dbug.reportEnd('jframe filters', name);
				return result;
			},

			_applyRenderers: function(){
				var result = this.previous.apply(this, arguments);
				dbug.logAllReports('jframe renderers', true);
				return result;
			},

			_defaultRenderer: function(){
				dbug.reportStart('jframe renderers', 'default renderer');
				var result = this.previous.apply(this, arguments);
				dbug.reportEnd('jframe renderers', 'default renderer');
				return result;
			},

			_applyRenderer: function(name, content){
				dbug.reportStart('jframe renderers', name);
				var result = this.previous.apply(this, arguments);
				dbug.reportEnd('jframe renderers', name);
				return result;
			},

			_empty: function(){
				dbug.time('jframe empty');
				var result = this.previous.apply(this, arguments);
				dbug.timeEnd('jframe empty');
				return result;
			}
		});
	}


	var groups = {};

	//given a group, return its reports
	var getGroup = function(group){
		var grp = groups[group || 'defaultGroup'];
		if (!grp){
			grp = groups[group] = {};
		}
		return grp;
	};

	//given a group/name get its report values
	var getReport = function(group, name){
		var grp = getGroup(group);
		if (!grp[name]){
			grp[name] = {
				duration: 0,
				count: 0,
				timer: null
			};
		}
		return grp[name];
	};

	//given a group, return the total duration and count
	var getReportTotals = function(group){
		var grp = getGroup(group);
		var totals = {
			duration: 0,
			count: 0
		};
		for (var name in grp){
			totals.duration += grp[name].duration;
			totals.count += grp[name].count;
		}
		return totals;
	};

})();