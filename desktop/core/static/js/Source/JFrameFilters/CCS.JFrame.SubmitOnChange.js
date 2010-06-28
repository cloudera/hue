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
description: Makes any form with the css class .submit_on_change submit itself whenever any input is changed.
provides: [CCS.JFrame.SubmitOnChange]
requires: [/CCS.JFrame]
script: CCS.JFrame.SubmitOnChange.js

...
*/


CCS.JFrame.addGlobalFilters({

	submitOnChange: function(container) {
		container.getElements('form.submit_on_change').each(function(form) {
			form.getElements('input, select, textarea').each(function(input){
				input.addEvents({
					change: function(e){
						if (e) form.fireEvent('submit', e);
						else form.fireEvent('submit');
					},
					keydown: function(e) {
						if (e.key == 'enter') form.fireEvent('submit', e);
					}
				});
			});
		});
	}

});