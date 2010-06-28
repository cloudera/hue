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
description: If any element loaded by JFrame has the css class .no_overflow, the jframe wrapper is set to have an overflow value of 'none'.
provides: [CCS.JFrame.NoOverflow]
requires: [/CCS.JFrame]
script: CCS.JFrame.NoOverflow.js

...
*/


CCS.JFrame.addGlobalFilters({

	noOverflow: function(container){
		//if the container has the class no_overflow, or an element within it has the no_overflow class
		//set the content to have no overflow; you must handle the overflow in your own css/js
		if (container.hasClass('no_overflow') || container.getElement('.no_overflow')) {
			this.element.setStyle('overflow', 'hidden');
		}
	}

});