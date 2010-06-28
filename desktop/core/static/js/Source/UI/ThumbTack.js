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
description: ThumbTack
provides: [ThumbTack]
requires: [More/Fx.Move, More/Class.Occlude, More/Class.Binds]
script: ThumbTack.js

...
*/
var ThumbTack = new Class({

	Implements: [Options, Class.Occlude],
	
	Binds: ['position'],
	
	property: 'thumbTack',
	
	options: {
	//	destination: {},
	//	fxOptions: {},
		events: ['resize']
	},
	
	initialize: function(element, options) {
		this.element = $(element);
		if (this.occlude()) return this.occluded;
		this.setOptions(options);
		this.element.set('move', this.options.fxOptions);
		this.attach();
	},

	attach: function(detach){
		this.options.events.each(function(event) {
			window[detach ? 'removeEvent' : 'addEvent'](event, this.position);
		}, this);
		return this;
	},

	detach: function(){
		if (this.element) this.element.get('move').cancel();
		return this.attach(true);
	},

	position: function(destination){
		if (!this.element) return this.detach();
		this.element.move(destination || this.options.destination);
		return this;
	}

});
