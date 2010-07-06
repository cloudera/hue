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
description: Inputs.
provides: [CCS.JFrame.Input]
requires: [/CCS.JFrame]
script: CCS.JFrame.Input.js

...
*/
(function(){

var re = /ccs-search|ccs-input/;

CCS.JFrame.addGlobalFilters({

	artInputs: function(container) {
		if (!container.get('html').match(re)) return;
		container.getElements('.ccs-search, .ccs-input').each(function(input){
			dbug.warn('you are using a deprecated JFrame filter (ccs-search or ccs-input) on %o, use the ArtInput data-filter instead.', input);
			input.addDataFilter('ArtInput');
			if (input.hasClass('ccs-search')) input.set('data', 'art-input-type', 'search');
		}, this);
	}

});

})();