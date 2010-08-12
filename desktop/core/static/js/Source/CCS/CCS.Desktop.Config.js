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
requires: [/CCS.Desktop, clientcide/StickyWin.Drag, Widgets/ART.Popup, Widgets/ART.Glyphs, Core/Selectors, More/HtmlTable.Select, Core/JSON]
script: CCS.Desktop.Config.js

...
*/

HtmlTable.implement({
	options: {
		classNoSort: 'noSort'
	}
});

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

	//given an element, determine if it's cool to double click and select text within it
	var canSelectOnDblClick = function(elem) {
		//if it's a textarea or input, go for it
		if (elem.match('input') || elem.match('textarea')) return true;
		//otherwise, we only allow double click selection inside of window contents
		if (elem.getParent('.jframe_contents')) {
			//except if the double clicked element is inside an html table that has selectable rows
			var parentTable = elem.getParent('[data-filters*=HtmlTable]');
			if(parentTable && (parentTable.hasClass('.selectable') || parentTable.hasClass('.multiselect'))){
				return false;
			}
			//or if the element is part of a double click action
			if(elem.match('[data-dblclick-delegate]') || elem.getParent('[data-dblclick-delegate]')) return false;
			return true;
		}
		return false;
	};
	
	$(document.body).addEvent('dblclick', function(e){
		if(!canSelectOnDblClick(e.target)){ 
			if(document.selection && document.selection.empty) document.selection.empty();
			else if(window.getSelection) window.getSelection().removeAllRanges();
		}
	});
});

Selectors.Pseudo.widget = function() { return this.get && (!! this.get("widget")); };

//Although implement checks for a pre-existing implementation of the method, it has to be forced for IE to overwrite the MooTools version.
//Thus, the IE check.
if (Browser.Engine.trident) {
	Array.implement({
		forEach: function(fn, bind){
			var len = this.length;
			for (var i=0; i < len; i++) {
				if(i in this) fn.call(bind, this[i], i, this);
			}
		}       
	}, true);

	Array.alias('forEach', 'each', true); 
}

// Monkey-patch the dbug.* functions to also log their events to the server. We don't want to
// crush the server either with too-many or too-frequent messages, so we only send every 5 seconds,
// unless there are more than 100 messages in the message queue.
(function(info, warn, error) {
	var parse = function(){
		var str = '';
		for (var i = 0; i < arguments.length; i++) {
			var value = arguments[i];
			switch ($type(value)) {
				case 'element':
					var el = document.id(value);
					str += el.get('tag');
					if (el.get('id')) str += '#' + el.get('id');
					if (el.get('class')) str += el.get('class').split(' ').join('.');
					break;

				case 'array': case 'collection':
					str +='[';
					var results = [];
					for (var index = 0; index < value.length; index++) {
						results.push(parse(value[index]));
					}
					str += results.join(', ') + ']';
					break;

				case 'object':
					var objs = [];
					for (name in value) {
						if ($type(value[name]) != 'object') {
							objs.push(name + ': ' + parse(value[name]));
						} else {
							objs.push(name + ': (object)');
						}
					}
					str += '{' + objs.join(', ') + '}';
					break;

				case 'function':
					str += '(function)';
					break;

				case 'boolean':
					str += String(value);
					break;

				default: str += value;
			}
			if (i != (arguments.length - 1)) str += ', ';
		}
		return str;
	};

	var monkeyPatchDbugFunction = function(dbugMethod, level) {
		var messageQueue = [],
		    timer;

		var startTimer = function(){
			$clear(timer);
			timer = sendQueuedMessages.delay(5000);
		};

		var sendQueuedMessages = function() {
			$clear(timer);
			if (window.sendDbug && messageQueue.length > 0) {
				new Request.JSON({
					url: '/log_frontend_event',
					data: {
						message: JSON.encode(messageQueue),
						level: level
					},
					onComplete: startTimer
				}).post();
				// Immediately clear the queue after we try to send it.
				// If the send fails, oh well.
				messageQueue.empty();
			} else {
				startTimer();
			}
		};

		// Poll the message queue every 5 seconds to see if it has messages to send.
		startTimer();

		return function() {
			messageQueue.push(parse.apply(parse, arguments));
			// Immediately send the message queue if it's getting too big.
			if (messageQueue.length > 100) {
				sendQueuedMessages();
			}
			dbugMethod.apply(dbug, arguments);
		};
	};

	// We do the monkey-patching of the functions regardless of the initial value
	// of window.sendDbug so that some one can turn this on in the browser at
	// run-time without having to restart the server.
	//
	// These strings are what hue expects.
	dbug.info = monkeyPatchDbugFunction(info, 'info');
	dbug.warn = monkeyPatchDbugFunction(warn, 'warning');
	dbug.error = monkeyPatchDbugFunction(error, 'error');
})(dbug.info, dbug.warn, dbug.error);
