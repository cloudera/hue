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
provides: [CCS.JobBrowser.Poller]
requires: [ccs-shared/CCS.Dock, Core/Request.HTML, clientcide/dbug, Core/Element.Event, Core/Cookie]
script: CCS.JobBrowser.Poller.js

...
*/

if (!CCS.Dock) {
	dbug.warn('could not set up the jobs poller; CCS.Dock is not defined');
} else {
	//adding a hidden ability to toggle the job poller
	//the console statements for the ajax requests are distracting
	$('ccs-dock-status').addEvent('dblclick', function(){
		CCS.Dock[CCS.Dock.pollingJobs ? 'stopJobsPoll' : 'startJobsPoll']();
		Cookie.write('activateJobsPoller', CCS.Dock.pollingJobs);
		if (!CCS.Dock.pollingJobs) CCS.Dock.statusContent.set('html', 'poller paused');
	});
	//poll for new jobs from the job tracker
	//when the status notes are clicked, launch a Job Browser instance with that view
	CCS.Dock.statusContent.addEvents({
		'click:relay(a)': function(e, a){
			e.preventDefault();
			CCS.Desktop.launch(a.get('target'), [a.get('href')]);
		}
	});
	

	$extend(CCS.Dock, {
		/*
			loads the job data into the dock
		*/
		loadJobs: function(){
			if (CCS.Dock.pollingJobs) {
				CCS.Dock.statusContent.set('load', {
					onCcsError: CCS.Dock.stopJobsPoll,
					onFailure: CCS.Dock.stopJobsPoll,
					onSuccess: CCS.Dock.loadJobs.delay(5000),
					url: '/status_bar/'
				}).load();
			}
		},
		startJobsPoll: function(){
			dbug.log('starting job poller');
			CCS.Dock.pollingJobs = true;
			CCS.Dock.loadJobs();
		},
		stopJobsPoll: function(){
			dbug.log('stopping job poller');
			CCS.Dock.statusContent.set('html', 'poller paused');
			CCS.Dock.pollingJobs = false;
		}	
	});
	//whenever our poller gets an error, just stop polling
	CCS.Dock.statusContent.get('load').addEvent('ccsError', CCS.Dock.stopJobsPoll);
}
