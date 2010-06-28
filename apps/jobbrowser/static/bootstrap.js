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
CCS.Desktop.register({
	JobBrowser: {
		name: 'Job Browser',
		css: '/jobbrowser/static/css/jobbrowser.css',
		require: ["CCS.JobBrowser"],
		launch: function(path, options){
			return new CCS.JobBrowser(path, options);
		},
		menu: {
			id: 'ccs-jobbrowser-menu',
			img: {
				src: '/jobbrowser/static/art/jobbrowser-small.png'
			}
		},
		help: '/help/jobbrowser/'
	}
});
Depender.require({
	scripts: ["CCS.JobBrowser.Poller"],
	callback: function(){
		if (Cookie.read('activateJobsPoller') != "false") CCS.User.withUser(CCS.Dock.startJobsPoll);
		else CCS.Dock.statusContent.set('html', 'poller paused');
	}
});
