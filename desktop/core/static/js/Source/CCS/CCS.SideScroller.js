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
description: Side Scroller
provides: [CCS.SideScroller]
requires: [More/Fx.Elements, More/Element.Shortcuts]
script: CCS.SideScroller.js

...
*/
CCS.SideScroller = new Class({
	Implements: [Options, Events, Chain],
	options: {
		/*
		onStart: $empty(currentIndex, currentSlide, toIndex, toSlide),
		onComplete: $empty(index, slide),
		filter: null,
		slideWidth: null,
		*/
		activeClass: 'active',
		slides: []
	},
	initialize: function(container, options) {
		this.element = $(container);
		this.setOptions(options);
		this.slideNames = $H();
		if (!this.options.slides.length) {
			var slides = this.element.getChildren(this.options.filter);
			if (slides) slides.each(function(slide) {
				this.addSlide(slide, slide.get('id'));
			}, this);
		} else {
			this.options.slides.each(function(slide){
				this.addSlide.apply(this, $splat(slide));
			}, this);
		}
		this.slide(0, false);
		this.fx = new Fx.Elements([], {
			link: 'cancel',
			transition: 'expo:in:out',
			onComplete: function(){
				this.fireEvent('complete', [this.current, this.slides[this.current]]);
			}.bind(this)
		});
		this.internalChain = new Chain();
	},
	toElement: function(){
		return this.element;
	},
	slides: [],
	current: 0,

	getSlide: function(slide) {
		switch($type(slide)) {
			case 'number': 
				return this.slides[slide];
			case 'string': 
				return this.slideNames[slide];
			default: return slide;
		}
	},

	getSlideName: function(slide) {
		slide = this.getSlide(slide);
		return this.slideNames.keyOf(slide);
	},

	getCurrent: function(type){
		switch(type) {
			case 'name': return this.getSlideName(this.current);
			case 'number': return this.current;
			case 'element': return this.slides[this.current];
		} 
	},

	addSlide: function(slide, name){
		slide = $(slide);
		this.element.adopt(slide);
		this.slides.include(slide);
		if (name) this.slideNames[name] = slide;
		if(this.current != null && this.slides.indexOf(slide) != this.current) slide.hide();
		return this;
	},
	removeSlide: function(slide) {
		slide = this.getSlide(slide);
		if (!slide) return this;
		if (this.current == this.slides.indexOf(slide) && this.slides.length > 1) {
			this.internalChain.chain(function(){
				this.removeSlide(slide);
			}.bind(this));
			this[this.current == 0 ? 'slideForward' : 'slideBack']();
		} else {
			this.slides.erase(slide);
			slide.dispose();
		}
		return this;
	},
	getWidth: function(slide, subMargins){
		subMargins = $pick(subMargins, true);
		if (this.options.slideWidth) return this.options.slideWidth;
		var x = this.element.getSize().x;
		if (!subMargins) return x;
		var calc = function(w, i) {
			if (i%2) x = x - w.toInt();
		};
		slide.measure(function(){
			slide.getStyle('padding').split(' ').each(calc);
			slide.getStyle('margin').split(' ').each(calc);
		});
		return x;
	},
	slide: function(slide, useFx) {
		var current = this.slides[this.current||0];
		var next = this.getSlide(slide);	
		if (next == current) return;
		var index = this.slides.indexOf(next);
		this.fireEvent('start', [this.current, current, index, next]);
		next.addClass(this.options.activeClass);
		if (current) current.removeClass(this.options.activeClass);

		this.fx.elements = this.fx.subject = [current, next];
		var dir = index > (this.current||0) ? 'forward' : 'back';
		if ($pick(useFx, true)) {
			var width = this.getWidth(next, false);
			var overflow = this.element.getStyle('overflow');

			current.setStyles({
				position: 'absolute',
				top: 0
			});

			next.setStyles({
				left: dir == 'forward' ? width : -width,
				position: 'relative',
				display: 'block'
			});

			this.element.setStyle('overflow', 'visible');

			this.fx.start({
				'0': {
					left: dir == 'forward' ? -width : width
				},
				'1': {
					left: 0
				}
			}).chain(function(){
				current.setStyles({
					display: 'none',
					position: 'relative',
					left: 0
				});
				this.element.setStyles({
					overflow: overflow || 'visible'
				});
				next.setStyles({
					position: 'relative',
					width: 'auto'
				});
				this.callChain();
				this.internalChain.callChain();
			}.bind(this));
		} else {
			current.hide();
			next.show();
			this.scroller.fireEvent('complete', [this.current, this.slides[this.current]]);
			this.callChain();
			this.internalChain.callChain();
		}
		this.current = index;
		return this;
	},
	slideForward: function(){
		if (this.slides[this.current + 1]) this.slide(this.current + 1);
		return this;
	},
	slideBack: function(){
		if (this.current > 0) this.slide(this.current - 1);
		return this;
	}
});
