
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
description: Converts any element with the class '.ccs-art_button' into an ART button widget.
provides: [CCS.JFrame.ArtButtons]
requires: [/CCS.JFrame, Widgets/ART.Button, /Element.Data]
script: CCS.JFrame.ArtButtons.js

...
*/

CCS.JFrame.addGlobalFilters({

	artButtons: function(container) {
		if (!container.get('html').contains('ccs-art_button')) return;
		var buttonSelector = 'a.ccs-art_button, button.ccs-art_button, input.ccs-art_button';
		container.getElements('.ccs-button_bar, .ccs-button_subbar_above, .ccs-button_subbar_below').each(function(bar) {
			var above = bar.hasClass('ccs-button_subbar_above');
			var below = bar.hasClass('ccs-button_subbar_below');
			dbug.warn('you are using a deprecated JFrame filter (ccs-button_bar) on %o, use the ArtButtonBar data-filter instead.', bar);
			bar.addDataFilter('ArtButtonBar');
			if (above) bar.set('data', 'bar-position', 'above');
			if (below) bar.set('data', 'bar-position', 'below');
		}, this);

		container.getElements(buttonSelector).each(function(button){
			dbug.warn('you are using a deprecated JFrame filter (ccs-art_button) on %o, use the ArtButton data-filter instead.', button);
			button.addDataFilter('ArtButton');
		}, this);
	}

});