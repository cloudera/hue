/*
---

script: FitText.js

description: Truncates the text nodes of elements to fit inside a container

license: MIT-style license.

authors: Ryan Florence <http://ryanflorence.com>

docs: http://moodocs.net/rpflo/mootools-rpflo/FitText

requires:
- Core/Element
- Core/Options
- Core/Events
- Core/Array.each

provides: [FitText]

...
*/



var FitText = new Class({
  
	Implements: Options,
  
		options: {
			offset: 10,
			fitClass: 'truncated'
		},
  
	initialize: function(container, elements, options){
		this.setOptions(options);
		this.container = document.id(container);
		this.elements = $$(elements);
		this.bound = this.fit.bind(this);
		
		this.elements.each(function(element){
			element.store('scrollWidth',element.getSize().x).store('text',element.get('text')).store('FitText', this);
		}, this);

		this.attach();
		this.fit();
	},
 
	fit: function(){
		var contentWidth = this.container.getSize().x-this.options.offset;
		this.elements.each(function(element,index){
			var scrollWidth = element.retrieve('scrollWidth');
			var text = element.retrieve('text');
			if(scrollWidth > contentWidth){
				element.addClass(this.options.fitClass);
				var length = ((text.length*(contentWidth/scrollWidth))/2).round();
				var truncatedText = text.substr(0,length) + '...' + text.substr(-length+6);
				element.set('text',truncatedText);
			} else if(element.hasClass(this.options.fitClass)){
				element.removeClass(this.options.fitClass);
				element.set('text',text);
			}
		}, this);

		return this;
	},

	attach: function(){
		window.addEvent('resize',this.bound);
		return this;
  },

	detach: function(){
		window.removeEvent('resize',this.bound);
		return this;
	},
	
	reset: function(){
		this.elements.each(function(element){
			element.removeClass(this.options.fitClass).set('text',element.retrieve('text'));
		}.bind(this));
		return this;
	}

});