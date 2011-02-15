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
description: Hue namespace, (deprecated) Hue namespace + the base requirements for loading the Hue.
provides: [Hue, CCS]
requires: [
  JFrame/JFrame.Browser
]
script: Hue.js

...
*/
var Hue = CCS = new Events();

JFrame.Browser.implement({

	options: {
		help: function(){
			var help = $(this).getElement('a[target=Help].help');
			Hue.Desktop.showHelp(this, help ? help.get('href') : null);
		},
		link: function(){
			this.prompt('Application Location', '<input type="text" style="width:350px" name="path" value="' + new URI(this.jframe.currentPath).toString() + '">', function(newPath){
				this.load({requestPath: unescape(newPath.split('path=')[1]) });
			}.bind(this), {
				onShow: function(){
					var input = $(this).getElement('input').addEvent('focus', function(){
						this.select();
					});
					input.select.delay(100, input);
				}
			});
		}
	}

});

Hue.error = JFrame.error;