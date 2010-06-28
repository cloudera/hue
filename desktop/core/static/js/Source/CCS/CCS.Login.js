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
description: A modal window which asks the user to login.  Called by CCS.Request when the server-side middleware hits a URL for which login is required.
provides: [CCS.Login]
requires: [/CCS.SolidWindow, ccs-shared/ThumbTack, Core/Request.JSON, ccs-shared/Fx.Shake,
  /CCS.User, More/OverText, More/Mask, clientcide/StickyWin.PointyTip, /CCS.Desktop]
script: CCS.Login.js

...
*/
CCS.Login = new Class({
	Implements: [Options, Events],

	options: {/*
			onLoggedIn: $empty,
		*/
		formUrl: '/accounts/login_form'
	},

	initialize: function(options) {
		this.setOptions(options);
	},

	show: function() {
		new Request.HTML({
			url: this.options.formUrl,
			//don't evaluate js as we're handling the response manually
			evalScripts: false,
			onSuccess: function(tree, elements, html, js) {
				//mask the body
				$(document.body).mask({
					inject:{
						target: $('ccs-desktop'),
						where: 'bottom'
					}
				});
				//launch the login window with our html response
				this.window = new CCS.SolidWindow({
					getWindowManager: $empty,
					content: html,
					id: 'ccs-login',
					showNow: false,
					zIndex: 10003
				});
				//exec the js now that the html is in the DOM
				if (js) $exec(js);

				//set up overtext
				$(this.window).getElements('input').each(function(input){
					new OverText(input, {
						poll: true
					});
				});
				
				// pin the login box centered
				this.tack = new ThumbTack($(this.window), {
					destination: { edge: 'centerBottom' }
				});
				this.attachForm($(this.window).getElement('form'));
				this.window.show();

				var first = $('ccs-flogin-first');
				var pw = $(this.window).getElement('#ccs-pwhelp');
				var tip;
				if (first) {
					pw.hide();
					this.tip = new StickyWin.PointyTip('Welcome to Hue !', first, {
						point: 12,
						relativeTo: $(this.window),
						width: 400,
						zIndex: 10003,
						offset: {
							x: 4,
							y: 8
						}
					});
				} else {
					pw.addEvent('click', function(){
						if (this.tip && !this.tip.destroyed) return;
						this.tip = new StickyWin.PointyTip('Password Help', 
							'Your password here is set by the administrator of your cluster. Please contact them for password support.', 
							{
							point: 11,
							relativeTo: pw,
							width: 200,
							zIndex: 10003,
							offset: {
								x: -16
							}
						});
					}.bind(this));
				}
				OverText.update(); // show overtext
				$(document.body).addClass('ccs-loaded');
			}.bind(this)
		}).send();
	},

	/******** PRIVATE ************/
	//attaches to the login form
	attachForm: function(form){
		this.form = form;
		this.form.addEvent('submit', this.submit.bind(this));
	},

	//handles form submission
	submit: function(e){
		e.stop();
		this.mask();
		//before we send our request, check to see if we're resetting the user's session.
		this.send();
	},

	//shows the user that its busy
	mask: function(){
		$(this.window).addClass('ccs-loading');
		try { //some browsers hate this
			this.form.getElement('input.ccs-submit').blur();
		} catch(e) {dbug.log(e);}
	},

	//removes the loading state from the UI
	unmask: function(){
		$(this.window).removeClass('ccs-loading');
	},

	//sends the form
	send: function(){
		if (!this.validate()) return this.error();
		var fail = function(){
			if (this.xhr.failed) return;
			this.xhr.failed = true;
			CCS.error('Login Error', 'Something seems to be amiss. You can reload and try again or contact us for help.');
			this.unmask();
		}.bind(this);
		this.xhr = this.xhr || new Request.JSON({
			url: this.form.get('action'),
			secure: false,
			method: this.form.get('method') || 'post',
			onComplete: function(response){
				dbug.log('login attempt: ', response);
				if (!response) return fail();
				if (response.success) {
					this.success(response.user_data);
				} else {
					dbug.log("bad u/p!");
					this.error();
				}
			}.bind(this),
			onException: fail,
			onFailure: fail
		});
		this.xhr.failed = false;
		this.xhr.send(this.form);
	},


	//validates the form
	validate: function(){
		return this.form.getElement('input.ccs-password').get('value').trim() && 
			this.form.getElement('input.ccs-username').get('value').trim();
	},

  //when the form is successful
	//hide the login box and call login
	success: function(user_data){
		if ($('ccs-restore-option') && !$('ccs-restore-option').getElement('input').get('checked')) CCS.Desktop.resetSession();
		this.tack.detach();
		if (this.tip && !this.tip.destroyed) this.tip.destroy();
		$(this.window).set('tween', {
			transition: 'back:in',
			duration: 800,
			link: 'ignore'
		}).tween('top', -1000).get('tween').chain(function(){
			$(document.body).unmask();
			$(this.window).destroy();
			this.fireEvent('loggedIn', user_data);
		}.bind(this));
	},

  //displays the error transition when the credentials are bad
	error: function(){
		this.form.getElement('input.ccs-password').set('value', '').fireEvent('change');
		$(this.window).addClass('ccs-error').set('shake', {
			link:'ignore'
		}).shake('left', 20);
		this.unmask();
	}

});
