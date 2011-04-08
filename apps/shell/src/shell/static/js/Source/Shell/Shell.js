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

script: Shell.js

description: Defines Shell; a Hue application that extends Hue.JBrowser.

authors:
- Hue

requires: [JFrame/JFrame.Browser, hue-shared/Hue.Request, Core/Element, Core/Native, Poller, Core/Fx, hue-shared/Hue.Desktop]
provides: [Shell]

...
*/
ART.Sheet.define('window.art.browser.shell', {
	'min-width': 620
});

(function() {
	var expressions = [
		{
			expr: /&/gm,
			replacement: '&amp;'
		},
		{
			expr: /</gm,
			replacement: '&lt;'
		},
		{
			expr: />/gm,
			replacement: '&gt;'
		},
		{
			expr: /"/gm,
			replacement: '&quot;'
		},
		{
			expr: /\n/g,
			replacement: "<br>"
		}
	];

	String.implement({
		escapeHTML: function() {
			var cleaned = this;
			expressions.each(function(expression) {
				cleaned = cleaned.replace(expression.expr, expression.replacement);
			});
			return cleaned;
		}
	});
})();

var Shell = new Class({

	Extends: Hue.JBrowser,
	options: {
		className: 'art browser logo_header shell',
		displayHistory: false
	},

	initialize: function(path, options) {
		this.parent(path || '/shell/', options);
		if (this.options && this.options.shellId) {
			this.shellId = options.shellId;
		}
		this.addEvent("load", this.startShell.bind(this));
	},

	startShell: function(view) {
		var shellIdContainer = $(this).getElement('.shell_id');
		if (shellIdContainer) {
			this.shellId = shellIdContainer.get("text");
		}

		// Set up some state shared between "fresh" and "restored" shells.
		this.previousCommands = [];
		this.currentCommandIndex = -1;

		this.jframe.markForCleanup(this.cleanUp.bind(this));
		this.shellKilled = false;

		this.background = $(this).getElement('.jframe_contents');
		this.background.setStyle("background-color", "#ffffff");
		this.container = $(this).getElement('.shell_container');
		this.output = new Element('span');
		this.input = new Element('textarea', {
			events: {
				keydown: this.handleKeyDown.bind(this),
				keyup: this.resizeInput.bind(this)
			},
			spellcheck: false
		});

		this.inputExpander = new Fx.Morph(this.input, { duration:0, transition: Fx.Transitions.linear });

		this.jframe.scroller.setOptions({
			duration: 200
		});

		// The command-sending request.
		this.commandReq = new Request.JSON({
			method: 'post',
			url: '/shell/process_command',
			onSuccess: this.commandProcessed.bind(this)
		});

		if (this.shellId) {
			this.startRestore(view);
		} else {
			this.setup(view);
		}
	},

	startRestore: function(view) {
		this.view = view;
		this.restoreReq = new Request.JSON({
			method: 'post',
			url: '/shell/restore_shell',
			onSuccess: this.restoreCompleted.bind(this),
			onFailure: this.restoreFailed.bind(this)
		});
		var shellId = this.shellId;
		this.restoreReq.send({
			data: 'shellId='+shellId
		});
	},

	restoreCompleted: function(json, text) {
		this.restoreReq = null;
		if (json.success) {
			this.view = null;
			this.nextOffset = json.nextOffset;
			this.previousCommands = json.commands;
			this.currentCommandIndex = this.previousCommands.length - 1;
			this.jframe.collectElement(this.container);
			this.container.empty();
			this.setupTerminal(json.output);
		} else if (json.notRunningSpawning) {
			this.errorMessage("Error", "The currently running webserver does not support the Shell app. Please contact your admin.");
		} else {
			this.restoreFailed();
		}
	},

	restoreFailed: function() {
		this.restoreReq = null;
		this.shellId = null;
		var view = this.view;
		this.view = null;
		this.setup(view);
	},

	setupTerminal: function(initVal) {
		// Set up the DOM
		this.container.adopt([this.output, this.input]);

		if (initVal) {
			this.appendToOutput(initVal);

			// Scroll the jframe and focus the input
			this.jframe.scroller.toBottom();
		}
		this.focusInput();

		// If the user clicks anywhere in the jframe, focus the textarea.
		this.background.addEvent("click", this.focusInput.bind(this));
		this.shellCreated = true;

		// Register the shell we have with Poller, so we can be included in the output channel it has.
		Hue.Desktop.store();
		Poller.listenForShell(this.shellId, this.nextOffset, this.outputReceived.bind(this));
	},

	focusInput: function() {
		if (!this.input.get("disabled")) {
			this.input.focus();
		}
	},

	setup: function(view) {
		this.shellCreated = false;
		var mainMenuButtons = $(this).getElements("a.menu_button");
		mainMenuButtons.each(function(button) {
			var keyName = button.nextSibling.get("text");
			button.addEvent('click', this.handleShellSelection.bind(this, keyName));
		}.bind(this));
	},

	handleShellSelection: function(keyName) {
		this.registerReq = new Request.JSON({
			method: 'post',
			url: '/shell/create',
			onSuccess: this.registerCompleted.bind(this),
			onFailure: this.registerFailed.bind(this)
		});
		this.registerReq.send({ data: "keyName="+keyName });
	},

	resizeInput: function() {
		var currHeight = this.input.getSize().y;
		var scrollHeight = this.input.getScrollSize().y;
		if (scrollHeight < currHeight) {
			return;
		}
		// Credit to Philip Hutchison, http://pipwerks.com/2010/05/07/textareaexpander-class-for-mootools/
		// for suggesting this way of resizing the input. It works really well. This idea is borrowed and
		// modified from his MIT-licensed code.
		this.inputExpander.start({ height: scrollHeight });
	},

	appendToOutput:function(text) {
		this.output.set('html', this.output.get('html')+text.escapeHTML());
	},

	registerFailed: function() {
		this.registerReq = null;
		this.choices = null;
		this.choicesText = null;
		this.errorMessage('Error',"Error creating shell. Is the shell server running?");
	},

	registerCompleted: function(json, text) {
		this.registerReq = null;
		if (!json.success) {
			if (json.shellCreateFailed) {
				this.errorMessage('Error', 'Could not create any more shells. Please try again soon.');
			} else if (json.notRunningSpawning) {
				this.errorMessage("Error", "The currently running webserver does not support the Shell app. Please contact your admin.");
			} else if (json.noSuchUser) {
				this.errorMessage("Error", "The remote server does not have a Unix user with your username. Please contact your admin.");
			} else if (json.shellNotAllowed) {
				this.errorMessage("Error", "You do not have permission to create a Shell of this type. Please contact your admin to get permission.");
			}
		} else {
			this.background.setStyle("background-color","#ffffff");
			this.shellCreated = true;
			this.shellId = json.shellId;
			this.options.shellId = json.shellId;
			this.nextOffset = 0;
			this.jframe.collectElement(this.container);
			this.container.empty();
			this.setupTerminal();
		}
	},

	showPreviousCommand: function() {
		if (this.currentCommandIndex < 0 || this.currentCommandIndex >= this.previousCommands.length) {
			this.currentCommandIndex = this.previousCommands.length-1;
		}
		var oldCommand = this.previousCommands[this.currentCommandIndex];
		if (oldCommand) {
			this.input.set('value', oldCommand);
			this.currentCommandIndex--;
			this.focusInput();
		}
	},

	showNextCommand: function() {
		if (this.currentCommandIndex < 0 || this.currentCommandIndex >= this.previousCommands.length) {
			this.currentCommandIndex = this.previousCommands.length?0:-1;
		}
		var oldCommand = this.previousCommands[this.currentCommandIndex];
		if (oldCommand) {
			this.input.set('value', oldCommand);
			this.currentCommandIndex++;
			this.focusInput();
		}
	},

	handleUpKey: function() {
		var tempInputValue = this.tempInputValue;
		this.tempInputValue = null;
		if (tempInputValue === this.input.get("value")) {
			this.showPreviousCommand();
		}
	},

	handleDownKey: function() {
		var tempInputValue = this.tempInputValue;
		this.tempInputValue = null;
		if (tempInputValue === this.input.get("value")) {
			this.showNextCommand();
		}
	},

	handleKeyDown: function(event) {
		if (event.key=="enter") {
			this.recordCommand();
			this.sendCommand();
		} else if (event.key=="up") {
			this.tempInputValue = this.input.get("value");
			// The delay is to deal with a problem differentiating "&" and "up" in Firefox.
			this.handleUpKey.delay(5, this);
		} else if (event.key=="down") {
			this.tempInputValue = this.input.get("value");
			// The delay is to deal with a problem differentiating "(" (left paren) and "down" in Firefox.
			this.handleDownKey.delay(5, this);
		} else if (event.key=="tab") {
			event.stop();
		}
		this.resizeInput.delay(0, this);
	},

	recordCommand: function() {
		var enteredCommand = this.input.get("value");
		if (enteredCommand) {
			if (this.previousCommands[this.previousCommands.length - 1] != enteredCommand) {
				this.previousCommands.push(enteredCommand);
				this.currentCommandIndex = this.previousCommands.length - 1;
			}
		}
	},

	sendCommand: function() {
		var enteredCommand = this.input.get("value");
		var shellId = this.shellId;
		this.disableInput();
		var dataToSend = {
			lineToSend : enteredCommand,
			shellId : shellId
		};
		this.commandReq.send({
			data: dataToSend
		});
	},

	commandProcessed: function(json, text) {
		if (json.success) {
			this.enableInput();
			this.input.setStyle("height","auto");
			this.input.set("value", "");
		} else {
			if (json.noShellExists) {
				this.shellExited();
			} else if (json.bufferExceeded) {
				this.errorMessage("Error", "You have entered too many commands. Please try again.");
			} else if (json.notRunningSpawning) {
				this.errorMessage("Error", "The currently running webserver does not support the Shell app. Please contact your admin.");
			}
		}
	},

	outputReceived: function(json) {
		if (json.alive || json.exited) {
			this.appendToOutput(json.output);
			this.jframe.scroller.toBottom();
			if (json.exited) {
				this.shellExited();
			}
		} else {
			if (json.noShellExists) {
				this.shellExited();
			} else if (json.shellKilled) {
				this.shellExited();
			} else {
				this.errorMessage('Error','Received invalid JSON response object from the Shell poller');
			}
		}
	},

	enableInput:function() {
		this.input.set({
			disabled: false,
			styles: {
				cursor: 'text',
				display: ''
			}
		}).focus();
	},

	disableInput:function() {
		this.input.set({
			disabled: true,
			styles: {
				cursor: 'default',
				display: 'none'
			}
		}).blur();
	},

	errorStatus:function() {
		this.disableInput();
		this.background.setStyle("background-color", "#cccccc");
	},

	errorMessage:function(title, message) {
		this.errorStatus();
		this.alert(title, message);
	},

	shellExited:function() {
		this.errorStatus();
		this.appendToOutput("\n[Process completed]");
		this.shellKilled = true;
	},

	cleanUp:function() {
		if (this.registerReq) {
			this.registerReq.cancel();
		}
		if (this.restoreReq) {
			this.restoreReq.cancel();
		}
		if (this.commandReq) {
			this.commandReq.cancel();
		}

		//Clear out this.options.shellId and this.shellId, but save the value in a local variable
		//for the purposes of this function.
		this.options.shellId = null;
		var shellId = this.shellId;
		this.shellId = null;

		//Tell the shell poller to stop listening for shellId. Important to do this before
		//sending the kill shell request because then the resulting output doesn't cause
		//a non-existent callback to be called.
		if (shellId) {
			Poller.stopShellListener(shellId);
			if (this.shellCreated && !this.shellKilled) {
				//A one-time request to tell the server to kill the subprocess if it's still alive.
				var req = new Request.JSON({
					method: 'post',
					url: '/shell/kill_shell'
				});
				req.send({
					data: 'shellId='+shellId
				});
			}
		}
		Hue.Desktop.store();
	}

});
