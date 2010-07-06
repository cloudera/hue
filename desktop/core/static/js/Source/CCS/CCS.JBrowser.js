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
description: A JBrowser is a window that encapsulates a JFrame and a linked HistoryMenu.
provides: [CCS.JBrowser]
requires: 
 - /CCS.JFrame
 - Widgets/ART.Browser
 - Widgets/ART.SolidWindow
 - /CCS.JFrame.AutoRefresh
 - /CCS.JFrame.Collapsible
 - /CCS.JFrame.DoubleClickDelegate
 - /CCS.JFrame.HtmlTable
 - /CCS.JFrame.OverText
 - /CCS.JFrame.SubmitOnChange
 - /CCS.JFrame.ContextMenu
 - /CCS.JFrame.FormRequest
 - /CCS.JFrame.NoOverflow
 - /CCS.JFrame.SplitView
 - /CCS.JFrame.Tabs
 - /CCS.JFrame.FitText
 - /CCS.JFrame.ConfirmAndPost
 - /CCS.JFrame.PromptAndPost
 - /CCS.JFrame.Refresh
 - /CCS.JFrame.SizeTo
 - /CCS.JFrame.FilterInput
 - /CCS.JFrame.FakeRefresh
 - /CCS.JFrame.Target
 - /CCS.JFrame.Chooser
 - /CCS.JFrame.Alert
 - /CCS.JFrame.Prompt
 - /CCS.JFrame.PartialRefresh
 - /CCS.JFrame.ArtButtons
 - /CCS.JFrame.SideBySideSelect
 - /CCS.JFrame.CheckAllOrNone
 - /CCS.JFrame.FormValidator
 - /CCS.JFrame.DataGroupToggle
 - /CCS.JFrame.ToggleHistory
 - /CCS.JFrame.Nav
 - /CCS.JFrame.Tips
 - /CCS.JFrame.SelectWithOther
 - /CCS.JFrame.Input
script: CCS.JBrowser.js

...
*/
(function(){

	var jbrowser = {

		options: {
			//the onLoad event fires when new content loads
			//onLoad: $empth(view),
			
			//display the history widget in the header?
			displayHistory: true,
			//showNow: if true, the window is displayed on instantiation
			showNow: false,
			//draggable: if true, the window can be dragged around
			draggable: true,
			//windowTitler: passed the default title from the response, returns a title for the window.
			windowTitler: function(title) {
				return title || this.options.windowOptions.caption || '';
			},
			jframeOptions: {}
		},

		initialize: function(path, options) {
			options = options || {};
			var show = $pick(options.showNow, true);
			options.showNow = false;
			this.parent(options);
			this._setupHistory(path);
			if (show) {
				this.options.showNow = true;
				this.show();
			}
			this._makeJFrame(path);
			if (Browser.Engine.trident) {
				$(this).setStyle('top', -111111111);
			} else {
				$(this).setStyle('visibility', 'hidden');
				if (this.history) $(this.history).setStyle('visibility', 'hidden');
			}
		},
		
		draw: function(){
			this.parent.apply(this, arguments);
			var cur = this.jframe.currentSize;
			if (cur.x != this.contentSize.x || cur.y != this.contentSize.y) {
				this.jframe.resize(this.contentSize.x, this.contentSize.y);
			}
		},
		
		_setupHistory: function(path){
			if (this.history) {
				if (!this.options.displayHistory) this.hideHistory();
				//prevent clicks to the history element from starting the drag behavior attached to the entire header
				$(this.history).addEvent('click', function(e) { e.stopPropagation(); });
				this.history.addEvents({
					refresh: function(){
						this.refresh();
					}.bind(this),
					select: function(path, title){
						if (path != this.jframe.currentPath) this.load({requestPath: path, suppressHistory: true });
					}.bind(this)
				});
			}
		},

		_makeJFrame: function(path){
			var opt = $merge({
				onLoadComplete: this._jframeLoaded.bind(this),
				onLoadError: this._jframeError.bind(this),
				onRedirect: function(){
					//do not restore scroll offsets when jframe is redirected
					this._scrolled = null;
				}.bind(this),
				size: {
					width: this.contentSize.x,
					height: this.contentSize.y
				},
				getScroller: function(){
					return this.content;
				}.bind(this),
				spinnerTarget: this.content
			}, this.options.jframeOptions);
			opt.parentWidget = this;
			this.jframe = new CCS.JFrame(path, opt);
			this.jframe.inject(this, this.content);
			
			//adds mouseover/mouseout behaviors for all links that have the class
			//.frame_tip; when the user mouses over such an object, the "status"
			//area in the window footer displays the title of that element.
			this.jframe.addFilters({
				statusTips: function(container) {
					container.addEvents({
						'mouseover:relay(.frame_tip)': function(e, element){
							var tipTitle = element.retrieve('tip:title', element.get('title') || '');
							element.set('title', '');
							this.setFooter(tipTitle);
						}.bind(this),
						'mouseout:relay(.frame_tip)': function(e, element){
							this.setFooter('');
						}.bind(this)
					});
				}.bind(this)
			});

			this.toolbar = new Element('div', {
				'class':'ccs-window-toolbar',
				events: {
					mousedown: function(e){
						//prevent clicks to the toolbar element from starting the drag behavior attached to the entire header
						if (!$(e.target).match('.draggable') && !$(e.target).getParent('.draggable')) e.stopPropagation();
					}
				}
			}).inject(this.header);
			this.jframe.applyDelegates(this.toolbar);
			this.jframe.applyDelegates(this.footerText);
			this.addEvents({
				focus: function(){
					this.jframe.focus();
				}.bind(this),
				destroy: function(){
					this.jframe.destroy();
				}.bind(this),
				unshade: function(){
					this.jframe.behavior.show();
				},
				shade: function(){
					this.jframe.behavior.hide();
				}
			});
			this.jframe.addEvent('refresh', this._storeScroll.bind(this));
			
		},

		wait: function(start){
			start = $pick(start, true);
			if (start) this.content.spin({ fxOptions: {duration: 200} });
			else this.content.unspin();
		},

		load: function(options) {
			this.jframe.load(options);
			return this;
		},

	/*
		options are passed to jframe's renderContent method
		*/

		setContent: function(options){
			this.jframe.renderContent(options);
			return this;
		},

		refresh: function() {
			this.jframe.refresh();
			return this;
		},

		resize: function(w, h) {
			if (w == this.currentWidth && h == this.currentHeight) return;
			this.parent(w, h);
			this.jframe.resize(this.contentSize.x, this.contentSize.y);
		},

		_jframeLoaded: function(data) {
			if (!Browser.Engine.trident) {
				(function(){
					$(this).setStyle('visibility', 'visible');
					if (this.history) $(this.history).setStyle('visibility', 'visible');
				}).delay(20, this);
			}
			this.setCaption(this.options.windowTitler(data.title || data.repsonsePath));
			this.toolbar.empty();
			this.footerText.empty();
			if (data.toolbar) this.toolbar.adopt(data.toolbar);
			if (data.footer) this.footerText.adopt(data.footer);
			if (!data.suppressHistory && this.history) this.history.push({ path: data.responsePath, title: data.title || data.repsonsePath});
			if (this._jframe_view != data.view) {
				if (this._jframe_view) {
					this.contents.removeClass(this._jframe_view);
					this.removeClass(this._jframe_view);
				}
				if (data.view) {
					this.contents.addClass(data.view);
					this.addClass(data.view);
					this._jframe_view = data.view;
				}
			}
			this.fireEvent('load', data.view);
			if (this.getState('focused')) this.jframe.focus();
			/*
				I hate this delay, but the browser apparently needs it to render the HTML. You can't set the scroll offset of something
				thats empty (because there's no where to scroll). The duration may require some additional care with diff. browsers or
				slower computers.
			*/
			this._restoreScroll.delay(50, this);
		},

		_jframeError: function(error) {
			if (this.refreshButton) this.refreshButton.unspin();
		},

		//returns an object with the dimensions, location, path, and options
		serialize: function(){
			return {
				styles: $(this).getStyles(['top', 'left']),
				size: this.getSize(),
				path: this.jframe.currentPath,
				options: this.options
			};
		},

		//restore's a window to a given location and size
		restore: function(state){
			//restore the position
			$(this).setStyles(state.styles);
			//restore the size
			this.resize(state.size.width, state.size.height);
			return this;
		},
		
		minMax: function(operation){
			if (operation == "maximize") {
				this.toolbar.setStyle('display', 'block');
				if (this.history) $(this.history).setStyle('display','block');
				this._minimized = false;
				var beforeStr = 'before'+ operation.capitalize();
				if (this[beforeStr]) {
					this.element.setStyles(this.posBefore);
				} else {
					this.posBefore = this.element.getStyles('top', 'left');
					this.element.setStyles({
						top: 0,
						left: 0
					});
				}
			} else {
				if (!this._minimized) {
					this.toolbar.setStyle('display', 'none');
					if (this.history) $(this.history).setStyle('display','none');
					this._minimized = true;
				} else {
					if (this.history) $(this.history).setStyle('display','block');
					this.toolbar.setStyle('display', 'block');
					this._minimized = false;
				}
			}
			this.parent(operation);
		},

		//returns the elements whose scroll offset we want to store
		//this includes any element with the .save_scroll class
		//and also the contents of the window itself.
		_getScrollElements: function(){
			var scrollers = $(this).getElements('.save_scroll');
			scrollers.include(this.content);
			return scrollers;
		},

		//stores the scroll offset for all the elements that we are saving
		_storeScroll: function(){
			this._storedScrollPath = this.jframe.currentPath;
			this._scrolled = this._getScrollElements().map(function(el){
				return el.getScroll();
			});
		},

		//restores the scroll offsets to the elements we saved
		//but only if we found a matched number of each
		//note: that this behavior is only triggered on refresh. The main issue with refresh is if there's a redirect.
		_restoreScroll: function(){
			if (!this._scrolled || this.jframe.currentPath != this._storedScrollPath) return;
			var scrollers = this._getScrollElements();
			if (scrollers.length == this._scrolled.length) {
				this._scrolled.each(function(data, i) {
					scrollers[i].scrollTo(data.x, data.y);
				});
			}
			this._scrolled = null;
		}

	};

	CCS.JBrowser = new Class(
		$merge({
			Extends: ART.Browser,
			options: {
				help: function(){
					var help = $(this).getElement('a[target=Help].help');
					CCS.Desktop.showHelp(this, help ? help.get('href') : null);
				}
			}
		}, jbrowser)
	);
	CCS.JBrowser.Solid = new Class(
		$merge({
			Extends: ART.SolidWindow
		}, jbrowser)
	);
	//a window alert w/ a jframe
	CCS.JBrowser.Confirm = new Class(
		$merge({
			Extends: ART.Confirm,
			displayHistory: false
		}, jbrowser)
	);
	//shortcut for JBrowser.Confirm
	CCS.JBrowser.confirm = function(caption, content, callback, options) {
		return new CCS.JBrowser.Confirm(options.path,
			$extend(options || {}, {
				caption: caption,
				onConfirm: callback || $empty
			})
		);
	};
})();
