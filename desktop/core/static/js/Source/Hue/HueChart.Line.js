/*
---

script: HueChart.Line.js

description: Defines HueChart.Line, builds on HueChart.Box to produce line charts.

license: MIT-style license

authors:
 - Marcus McLaughlin

requires:
 - /HueChart.Box

provides: [HueChart.Line]

...
*/

HueChart.Line = new Class({

		Extends: HueChart.Box,

		options: {
				lineWidth: 3, //Width of the lines in the chart
				dot: {
					strokeColor: '#fff', //the color of the line around the dot at each data point
					size: 0
				}
		},

		initialize: function(element, options) {
				this.parent(element, options);
				this.render();
		},
		
		//Build line graph.
		addGraph: function(vis) {
				//In effort to maintain same data structure for lines and stacked charts, iterating
				//through the series and adding a line using each series for its data points.
				for (var itemIndex = 0; itemIndex < this.series.length; itemIndex++) {
						var series = this.series[itemIndex];
						var dataSeries = this.getData(true).getDataSeries(series);
						//Add a line to the visualization, connecting points produced from the data object.
						var visLine = vis.add(pv.Line)
								//Using as data, this.data.getObjects.
								.data($lambda(dataSeries))
								//Closures used because the function argument isn't executed until the render phase.
								//Color the line, based on the color returned by the colorManager.
								.strokeStyle(function(itemIndex) {
										return function() {
												return this.getColor(this.series[itemIndex]);
										}.bind(this);
								}.bind(this)(itemIndex))
								//For each data object, create a point with its left position at the data object's xField value scaled to pixels and its bottom position at the data object's value for this series scaled to pixels.
								.left(function(d) {
										return this.xScale(d[this.xProperty]);
								}.bind(this))
								.bottom(function(itemIndex) {
										return function(d) {
												return this.yScale(d[this.series[itemIndex]]);
										}.bind(this);
								}.bind(this)(itemIndex))
								//Make the line's width 3 pixels.
								.lineWidth(this.options.lineWidth);
						if (this.options.dot.size) {
							visLine.add(pv.Dot)
								.strokeStyle(this.options.dot.strokeColor)
								.fillStyle(function(itemIndex) {
										return function() {
												return this.getColor(this.series[itemIndex]);
										}.bind(this);
								}.bind(this)(itemIndex))
								.size(this.options.dot.size)
								.lineWidth(1);
						}
				}
		}
});

