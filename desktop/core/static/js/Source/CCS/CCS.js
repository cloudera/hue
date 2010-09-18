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
description: CCS Configuration Options
provides: [CCS]
requires: [clientcide/StickyWin, Widgets/ART.Popup, Core/Element.Event, Core/Request.HTML,
  More/Spinner, Core/Selectors]
script: CCS.js

...
*/
var CCS = new Events();
/* config */
Request.implement({
	options: {
		evalScripts: true,
		noCache: true
	}
});
Spinner.implement({
	options: {
		fxOptions: {
			link: 'cancel'
		}
	}
});

Hash.implement({
	//implements the ability to serialize arrays into query strings without brackets
	//foo[0]=bar&foo[1]=baz
	//vs
	//foo=bar&foo=baz
	toQueryString: function(base, useBrackets){
		useBrackets = useBrackets == null ? true : useBrackets;
		var queryString = [];
		Hash.each(this, function(value, key){
			if (base && useBrackets) key = base + '[' + key + ']';
			var result;
			switch ($type(value)){
				case 'object': result = Hash.toQueryString(value, key); break;
				case 'array':
					if (useBrackets) {
						var qs = {};
						value.each(function(val, i){
							qs[i] = val;
						});
						result = Hash.toQueryString(qs, key);
					} else {
						result = value.map(function(val){
							return key + '=' + encodeURIComponent(val);
						}).join('&');
					}
				break;
				default: result = key + '=' + encodeURIComponent(value);
			}
			if (value != undefined) queryString.push(result);
		});
		return queryString.join('&');
	}
});

URI.implement({

	options: {
		useBrackets: false
	},

	setData: function(values, merge, part){
		if (typeof values == 'string'){
			data = this.getData();
			data[arguments[0]] = arguments[1];
			values = data;
		} else if (merge) {
			values = $merge(this.getData(), values);
		}
		return this.set(part || 'query', Hash.toQueryString(values, null, this.options.useBrackets));
	}

});

Element.Events.esc = {
	base: 'keydown', //we set a base type
	condition: function(event){ //and a function to perform additional checks.
		return (event.escape == true); //this means the event is free to fire
	}
};
StickyWin.implement({
	options: {
		destroyOnClose: true,
		allowNegative: false
	}
});
ART.Popup.implement({
	options: {
		destroyOnClose: true,
		allowNegative: false,
		posMin: {x: 0, y: 0}
	}
});
StickyWin.Stacker.implement({
	options: {
		zIndexBase: 10003
	}
});
StickyWin.WM.setOptions({
	zIndexBase: 10003
});

//allows for selectors like $$('[data-foo-bar]'); TODO: move this up at some point. Note that it'll be in Moo 1.3
// Selectors.RegExps.combined = (/\.([\w-]+)|\[([\w-]+)(?:([!*^$~|]?=)(["']?)([^\4]*?)\4)?\]|:([\w-]+)(?:\(["']?(.*?)?["']?\)|$)/g);
