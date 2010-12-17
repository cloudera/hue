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
description: Adds polling functionality to the dock for JobBrowser
provides: [Hue.JobBrowser.Poller]
requires: [hue-shared/Hue.Dock, Core/Request.HTML, clientcide/dbug, Core/Element.Event, Core/Cookie]
script: Hue.JobBrowser.Poller.js

...
*/

if (!Hue.Dock) {
	dbug.warn('could not set up the jobs poller; Hue.Dock is not defined');
} else {
	//adding a hidden ability to toggle the job poller
	//the console statements for the ajax requests are distracting
	$('hue-dock-status').addEvent('dblclick', function(){
		Hue.Dock[Hue.Dock.pollingJobs ? 'stopJobsPoll' : 'startJobsPoll']();
		Cookie.write('activateJobsPoller', Hue.Dock.pollingJobs);
		if (!Hue.Dock.pollingJobs) Hue.Dock.statusContent.set('html', 'poller paused');
	});
	//poll for new jobs from the job tracker
	//when the status notes are clicked, launch a Job Browser instance with that view
	Hue.Dock.statusContent.addEvents({
		'click:relay(a)': function(e, a){
			e.preventDefault();
			Hue.Desktop.launch(a.get('target'), [a.get('href')]);
		}
	});
	

	$extend(Hue.Dock, {
		/*
			loads the job data into the dock
		*/
		loadJobs: function(){
			if (Hue.Dock.pollingJobs) {
				Hue.Dock.statusContent.set('load', {
					onHueError: Hue.Dock.stopJobsPoll,
					onFailure: Hue.Dock.stopJobsPoll,
					onSuccess: Hue.Dock.loadJobs.delay(5000),
					url: '/status_bar/'
				}).load();
			}
		},
		startJobsPoll: function(){
			dbug.log('starting job poller');
			Hue.Dock.pollingJobs = true;
			Hue.Dock.loadJobs();
		},
		stopJobsPoll: function(){
			dbug.log('stopping job poller');
			Hue.Dock.statusContent.set('html', 'poller paused');
			Hue.Dock.pollingJobs = false;
		}	
	});
	//whenever our poller gets an error, just stop polling
	Hue.Dock.statusContent.get('load').addEvent('hueError', Hue.Dock.stopJobsPoll);
}
