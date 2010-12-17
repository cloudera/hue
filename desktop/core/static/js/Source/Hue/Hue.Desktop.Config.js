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
provides: [Hue.Desktop.Config]
requires: [/Hue.Desktop, clientcide/StickyWin.Drag, Widgets/ART.Popup, Widgets/ART.Glyphs, Core/Selectors, More/HtmlTable.Select, Core/JSON]
script: Hue.Desktop.Config.js

...
*/

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
		size.y = size.y - $('hue-desktop').getStyle('top').toInt();
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

});

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
