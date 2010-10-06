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
description: Provides functionality for links that update the window path on the fly.
provides: [CCS.JFrame.LivePath]
requires: [/CCS.JFrame]
script: CCS.JFrame.LivePath.js
...
*/

(function(){

	CCS.JFrame.addGlobalLinkers({

		'[data-livepath-toggle]': function(event, link){
			this.currentPath = updateLivePath(link, this.currentPath);
		},
		//these are a bit silly, but mootools 1.2 selector engine doesn't support
		//complex selectors for element.match, so we have to do a bit of repetition here
		'[data-livepath-add]': function(event, link){
			this.currentPath = updateLivePath(link, this.currentPath);
		},
		'[data-livepath-remove]': function(event, link){
			this.currentPath = updateLivePath(link, this.currentPath);
		}

	});

	var updateLivePath = function(link, currentPath){
		var setData = function(uri, paths, action){
			var okToRemove = action == "toggle" || action == "remove";
			var okToAdd = action == "toggle" || action == "add";
			for (path in paths){
				var state = uri.getData(path);
				if (window.paused) debugger;
				if (!state) {
					uri.setData(path, paths[path]);
				} else if ($type(state) == "string") {
					if (state == paths[path] && okToRemove)
						uri.setData(path, null);
					else if (okToAdd)
						uri.setData(path, [state, paths[path]]);
				} else if ($type(state) == "array") {
					if (state.contains(paths[path]) && okToRemove) state.erase(paths[path]);
					else if (okToAdd) state.push(paths[path]);

					if (state.length) uri.setData(path, state);
					else uri.clearData(path);
				}
			}
		};
		var toggle = link.get('data', 'livepath-toggle'),
		    add = link.get('data', 'livepath-add'),
		    remove = link.get('data', 'livepath-remove'),
		    uri = new URI(currentPath);
		if (toggle) {
			toggle = toggle.parseQueryString();
			setData(uri, toggle, 'toggle');
		} else if (add) {
			add = add.parseQueryString();
			setData(uri, add, 'add');
		} else if (remove) {
			remove = remove.parseQueryString();
			setData(uri, remove, 'toggle');
		}
		return uri.toString();
	};

})();