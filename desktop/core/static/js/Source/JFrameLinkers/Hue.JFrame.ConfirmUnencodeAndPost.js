/*
---
description: Makes all links with the css class .confirm_unencode_and_post un-URL encode the href of a URL, prompt the user and then send the link as a post if they confirm.
provides: [Hue.JFrame.ConfirmUnencodeAndPost]
requires: [JFrame/JFrame]
script: Hue.JFrame.ConfirmUnencodeAndPost.js

...
*/

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

JFrame.addGlobalLinkers({

	'.confirm_unencode_and_post': function(e, link){
		//for each link with the class .confirm_unencode_and_post, confirm with the user,
		//then un-URL encode the query string, and POST the data parsed out.
		//use the link's title for the caption of the popup, and the alt as the body,
		//defaulting to "Confirm" and "Are you sure?" respectively.
		if (e) e.preventDefault();

		var win = this.getWindow();
		var confirmer;
		if (win) confirmer = win.confirm.bind(win);
		else confirmer = ART.confirm;
		var linkParts = link.get('href').split('?');
                var unencodedParams = decodeURIComponent(linkParts[1].replace(/\+/g,' '))
                var unencodedLink = linkParts[0] + '?' + unencodedParams;
		confirmer(link.get('title') || link.retrieve('tip:title') || 'Confirm', link.get('alt') || "Are you sure?", function(){
			this.load({
				requestPath: linkParts[0],
				data: new URI(unencodedLink).get('data'),
				method: 'post',
				skipPostConfirmation: true
			});
		}.bind(this));
	}

});
