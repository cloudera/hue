/*
---
description: DynamicTextarea

license: MIT-style

authors:
- Amadeus Demarzi (http://enmassellc.com/)

requires:
  - More/Element.Measure

provides: [DynamicTextarea]
...
*/

var DynamicTextarea = new Class({
	
	Implements:[Options,Events],
	
	options:
	{
		value:'',
		minRows:1,
		string:'',
		noBreaks:false,
		value:null,
		basic:'default',
		focused:'focused',
		filled:'filled',
		disabled:'disabled',
		timeout:'ready',
		maxLength:Infinity,
		lineHeight:null,
		offset:0,
		ctaClass:''
		// AVAILABLE EVENTS
		// onFocus:$empty,
		// onBlur:$empty,
		// onKeyPress:$empty,
		// onLoad:$empty,
		// onEnable:$empty,
		// onDisable:$empty,
		// onReset:$empty
	},
	
	elements:
	{
		input:null,
		parent:null,
		cta:null
	},
	
	initialize:function(el,options)
	{
		this.setOptions(options);
		this.elements.input = document.id(el);
		if(!this.elements.input) return;
		
		// Firefox handles scroll heights differently than all other browsers
		if(window.Browser.Engine.gecko)
		{
			this.options.offset = parseInt(this.elements.input.getStyle('padding-top'),10)+parseInt(this.elements.input.getStyle('padding-bottom'),10)+parseInt(this.elements.input.getStyle('border-bottom-width'),10)+parseInt(this.elements.input.getStyle('border-top-width'),10);
			this.options.padding = 0;
		}
		else
		{
			this.options.offset = parseInt(this.elements.input.getStyle('border-bottom-width'),10)+parseInt(this.elements.input.getStyle('border-top-width'),10);
			this.options.padding = parseInt(this.elements.input.getStyle('padding-top'),10)+parseInt(this.elements.input.getStyle('padding-bottom'),10);
		}
		
		this.elements.parent = this.elements.input.getParent();
		if(this.options.string!='' && window.OverText)
		{
			this.elements.cta = new OverText(this.elements.input,{
				textOverride:this.options.string,
				labelClass:this.options.ctaClass
			});
		}
		
		var backupString = '';
		if(this.elements.input.value=='') this.elements.parent.addClass(this.options.basic);
		else
		{
			backupString = this.elements.input.value;
			this.elements.parent.addClass(this.options.filled);
		}
		
		this.elements.input.set({
			'rows':1,
			'styles':
			{
				'resize':'none', // Disable webkit resize handle
				'position':'relative',
				'display':'block',
				'overflow':'hidden',
				'height':'auto'
			}
		});
		
		// This is the only crossbrowser method to determine scrollheight of a single line in a textarea
		this.elements.input.value = 'M';
		this.options.lineHeight = (this.elements.input.measure(function(){ return this.getScrollSize().y; }))-this.options.padding;
		this.elements.input.value = backupString;
		this.elements.input.setStyle('height',this.options.lineHeight*this.options.minRows);
		
		// Prebind common methods - I prefer to not require MooTools More Bind, so I am doing it manually
		this.focus = this.focus.bind(this);
		this.delayStart = this.delayStart.bindWithEvent(this);
		this.delayStart = this.delayStart.bindWithEvent(this);
		this.blur = this.blur.bind(this);
		this.scrollFix = this.scrollFix.bind(this);
		this.checkSize = this.checkSize.bind(this);
		this.clean = this.clean.bind(this);
		this.disable = this.disable.bind(this);
		this.enable = this.enable.bind(this);
		
		// Set the height of the textarea, based on content
		this.checkSize(true);
		this.elements.input.addEvent('focus',this.focus);
		this.fireEvent('load');
	},
	
	// For Safari (mostly), stops a small jump on textarea resize
	scrollFix: function(){ this.elements.input.scrollTo(0,0); },
	
	// Sets up textarea to be interactive, and calls focus event
	focus:function()
	{
		this.elements.parent.removeClass(this.options.basic);
		this.elements.parent.removeClass(this.options.filled);
		this.elements.parent.addClass(this.options.focused);
		
		this.elements.input.addEvents({
			'keydown':this.delayStart,
			'keypress':this.delayStart,
			'blur':this.blur,
			'scroll':this.scrollFix
		});
		this.fireEvent('focus');
	},
	
	// Set's appropriate blur classes and calls user binded blur
	blur:function()
	{
		this.elements.parent.removeClass(this.options.focused);
		if(this.elements.input.value=='') this.elements.parent.addClass(this.options.basic);
		else this.elements.parent.addClass(this.options.filled);
		
		this.elements.input.removeEvents({
			'keydown':this.delayStart,
			'keypress':this.delayStart,
			'blur':this.blur,
			'scroll':this.scrollFix
		});
		
		this.fireEvent('blur');
	},
	
	// Delay start of check because text hasn't been injected into the textarea yet
	delayStart:function(e)
	{
		if(this.options.timeout=='ready' && this.options.value.length<this.options.maxLength)
		{
			this.options.timeout = setTimeout(this.checkSize,1);
			return;
		}
		if(
			(this.options.maxLength &&
			this.options.maxLength!=null &&
			this.options.value.length>=this.options.maxLength &&
			e.key!='backspace' &&
			e.key!='delete' &&
			e.meta==false &&
			e.control==false &&
			e.shift==false &&
			e.key!='up' &&
			e.key!='down' &&
			e.key!='left' &&
			e.key!='tab' &&
			e.key!='right') || (this.options.noBreaks==true && (e.key=='enter' || e.key=='return')))
		{
			e.preventDefault();
			return;
		}
		if(this.options.timeout=='ready') this.options.timeout = setTimeout(this.checkSize,1);
	},
	
	// Set text area to smallest size, and begin adjusting size
	checkSize: function(manual)
	{
		var oldVal = this.options.value;
		
		this.options.value = this.elements.input.value;
		this.options.timeout = 0;
		
		if(this.options.value==oldVal && manual!=true)
		{
			this.options.timeout = 'ready';
			return;
		}
		
		if(oldVal==null || this.options.value.length<oldVal.length)
		{
			this.elements.parent.setStyle('height',this.elements.parent.getSize().y);
			this.elements.input.setStyle('height',this.options.minRows*this.options.lineHeight);
		}
		
		var tempHeight = this.elements.input.getScrollSize().y;
		var offsetHeight = this.elements.input.offsetHeight;
		var cssHeight = tempHeight-this.options.padding;
		var scrollHeight = tempHeight+this.options.offset;
		if(scrollHeight!=offsetHeight && cssHeight>this.options.minRows*this.options.lineHeight) this.elements.input.setStyle('height',cssHeight);
		
		this.elements.parent.setStyle('height','auto');
		this.options.timeout = 'ready';
		if(manual!=true) this.fireEvent('keyPress');
	},
	
	// Reset the text area to blank
	reset:function()
	{
		this.elements.input.value = '';
		this.checkSize(true);
		this.elements.parent.removeClass(this.options.filled);
		this.elements.parent.removeClass(this.options.focused);
		this.elements.parent.addClass(this.options.basic);
		
		this.fireEvent('reset');
	},
	
	// Sets the caret to the desired position
	setCaret:function(pos)
	{
		// Standard Browsers
		if (!document.selection)
		{ 
			this.elements.input.selectionStart = pos;
			this.elements.input.selectionEnd = pos;
		}
		// For IE
		else
		{
			var sel = document.selection.createRange();
			sel.moveStart('character', -this.elements.input.value.length);
			sel.moveStart('character', pos);
			sel.moveEnd('character', 0);
			sel.select();
		}
	},
	
	// Clean out this textarea's event handlers
	clean:function()
	{
		this.elements.input.removeEvents({
			'focus':this.focus,
			'keydown':this.delayStart,
			'keypress':this.delayStart,
			'blur':this.blur,
			'scroll':this.scrollFix
		});
	},
	
	// Disable input for the textarea
	disable:function()
	{   
		this.elements.input.blur();
		this.elements.input.removeEvents({
			'focus':this.focus,
			'keydown':this.delayStart,
			'keypress':this.delayStart,
			'blur':this.blur,
			'scroll':this.scrollFix
		});
		this.elements.input.set(this.options.disabled,true);
		this.elements.parent.addClass(this.options.disabled);
		this.fireEvent('disable');
	},
	
	// Enable input for the textarea
	enable:function()
	{
		this.elements.input.addEvents({
			'focus':this.focus,
			'scroll':this.scrollFix
		});
		this.elements.input.set(this.options.disabled,false);
		this.elements.parent.removeClass(this.options.disabled);
		this.fireEvent('enable');
	}
});