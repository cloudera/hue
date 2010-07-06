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
description: Desktop Configuration
provides: [CCS.Desktop.Config]
requires: [/CCS.Desktop, clientcide/StickyWin.Drag]
script: CCS.Desktop.Config.js

...
*/
//by default, make all StickyWin instances load inside of div#ccs-desktop
StickyWin.implement({
	options: {
		inject: {
			target: 'ccs-desktop'
		}
	},
	destroyOnClose: true
});

//same for ART.Popup instances
ART.Popup.implement({
	destroyOnClose: true,
	options: {
		cascaded: true
	}
});
ART.Sheet.define('window.art', {
	'min-height': 88,
	'width':800
});

ART.Sheet.define('window.art.browser.logo_header', {
	'header-height': 90,
	'header-overflow': 'visible',
	'min-width': 620
});

ART.Sheet.define('window.art.browser.logo_header history.art', {
	'padding': [0, 8, 0, 70]
});

ART.Sheet.define('window.art.browser.logo_header history.art', {
	'top':32
}, 'css');

UI.Sheet.define('window.art button.art.wincontrol', {
	'background-color': ['hsb(0, 0, 100)', 'hsb(0, 0, 85)'],
	'border-color': ['hsb(0, 0, 60)', 'hsb(0, 0, 50)'],
	'font-family': 'Moderna',
	'font-size': 13,
	'font-color': 'black'
});

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

if (Browser.Engine.trident) {
	UI.Sheet.define('window.art:dragging', {
		'background-color': hsb(202, 20, 38, 1)
	});
}


window.addEvent('domready', function(){
	$(document.body).addEvent('contextmenu', function(e){
		if (!dbug.enabled) e.preventDefault();
	});
	
	//this sizer method will ensure that windows are always reachable and ever larger than the window
	//(so you can always reach it's bottom corner to resize it)
	var sizer = function(){
		//get the size of the desktop itself
		var size = window.getSize();
		//minus the offset of the desktop
		size.y = size.y - $('ccs-desktop').getStyle('top').toInt();
		//define the default size of windows to be 70% of the window size
		var styles = UI.Sheet.lookup('window.art');
		var defaults = {
			'height': (size.y * 0.7).toInt(),
			'width': (size.x * 0.7).toInt(),
			//and the max height/width is the size of the desktop
			//minus 35 px for the height for the dock
			'max-height': Math.max(styles.minHeight, (size.y + 2).toInt() - 50),
			'max-width': Math.max(styles.minWidth, (size.x + 2).toInt())
		};
		UI.Sheet.define('window.art', defaults);
		UI.Sheet.define('window.browser.art', defaults);
		styles = UI.Sheet.lookup('window.art');
		//for all the existing instances, resize them and move them onto the screen.
		ART.Popup.DefaultManager.instances.each(function(instance) {
			if (instance.currentHeight > styles.minHeight || instance.currentWidth > styles.minWidth) {
				var resize = {
					height: Math.max(styles.minHeight, Math.min(instance.currentHeight, size.y + 2)),
					width: Math.max(styles.minWidth, Math.min(instance.currentWidth, size.x + 2))
				};
				instance.resize(resize.width, resize.height);
			}
			instance.getOnScreen({
				y: -35
			});
		});
	};
	var timer;
	window.addEvent('resize', function(){
		$clear(timer);
		//when we resize the window, we adjust the open windows, but this event - window's resize event -
		//fires constantly as you resize it, so we add a timeout that is reset every time the event fires
		timer = sizer.delay(100);
	});
	//size everything now
	sizer();
	//whenever the window scrolls down (if the user hits space, for example, or page down)
	//send them back to 0,0; the desktop isn't supposed to scroll
	window.addEvent('scroll', function(e) {
		window.scrollTo(0,0);
	});
	
	$(document.body).addEvent('dblclick', function(e){
		if(document.selection && document.selection.empty) document.selection.empty();
		else if(window.getSelection) window.getSelection().removeAllRanges();
	});
});

Selectors.Pseudo.widget = function() { return !! this.get("widget"); }; 
