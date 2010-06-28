
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
description: Converts any element with the class '.ccs-art_button' into an ART button widget.
provides: [CCS.JFrame.ArtButtons]
requires: [/CCS.JFrame, Widgets/ART.Button, /Element.Data]
script: CCS.JFrame.ArtButtons.js

...
*/
(function(){
	var button = {
		'height': 19,
		'width': 22,
		'padding': [0, 0, 0, 0],
		'float': 'left',
		'marginLeft': -1,
		'corner-radius-top-right': 4,
		'corner-radius-bottom-right': 4,
		'corner-radius-top-left': 0,
		'corner-radius-bottom-left': 0,
		'glyph': ART.Glyphs.refresh,
		'glyph-stroke': 0,
		'glyph-fill': true,
		'glyph-height': 12,
		'glyph-width': 12,
		'glyph-top': 4,
		'glyph-left': 5
	};
	var large = {
		'height': 24,
		'width': 24,
		'glyph-top': 6,
		'glyph-left': 6
	};
	ART.Sheet.define('button.art.ccs-refresh', button);
	ART.Sheet.define('button.art.ccs-refresh.large', large);
	button.glyph = ART.Glyphs.triangleLeft;
	button['glyph-top'] = 5;
	button['glyph-left'] = 6;
	ART.Sheet.define('button.art.ccs-back', button);
	ART.Sheet.define('button.art.ccs-back.large', large);
	button.glyph = ART.Glyphs.triangleRight;
	button['glyph-left'] = 8;
	ART.Sheet.define('button.art.ccs-next', button);
	ART.Sheet.define('button.art.ccs-next.large', large);
})();
ART.Sheet.define('button.art.selected', {
	'font-color': hsb(50, 100, 10),
	'glyph-color': hsb(0, 0, 0, 0.8),
	'background-color': [hsb(210, 30, 100), hsb(210, 40, 80)],
	'reflection-color': [hsb(0, 0, 100, 1), hsb(0, 0, 0, 0)],
	'border-color': hsb(0, 0, 0, 0.8)
});

ART.Button.Icon = new Class({

	Extends: ART.Button,

	options: {
		//icon - the properties passed to the element constructor for the icon div
		icon: null
	},

	initialize: function(options){
		this.parent(options);
		if (this.options.icon) {
			this.iconDiv = new Element('div', this.options.icon);
			this.iconDiv.inject($(this));
		}
	}

});


CCS.JFrame.addGlobalFilters({

	/*
		auto-magic art buttons from links and buttons. 
		By default, the button is just rendered as a button with text in it, but it is possible to have an icon image.
		
		To have an icon, style the element with a background image as normal and specify the padding to accomodate that image as normal.
		You must also specify at the very least a width and height in the data-icon-styles property, but you can, if you like, also specify
		other styles for the image, including top and left offsets (these default to 4px). Here's a simple example (it's not required that you
		style it inline).

			<a class="ccs-art_button" href="/jframegallery/" style="background: url(/static/art/info.png) left 50%; padding: 6px 6px 6px 20px; margin: 10px;" data-icon-styles="{'width': 14, 'height': 14}">I'm a button too!</a>
		
		When used with buttons, the button is replaced with a standard art-button (button's with inner text just render as buttons with 
		that text as the visible value, so we must replace it with a regular DOM element). The button input is hidden. When the art button
		is clicked, the click event is fired on the button so it still behaves the same way.
	*/
	artButtons: function(container) {
		if (!container.get('html').contains('ccs-art_button')) return;
		var buttonSelector = 'a.ccs-art_button, button.ccs-art_button, input.ccs-art_button';
		container.getElements('.ccs-button_bar, .ccs-button_subbar_above, .ccs-button_subbar_below').each(function(bar) {
			var above = bar.hasClass('ccs-button_subbar_above');
			var below = bar.hasClass('ccs-button_subbar_below');
			var buttons = bar.getElements(buttonSelector);
			buttons.each(function(button, i) {
				var first = (i == 0);
				var last = (i == buttons.length - 1);
				var margin = !first ? -1 : 0;
				button.store('ccs-art_button:styles', {
					borderRadius: [
						first && !below ? 4 : 0, //top-left
						last && !below ? 4 : 0, //top-right
						last && !above ? 4 : 0, //bottom-right
						first && !above ? 4 : 0 //bottom-left
					],
					'buttonElementMargin': margin
				});
			});
		}, this);


		container.getElements(buttonSelector).each(function(button){
			var pos = button.getStyle('position');
			if (pos != 'absolute' && button.getStyle('display') == 'inline') button.addClass('ccs-inline');
			var text, element;
			var isAnchor = button.get('tag') == 'a';
			if (isAnchor) {
				text = button.get('html').stripTags();
				button.empty();
				element = button;
			} else {
				text = button.get('html').stripTags() || button.get('value') || button.get('name');
			}
			var buttonOptions = {
				element: element,
				text: text,
				styles: {},
				className: 'art ' + button.get('class')
			};
			var height = button.getStyle('height').toInt();
			if (height) buttonOptions.height = height;
			if (button.getStyle("background-image")) {
				buttonOptions.icon = {
					styles: $merge(
						{
							position: 'absolute', 
							top: 4,
							left: 4,
							backgroundRepeat: 'no-repeat'
						},
						button.getStyles('background-image', 'background-position'),
						button.get('data', 'icon-styles', true)
					)
				};
			}
			//converts valid css expressions for padding, margin, etc into arrays of integers
			var fixStyleString = function(str) {
				var style = str.split(' ');
				style[0] = style[0].toInt();
				for (var i = 1; i < 4; i++) {
					style[i] = (style[i] || style[(i-2).max(0)]).toInt();
				}
				return style;
			};

			var isInButtonBar;
			if (button.retrieve('ccs-art_button:styles')) {
				isInButtonBar = true;
				$extend(buttonOptions.styles, button.retrieve('ccs-art_button:styles'));
			}
			if (button.getStyle('padding') != "0px 0px 0px 0px") buttonOptions.styles.padding = button.getStyle('padding');
			if ($type(buttonOptions.styles.padding) == "string") {
				buttonOptions.styles.padding = fixStyleString(buttonOptions.styles.padding);
			}
			if (isAnchor) button.set('class', '');
			var b = new ART.Button.Icon(buttonOptions);
			this.markForCleanup(function(){
				b.eject();
			});
			if (button.retrieve('ccs-art_button:styles')) {
				$(b).setStyle('margin-left', button.retrieve('ccs-art_button:styles').buttonElementMargin);
			}
			

			$(b).setStyles({
				background: 'none',
				padding: 0,
				position: (pos == 'static') ? 'relative' : pos
			});
			if (isInButtonBar) $(b).setStyle('float', 'left');
			if (!isAnchor) {
				b.inject(this, button, 'after');
				b.addEvent('press', function(){
					button.click();
				});
				button.hide();
			} else {
				b.register(this);
			}
			b.draw();
		}, this);
	}

});