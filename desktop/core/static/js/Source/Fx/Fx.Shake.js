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
description: Shake effect.
provides: [Fx.Shake]
requires: [Core/Fx.Tween]
script: Fx.Shake.js

...
*/
Fx.Shake = new Class({

	Extends: Fx.Tween,

	options: {
		times: 5
	},

	initialize: function(){
		this.parent.apply(this, arguments);
		if (this.options.property) {
			this.property = this.options.property;
			delete this.options.property;
		}
		this._start = this.start;
		this.start = this.shake;
		this.duration = this.options.duration;
		this.shakeChain = new Chain();
	},

	complete: function(){
		if (!this.shakeChain.$chain.length && this.stopTimer()) this.onComplete();
		else if (this.shakeChain.$chain.length) this.shakeChain.callChain();
		return this;
	},

	shake: function(property, distance, times){
		if (!this.check(arguments.callee, property, distance)) return this;
		var args = Array.link(arguments, {property: String.type, distance: $defined, times: $defined});
		property = this.property || args.property;
		times = args.times || this.options.times;
		this.stepDur = this.duration / (times + 1);
		this._getTransition = this.getTransition;
		this.origin = this.element.getStyle(property).toInt()||0;
		this.shakeChain.chain(
			function(){
				this.shakeChain.chain(
					function() {
							this.stopTimer();
							this.getTransition = this._getTransition;
							this.options.duration = this.stepDur / 2;
							//stage three, return to origin
							this._start(property, this.origin);
					}.bind(this)
				);
				this.getTransition = function(){
					return function(p){
						return (1 + Math.sin( times*p*Math.PI - Math.PI/2 )) / 2;
					}.bind(this);
				}.bind(this);
				this.stopTimer();
				this.options.duration = this.stepDur * times;
				//stage 2: offset to the other side using the shake transition
				this._start(property, this.origin - args.distance);
			}.bind(this)
		);
		this.options.duration = this.stepDur / 2;
		//stage 1: offset to one side
		return this._start(property, this.origin + args.distance);
	},

	onCancel: function(){
		this.parent();
		this.shakeChain.clearChain();
		return this;
	}

});


Element.Properties.shake = {

	set: function(options){
		var shake = this.retrieve('shake');
		if (shake) shake.cancel();
		return this.eliminate('shake').store('shake:options', $extend({link: 'cancel'}, options));
	},

	get: function(options){
		if (options || !this.retrieve('shake')){
			if (options || !this.retrieve('shake:options')) this.set('shake', options);
			this.store('shake', new Fx.Shake(this, this.retrieve('shake:options')));
		}
		return this.retrieve('shake');
	}

};

Element.implement({

	shake: function(property, distance, times, options){
		var args = Array.link(arguments, {property: String.type, distance: Number.type, times: Number.type, options: Object.type});
		if (args.options) this.set('shake', args.options);
		this.get('shake').start(args.property, args.distance, args.times);
		return this;
	}

});
