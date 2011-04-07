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
description: Opens a Hue.FileChooser for any element with the hue-choose_file, hue-choose_dir, or hue-choose_path  class and places the chosen path in the input field whose "name" attribute is equal to the data stored in  the "chooseFor" attribute of the element.
provides: [Hue.JFrame.Chooser, CCS.JFrame.Chooser]
requires: [/Hue.JFrame]
script: Hue.JFrame.Chooser.js
...
*/

;(function(){

var caption = {
	'dir': 'Choose A Directory',
	'file': 'Choose A File',
	'any': 'Choose A Path'
};

var chooser = function(filter){
	return function(e, link){
		//Stop link from its standard action
		e.preventDefault();
		var targetName = link.get('data-chooseFor');
		var jbrowser = this.getWindow();
		var parent = link.getParent('form') || $(jbrowser);
		var targetInput = parent.getElement('input[name=' + targetName + ']');
		//use parent widget to get jbrowser for Hue.chooseFile
		//Hue.chooseFile creates an ART alert which contains a FileChooser from which teh user can select a file.
		//The function argument is the callback which is called after the OK button in the ART alert is clicked.
		Hue.Desktop.load("FileBrowser", function(){
			Hue.chooseFile(jbrowser, '/', caption[filter], function(data){
				targetInput.set('value', data.path);
				targetInput.fireEvent('change');
				//hide overtext on targetInput
				var overtext = targetInput.retrieve('OverText');
				if (overtext) overtext.hide();
			}, {
				filter: filter
			});
		});
	};
};

Hue.JFrame.addGlobalLinkers({
	'.hue-choose_file': chooser('file'),
	'.hue-choose_dir': chooser('dir'),
	'.hue-choose_path': chooser('any'),
	//deprecated
	'.ccs-choose_file': chooser('file'),
	'.ccs-choose_dir': chooser('dir'),
	'.ccs-choose_path': chooser('any')
});

})();
