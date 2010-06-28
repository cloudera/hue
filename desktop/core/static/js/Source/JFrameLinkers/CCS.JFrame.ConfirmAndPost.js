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
description: Makes all links with the css class .confirm_and_post prompt the user and then send the link url as a post if they confirm.
provides: [CCS.JFrame.ConfirmAndPost]
requires: [/CCS.JFrame, Widgets/ART.Alerts]
script: CCS.JFrame.ConfirmAndPost.js

...
*/

CCS.JFrame.addGlobalLinkers({

	'.confirm_and_post': function(e, link){
		//for each link with the class .confirm_and_post, confirm with the user and then post the url
		//use the link's title for the caption of the popup, and the alt as the body, 
		//defaulting to "Confirm" and "Are you sure?" respectively.
		if (e) e.preventDefault();
		
		var win = this.getWindow();
		var confirmer;
		if (win) confirmer = win.confirm.bind(win);
		else confirmer = ART.confirm;
		confirmer(link.get('title') || link.retrieve('tip:title') || 'Confirm', link.get('alt') || "Are you sure?", function(){
			this.load({
				requestPath: link.get('href').split('?')[0],
				data: new URI(link.get('href')).get('data'),
				method: 'post'
			});
		}.bind(this));
	}

});