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
description: Creates a SplitView instances for all elements that have the css class .splitview (and children with .left_col and .right_col).
provides: [CCS.JFrame.SplitView]
requires: [/CCS.JFrame, Widgets/ART.SplitView]
script: CCS.JFrame.SplitView.js

...
*/

CCS.JFrame.addGlobalFilters({

	splitView: function(container) {
		if (!container.get('html').contains('splitview')) return;
		container.setStyle('overflow', 'hidden');
		//for all div.splitview containers, get their left and right column and instantiate an ART.SplitView
		//if the container has the class "resizable" then make it so
		//ditto for the foldable option
		//if the left or right columns have explicit style="width: Xpx" assignments
		//resize the side to match that statement; if both have it, the right one wins
		var splitviews = container.getElements('div.splitview').map(function(splitview){
			var left = splitview.getElement('.left_col');
			var right = splitview.getElement('.right_col');
			var top = splitview.getElement('.top_col');
			var bottom = splitview.getElement('.bottom_col');
			if (!(left && right) && !(top && bottom)) {
				dbug.warn('found split view element, but could not find top/botom or left/right; exiting');
				return;
			}
			var conf;
			if (left) {
				conf = {
					sides: ['left', 'right'],
					elements: {
						left: left,
						right: right
					},
					dimension: 'width'
				};
			} else {
				conf = {
					sides: ['top', 'bottom'],
					elements: {
						top: top,
						bottom: bottom
					},
					dimension: 'height'
				};
			}
			var inlineSize = {};
			conf.sides.each(function(side) {
				var size = conf.elements[side].style[conf.dimension];
				if (size) inlineSize[side] = size.toInt();
				conf.elements[side].setStyle(conf.dimension, 'auto');
			});
			
			var styles = {}, splitterHidden;
			var splitter = splitview.getElement('.splitter_col');
			if (splitter) {
				if (splitter.getStyle('display', 'none')) {
					splitterHidden = true;
					splitter.setStyle('display', 'block');
				}
				if (left) styles['splitter-width'] = splitter.getSize().x;
				else styles['splitter-height'] = splitter.getSize().y;
			}
			
			var whichSplit = left ? ART.SplitView : ART.SplitView.Vertical;
			var split = new whichSplit({
				resizable: splitview.hasClass("resizable"),
				foldable: splitview.hasClass("foldable"),
				splitterContent: splitview.getElement('.splitter_col'),
				styles: styles
			}).inject(this, splitview, 'after').draw();
			var sized;
			conf.sides.each(function(side) {
				split['set' + side.capitalize() + 'Content'](conf.elements[side]);
				split[side].addClass('save_scroll');
				if (sized) return;
				if (conf.elements[side].getStyle('display') == 'none') {
					split.fold(side, 0, splitterHidden, true);
					conf.elements[side].setStyle('display', 'block');
					sized = true;
				} else if (inlineSize[side]) {
					split['resize'+side.capitalize()](inlineSize[side]);
					sized = true;
				}
			});
			var classes = splitview.get('class').split(' ');
			splitview.destroy();
			classes.each(split.addClass, split);
			split.resizer = function(){
				if (this.parentWidget && this.parentWidget.contentSize) {
					var offsets = {
						x: splitview.get('data', 'split-offset-x', true),
						y: splitview.get('data', 'split-offset-y', true)
					};
					var w = this.parentWidget.contentSize.x;
					var h = this.parentWidget.contentSize.y;
					if (offsets.x) w = w - offsets.x;
					if (offsets.y) h = h - offsets.y;
					if (w != undefined && h != undefined) split.resize(w, h);
					else split.resizer.delay(1);
				} else {
					split.resizer.delay(1);
				}
			}.bind(this);
			this.addEvents({
				resize: split.resizer,
				show: split.resizer
			});
			split.resizer();
			return split;
		}, this);
		this.markForCleanup(function(){
			splitviews.each(function(splitview) {
				this.removeEvent('resize', splitview.resizer);
				splitview.eject();
			}, this);
		}.bind(this));

		return splitviews;
	}

});

(function(){

var getWidget = function(link) {
	var splitview = link.getParent('.splitview');
	if (!splitview) return;
	return splitview.get('widget');
};
CCS.JFrame.addGlobalLinkers({

	'[data-splitview-resize]': function(e, link){
		var widget = getWidget(link);
		if (!widget) return;
		var resize = link.get('data', 'splitview-resize', true);
		if (!resize) return;
		var side;
		var sides = ['left', 'right', 'top', 'bottom'];
		for (key in resize) {
			if (sides.contains(key)) side = key;
		}
		widget.fold(side, resize[side], resize.hideSplitter).chain(partialPostFold.bind(this, [resize, e, link]));
	},

	'[data-splitview-toggle]': function(e, link){
		var widget = getWidget(link);
		if (!widget) return;
		var resize = link.get('data', 'splitview-toggle', true);
		if (!resize) return;
		widget.toggle(resize.side, resize.hideSplitter).chain(partialPostFold.bind(this, [resize, e, link]));
	}

});

var partialPostFold = function(data, event, link){
	if (!$(document.body).hasChild(link)) return;
	if (data.partialRefresh) {
		if ($type(data.partialRefresh) == "string") link = new Element('a', { href: data.partialRefresh });
		this.invokeLinker('.ccs-fake_refresh', link, event);
	}
};

})();