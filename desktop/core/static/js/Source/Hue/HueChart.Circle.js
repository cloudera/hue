/*
---

script: HueChart.Circle.js

description: Defines HueChart.Circle, a base class for circular charts, which builds on HueChart.

license: MIT-style license

authors:
- Marcus McLaughlin

requires:
- /HueChart

provides: [HueChart.Circle]

...
*/


HueChart.Circle = new Class({
		
		Extends: HueChart,

		options: {
				selectedColor: '#fff',
				//radius: null the radius of the chart, (will default to width/2)
				graphProperty: 'data', // the property in the data object that should be graphed,
				nameProperty: null // the property in the data object that should be used to name each wedge
				/*
				onWedgeOver: function to be executed when the mouse is moved over a wedge of the chart, 
				onWedgeOut: function to be executed when the mouse is moved off of a wedge of the chart,
				onWedgeClick: function to be executed when a wedge of the chart is clicked
				*/
		}, 

		initialize: function(element, options) {
				this.parent(element, options);
				this.selected_index = -1;
				this.radius = this.options.radius || this.width/2;
				this.addEvent('setupChart', function(vis) {
						this.addGraph(vis);
						if(this.hasEvent('wedgeOut') && this.hasEvent('wedgeOver') || this.hasEvent('wedgeClick')) this.addEventBar(vis);
						vis.render();
				});
		},

		addGraph: function(vis) {
				var valueSum = this.getData(false).getSeriesSum(this.options.graphProperty);
				//Put selected index, color array, and hue chart in scope
				var get_selected_index = this.getSelectedIndex.bind(this);
				var colorArray = this.options.colorArray;
				var hueChart = this;
				vis.add(pv.Wedge)
						//Data is the array of contained within the HueChart.Data object.
						.data(this.getData(false).getObjects())
						//Bottom of the wedge space is the radius
						.bottom(this.radius)
						//Left of the wedge space is the radius
						.left(this.radius)
						//The outer radius is the radius
						.outerRadius(this.radius)
						//The angle is a normalized value summing to 2PI based on the values in the graphProperty. 
						.angle(function(d) { 
								return (d[this.options.graphProperty]/valueSum) * 2 * Math.PI; 
						}.bind(this))
						//Fill with white if selected, otherwise use value from colorManager 
						.fillStyle(function(d) {
								return this.index == get_selected_index() ? hueChart.options.selectedColor : hueChart.getColor($pick(d[hueChart.options.nameProperty], this.index));
						}).event("click", function(d) {
								hueChart.fireEvent('wedgeClick', [d, this.index]);
						});                
		},
		
		//Adds an event processing bar on top of the panel, which is used to appropriately fire wedgeOut/Over events
		addEventBar: function(vis) {
				//Base vector is vector pointing straight up.
				var baseVector = {x: 0, y: this.radius};
				//Shortcut to data array
				var dataArray = this.getData(false).getObjects();
				//Calculate sum of graph values
				var valueSum = this.getData(false).getSeriesSum(this.options.graphProperty);
				//Shortcut to graphProperty
				var graphProperty = this.options.graphProperty;
				//Add an invisible bar to catch events
				vis.add(pv.Bar)
						//Left of bar at 0
						.left(0)
						//Bottom of bar at 0
						.bottom(0)
						//Width is width of panel
						.width(this.width)
						//Height is height of panel
						.height(this.height)
						//Fillstyle is white with a very very small (negligible, even) opacity
						.fillStyle("rgba(0,0,0,.001)")
						.event("mousemove", function() {
								//baseVector.y is equal to radius
								var curPoint = vis.mouse();
								//Conversion from mouse points to vectors where mouse point (radius, radius) is equal to vector (0, 0) (origin)
								//xPoint -> xVector: xVector = xPoint - radius;
								var curVector = {};
								curVector.x = curPoint.x - baseVector.y; 
								//yPoint -> yVector: yVector = (yPoint - radius) * -1;
								curVector.y = (curPoint.y - baseVector.y) * -1;
								//Length of vector - sqrt(x^2 + y^2)
								var vectorLength = Math.sqrt(Math.pow(curVector.x, 2) + Math.pow(curVector.y, 2));
								//Angle of a vector 2 relative to vector 1 = atan2(v2.y, v2.x) - atan2(v1.y, v1.x)
								//In radians
								//Quadrants 1 to 3 - negative numbers ascending clockwise from vertical.  
								//Quadrant 4 - positive number ascending counter-clockwise from vertical. 
								var angle = Math.atan2(curVector.y, curVector.x) - Math.atan2(baseVector.y, baseVector.x);
								//Convert angle to positive number ascending clockwise from vertical.
								if (angle < 0) {
										 //In quadrant 1 to 3 - convert to a positive number.
										 angle = -angle;
								} else {
										 //In quadrant 4 - subtract angle from Math.PI/2 to find positive amount from 3pi/2, add 3pi/2.  
										 angle = (Math.PI/2 - angle) + (3 * Math.PI/2);
								}
								var nextAngle = 0;
								//Create array of angle sums.
								var angleSums = [];
								for (var i = 0; i < dataArray.length; i++) {
										//Calculate angle -- previousAngle (angleSums[i-1] plus the latest angle. 
										newAngle = (angleSums[i -1] || 0) + ((dataArray[i][graphProperty]/valueSum) * 2 * Math.PI); 
										angleSums.push(newAngle);
								}

								//Fire wedgeOver event if the current angle is greater than the sum of all prior angles but less than that sum plus the next angle.
								//If the vector is shorter than the radius (meaning it's within the circle), search for a wedge, otherwise, fire wedge out
								if (vectorLength < this.radius) {
										for (i = 0; i < dataArray.length; i++) {
												lastAngle = angleSums[i -1] || 0;
												if (angleSums[i] > angle && angle > lastAngle) {
														//Don't do anything if this wedge is already selected.
														if (i != this.getSelectedIndex()) {
																//Fire wedgeOut for the previously selected wedge
																if (this.getSelectedIndex() != -1) {
																		this.fireEvent('wedgeOut', [ dataArray[this.getSelectedIndex()], this.getSelectedIndex()]);
																}
																//Fire wedgeOver for the newly selected wedge
																this.fireEvent('wedgeOver', [ dataArray[i], i]);
														}
												} 
										}
								} else if(this.getSelectedIndex() != -1) {
										this.fireEvent('wedgeOut', [ dataArray[this.getSelectedIndex()], this.getSelectedIndex()]);
								}
						}.bind(this))
						//Fire wedgeOut when we mouse out of the panel, since clearly we can no longer be over a wedge within the panel;.
						.event("mouseout", function() {
								if (this.getSelectedIndex() != -1) {
										this.fireEvent('wedgeOut', [ dataArray[this.getSelectedIndex() ], this.getSelectedIndex()]);
								}
						}.bind(this));
		},

		highlightWedge: function(sliceIndex) {
				this.setSelectedIndex(sliceIndex);
				this.render();
		},

		unHighlightWedges: function() {
				this.setSelectedIndex(-1);
				this.render();
		},

		resize: function(width, height) {
				this.radius = width/2;
				this.parent(width, height);
		}

});
