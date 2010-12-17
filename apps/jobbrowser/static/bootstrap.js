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
Hue.Desktop.register({
	JobBrowser: {
		name: 'Job Browser',
		css: '/jobbrowser/static/css/jobbrowser.css',
		require: ["jobbrowser/Hue.JobBrowser"],
		launch: function(path, options){
			return new Hue.JobBrowser(path, options);
		},
		menu: {
			id: 'hue-jobbrowser-menu',
			img: {
				src: '/jobbrowser/static/art/jobbrowser-small.png'
			}
		},
		help: '/help/jobbrowser/'
	}
});
Depender.require({
	scripts: ["Hue.JobBrowser.Poller"],
	callback: function(){
		if (Cookie.read('activateJobsPoller') != "false") Hue.User.withUser(Hue.Dock.startJobsPoll);
		else Hue.Dock.statusContent.set('html', 'poller paused');
	}
});
