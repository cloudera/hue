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
description: Adds support for Autocompletion on form inputs.
provides: [Behavior.Autocomplete]
requires: [Widgets/Behavior, clientcide/Autocompleter.Local, clientcide/Autocompleter.Remote]
script: Behavior.Autocomplete.js

...
*/

Behavior.addGlobalFilters({

	/*
		takes elements (inputs) with the data filter "Autocomplete" and creates a autocompletion ui for them
		that either completes against a list of terms supplied as a property of the element (dtaa-autocomplete-tokens)
		or fetches them from a server. In both cases, the tokens must be an array of values. Example:

		<input data-filters="Autocomplete" data-autocomplete-tokens="['foo', 'bar', 'baz']"/>

		Alternately, you can specify a url to submit the current typed token to get back a list of valid values in the
		same format (i.e. a JSON response; an array of strings). Example:

		<input data-filters="Autocomplete" data-autocomplete-url="/some/API/for/autocomplete"/>

		When the values ar fetched from the server, the server is sent the current term (what the user is typing) as
		a post variable "term" as well as the entire contents of the input as "value".

		An additional data property for autocomplete-options can be specified; this must be a JSON encoded string
		of key/value pairs that configure the Autocompleter instance (see documentation for the Autocompleter classes
		online at http://www.clientcide.com/docs/3rdParty/Autocompleter but also available as a markdown file in the
		clientcide repo fetched by hue in the thirdparty directory).

		Note that this JSON string can't include functions as callbacks; if you require amore advanced usage you should
		write your own Behavior filter or filter plugin.

	*/

	Autocomplete: function(element, methods){
		var options = $merge({
			minLength: 1,
			selectMode: 'type-ahead',
			overflow: true,
			selectFirst: true,
			multiple: true,
			separator: ' ',
			allowDupes: true,
			postVar: 'term'
		}, element.getJSONData('autocomplete-options'));

		if (element.getData('autocomplete-url')) {
			var aaj = new Autocompleter.Ajax.Json(element, element.getData('autocomplete-url'), options);
			aaj.addEvent('request', function(el, req, data, value){
				data['value'] = el.get('value');
			});
		} else {
			var tokens = element.getJSONData('autocomplete-tokens');
			if (!tokens) {
				dbug.warn('Could not set up autocompleter; no local tokens found.');
				return;
			}
			new Autocompleter.Local(element, tokens, options);
		}
	}

});
