// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.	See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.	Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.	You may obtain a copy of the License at
//
//		 http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/*
---
description: Manages the background image/color of the Hue desktop.
provides: [Hue.Desktop.BackgroundManager]
requires: [hue-shared/Hue.Desktop, Widgets/ART.Menu, More/Fx.Elements, Core/Request.JSON]
script: Hue.Desktop.BackgroundManager.js

...
*/

ART.Sheet.define('menu.art.desktop-menu', {
	'z-index': 10002
});

var BackgroundManager = new Class({

	Implements: [Options, Events],

	options: {
		//onChoose: $empty,

		//these images are located in desktop/core/art/desktops
		//the object below is a key/value set of pretty name / file name pairs.
		//each file has a logo and an image (file_name.jpg, file_name.logo.png) in
		//the desktops directory
		backgroundImages: {
			'Pencil Tips': 'pencil_tips',
			'Color Pencils': 'color_pencils',
			'Pencil Tips2': 'pencil_tips2',
			'Painted Wood': 'painted_wood',
			'Purple Flower': 'purple_flower',
			'Pantone Cards': 'pantone_cards',
			'Blue Windows': 'blue_windows',
			'Tree Frog': 'tree_frog',
			'Red Wood': 'red_wood',
			'Hadoop!': 'hadoop',
			'Fuzzy Sparkles': 'fuzzy_sparkles',
			'Green Leaves': 'green_leaves',
			'Pastels': 'pastels'
		},
		//and these are static colors
		backgroundColors: {
			'Solid Grey': '#444',
			'Rich Blue': '#2f6390',
			'Grey Green': '#5F7D5F',
			'Khaki': '#E0DCAD'
		},
		//current is the background to show
		//by default it returns a random background image
		//value can be a string - a key of either backgroundColors or backgroundImages
		//or a function that returns a similar key.
		current: function(){
			return $H(this.options.backgroundImages).getKeys().getRandom();
		},
		//element to inject the menu into
		target: 'hue-desktop'
	},
	//where to get the background prefs from the server
	prefsUrl: "prefs/background",

	initialize: function(container, list, options){
		this.setOptions(options);
		this.list = $(list);
		this.container = $(container);
		//get the current /startup state
		this.current = $lambda(this.options.current).apply(this);
		//if the value is a color
		if (this.options.backgroundColors[this.current]) {
			//create an image for the hue logo, chosen at random from the background images
			new Element('img', {
				src: '/static/art/desktops/' + $H(this.options.backgroundImages).getValues().getRandom() + '.logo.png',
				'class': 'desktop-logo'
			}).inject(this.container, 'top');
			//set the bg color
			this.container.setStyle('background-color', this.options.backgroundColors[this.current]);
		} else {
			//otherwise inject the background & logo
			this.injectImages(this.current);
		}
		//remaining setup...
		this._bound = {
			resizeImages: this.resizeImages.bind(this)
		};
		this.list.adopt(this.getMenuItems());
		this.createMenu();
		this.resizeImages();
		this.attach();
	},
	//attaches resize functionality for resizing bg images
	attach: function(){
		//when the window is resized, resize the background
		window.addEvent('resize', this._bound.resizeImages);
	},
	//detaches resize functionality
	detach: function(){
		window.removeEvent('resize', this._bound.resizeImages);
	},
	//resizes the background image (if present) to match the window dimensions
	resizeImages: function(){
		//get the backgrounds (there may be more than one if rotation is in process)
		var bgs = this.container.getElements('.desktop-bg');
		//get the window dimensions
		var size = window.getSize();
		//if the aspect ratio of the window is > 1.6
		if (size.x/size.y > 1.6) {
			//then set the width of the image to equal the window
			bgs.setStyles({
				width: size.x,
				height: 'auto'
			});
		} else {
			//else set the height to match the window
			bgs.setStyles({
				width: 'auto',
				height: size.y
			});
		}
	},
	//injects the appropriate background and logo images into the document
	//name - key of backgroundImages
	//events - (object) any events to add to the background image; optional
	injectImages: function(name, events){
		var bg = this.container.getElement('.desktop-bg');
		var styles = bg ? bg.getStyles('width', 'height'): {};
		var img = new Element('img', {
			src: '/static/art/desktops/' + this.options.backgroundImages[name] + '.jpg',
			'class': 'desktop-bg',
			styles: styles
		}).inject(this.container, 'top');
		new Element('img', {
			src: '/static/art/desktops/' + this.options.backgroundImages[name] + '.logo.png',
			'class': 'desktop-logo'
		}).inject(this.container, 'top');


		if (events) img.addEvents(events);
		this.resizeImages();
	},
	//set the background to the given name
	//noFx - boolean; optional. If true, no transition is used
	setBackground: function(name, noFx){
		//if the name is a key in the background images, rotate the bg image
		if (this.options.backgroundImages[name]) {
			this.rotateBackgroundImage(name, noFx);
		} else if (this.options.backgroundColors[name]) {
			//else, if the name is a key of the bg colors, hide the bg image (if there is one)
			//and fade to the new color.
			this.current = name;
			//fade the bg color
			this.container.tween('background-color', this.options.backgroundColors[name]);
			var bg = this.container.getElement('.desktop-bg');
			// if there's a bg image, fade it out.
			if (bg) {
				if (noFx){
					bg.setStyle('opacity', 0).setStyle('visibility', 'visible');
				} else {
					bg.tween('opacity', 0).get('tween').chain(function(){
						bg.setStyle('visibility', 'visible');
					});
				}
			}
		} else {
			//key error
			dbug.warn('could not load background preference: ', name);
			return;
		}
		//get the current selected item in the menu and remove that designation
		this.list.getElements('.current').removeClass('current');
		//mark the new one as current
		this.links[name].addClass('current');
		this.fireEvent('choose', name);
	},
	//choose a random background image
	chooseRandom: function(){
		this.rotateBackgroundImage($H(this.options.backgroundImages).getValues().getRandom());
	},
	//rotate to a new background image
	//name - the key of the background image; if not defined, chooses a random one
	//noFx - boolean; if true use no transition
	rotateBackgroundImage: function(name, noFx){
		this.current = name;
		//grab the images there now
		var bg = this.container.getElement('.desktop-bg');
		var logo = this.container.getElement('.desktop-logo');

		//inject the image and icon
		this.injectImages(name || $random(0, this.options.backgroundImages.length-1), {
			load: function(){
				//if no transition, just destroy the existing ones
				if (noFx){
					if (bg) bg.destroy();
					if (logo) logo.destroy();
				} else {
					//otherwise crossfade
					var style = {
							'opacity': 0
						},
						images = [],
						fx = {};
					if (bg) images.push(bg);
					if (logo) images.push(logo);
					images.each(function(img, i){
						fx[i] = style;
					});
					//after they load, crossfade
					new Fx.Elements(images, {duration: 500}).start(fx).chain(function(){
						if (bg) bg.destroy();
						if (logo) logo.destroy();
					});
				}
			}
		});
	},
	//gets the LI elements for the menu consisting of all the images and colors
	getMenuItems: function(){
		//now we create the menu
		//first we list all the names
		var items = new Elements();
		this.links = {};

		//given a name, create a LI element with an anchor for that name
		var makeItem = function(name){
			var link = new Element('a', {
				html: name,
				'class': name == this.current ? 'current' : ''
			});
			this.links[name] = link;
			return new Element('li', {
				'class': 'menu-item'
			}).adopt(link);
		}.bind(this);

		for (name in this.options.backgroundImages) {
			items.push(makeItem(name));
		}
		//a separator
		items.push(
			new Element('li', {
				'class': 'menu-separator'
			})
		);
		//and then all the static colors
		for (name in this.options.backgroundColors){
			items.push(makeItem(name));
		}
		return items;
	},
	//creates a new instance of ART.Menu for the background container
	createMenu: function(){
		this.menu = new ART.Menu({
			className: 'art desktop-menu',
			startEvent: 'contextmenu',
			tabIndex: 10,
			//when the user chooses an item
			onPress: function(link){
				//get the index of the new one
				var name = link.get('html');
				//set the background and store the preference
				this.setBackground(name);
				this.store();
			}.bind(this)
		}, this.list, this.container).inject($(this.options.target));
	},
	store: function(){
		//send a request to store the preference on the server side.
		new Request.JSON({
				url: this.prefsUrl,
				method: "post"
		}).send("set=" + this.current);
	}
});