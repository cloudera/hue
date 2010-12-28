/*
---

script: HueChart.js

description: Defines HueChart; a wrapper for Protovis, which produces charts of various sorts.

license: MIT-style license

authors:
- Marcus McLaughlin

requires:
- protovis/Protovis
- More/Date
- Core/Events
- Core/Options
- ccs-shared/Number.Files
- More/Element.Shortcuts
- ccs-shared/HueChart.GroupValueManager

provides: [ HueChart ]

...
*/
//

(function() {
var colorManager = GroupValueManager;

HueChart = new Class({

		Implements: [Events, Options],

		options: {
				//The array of colors which will be used for the chart.
				colorArray:  [
						'#1f77b4',
						'#aec7e8',
						'#ff7f0e',
						'#ffbb78',
						'#2ca02c',
						'#98df8a',
						'#d62728',
						'#ff9896',
						'#9467bd',
						'#c5b0d5',
						'#8c564b',
						'#c49c94',
						'#e377c2',
						'#f7b6d2',
						'#7f4f7f',
						'#c7c7c7',
						'#bcbd22',
						'#dbdb8d',
						'#17becf',
						'#9edae5'
				],
				//The font which will be used for the axis labels.
				labelFont: '14px sans-serif',
				//The height of the x axis rules
				width: 200, //the initial width of the chart 
				height: 200, //the initial height of the chart 
				dataTable: null, //table containing the chart data
				dataObject: [], //array of data objects
				//One of dataTable or dataObject is required
				/*
				onSetupChart: function that runs when the protovis rendering information is being set up, but before the protovis object is rendered, takes the protovis objects as an argument
				*/
				padding:[0], //the array of padding values.  Accepts between 1 and 4 values, in CSS TRBL format.  Also allows named padding values below.
				  //If there are named values, they will supercede the result from the padding array.  
				  /*bottomPadding: 0, // the padding between the bottom of the element, and the bottom of the graph,
				  topPadding: 0, // the padding between the top of the element, and the left of the graph,
				  leftPadding: 0, // the padding between the left of the element, and the left of the graph,
				  rightPadding: 0, // the padding between the right of the element, and the right of the graph,*/
				  url: "noUrl" //the url of the page. this will be used as a key in the colorManager
		},


		initialize: function(element, options) {
				this.setOptions(options);
				this.element = document.id(element);
				//Width and height will potentially change often, make them instance variables.
				this.width = this.options.width;
				this.height = this.options.height;
				//Process padding array with named values -- interpreted in same way CSS side-oriented values are.
				this.options.padding = $splat(this.options.padding);
				this.options.topPadding = $pick(this.options.topPadding, this.options.padding[0]);
				this.options.rightPadding = $pick(this.options.rightPadding, this.options.padding[1], this.options.padding[0]);
				this.options.bottomPadding = $pick(this.options.bottomPadding, this.options.padding[2], this.options.padding[0]);
				this.options.leftPadding = $pick(this.options.leftPadding, this.options.padding[3], this.options.padding[1], this.options.padding[0]);
				var table = document.id(this.options.dataTable);
				if (table) {
						this.data = new HueChart.Data(HueChart.buildData(table));
						table.hide();
				} else {
						this.data = new HueChart.Data(this.options.dataObject);
				}

				//Setup color manager
				this.colorManager = colorManager;
				this.colorManager.define(this.options.url, this.options.colorArray);
		},

		//Resize graph to width and height.
		resize: function(width, height) {
				this.width = width;
				this.height = height;
				this.render();
		},

		//Hide graph.
		hide: function(){
				this.element.hide();
		},
		
		//Show graph.
		show: function(){
				this.element.show();
		},
		
		//Render graph.
		render: function() {
				this.vis = new pv.Panel();
				this.vis.width(this.width)
						.height(this.height);
				this.vis.$dom = this.element.empty();
				this.fireEvent('setupChart', this.vis);
				this.vis.render();
		},
		
		//Returns selected data index
		getSelectedIndex: function() {
				return this.selected_index;
		},
		
		//Sets selected data index
		setSelectedIndex: function(index) {
				this.selected_index = index;
		},
		
		//Change full data object
		setData: function(data) {
				this.data = new HueChart.Data(data);
				delete this.currentData;
				if (this.hasData() && this.initializeData) this.initializeData();
		},

		//Set the currentData, which is the data currently being displayed, assuming it is different from the base data.  Should be a subset of the main data object. 
		setCurrentData: function(data) {
				this.currentData = new HueChart.Data(data);
		},
		
		//Return a data object.
		//current- (boolean) if true and there is a currentData object, return the currentData object.
		//Otherwise, return the base data object.
		getData: function(current) {
				if (current && this.currentData) return this.currentData;
				return this.data;
		},
		
		//Delete this.currentData to reset data to the base data.
		resetData: function() {
				delete this.currentData;
		},

		//Add data series
		addData: function(data, dateProperty) {
			return this.data.addData(data, dateProperty);
		},

		hasData: function() {
			return this.getData().getLength() > 0;
		},

		//Check that there is an event handler registered for an event
		hasEvent: function(name) {
				return this.$events[name] && this.$events[name].length;
		},

		//Get color given a series
		getColor: function(series) {
				return this.colorManager.get(this.options.url, series);
		}
});

//Wrapper for data object to be charted.
//Adds various functions on the data.
HueChart.Data = new Class({
		
		initialize: function(data) {
				//Check if it's a HC.Data object, and return the data if it is. 
				if(data._getExtreme) return data;
				//Otherwise, set the dataObjects property to data.
				this.dataObjects = data;
		},

		//Add data series
		//Argument is an array of objects containing dateProperty, and series entries
		//Data object should be same time frame as current dataSet
		//Returns boolean reflecting whether or not data was successfully added
		addData: function(data, dateProperty) {
			var dataAdded = false;
		    //Integrate data into current data object.
			var dataLength = data.length;
			var dataObject, datum;
			for (var i = 0; i < dataLength; i++) {
				dataObject = this.dataObjects[i];
				datum = data[i];
				if (dataObject[dateProperty].valueOf() == datum[dateProperty]) {
					//Remove dateProperty so we don't overwrite it.
					delete datum[dateProperty];
					dataObject = $merge(dataObject, datum);
					if(!dataAdded) dataAdded = true;
			    }
			}
			return dataAdded;
		},
		
		//Function to sort by dates and convert date strings into date objects.
		//Also creates ms, a useful integer value for graphing.
		//Accepts date formats parsable in Native/Date.js, or integral ms values.
		prepareDates: function(dateProperty) {
				//Convert date string in each object to date object
				this.dataObjects.each(function(d) {
						d[dateProperty] = this.parseDate(d[dateProperty]);
				}.bind(this));
				//Sort data by date property.
				this.sortByProperty(dateProperty);
				//Store first date for comparison.
				//Create ms, so as to not have to continually look it up.
				this.dataObjects.each(function(d) {
						d.ms = d[dateProperty].valueOf();
				}.bind(this));
		},
		
		//Parse date -- accepts date formats parsable in Native/Date.js, or integral ms values.
		parseDate: function(d) {
				//Check if dateProperty value is parsable as string.
				//Parse as string if it is, otherwise parse as ms value.
				var parseResult = Date.parse(d);
				if (parseResult.isValid()) {
						return parseResult;
				} else {
						parseResult = Date.parse(d.toInt());
						if (parseResult.isValid()) return parseResult;
				}
		},

		//Sort data by some property within it.
		sortByProperty: function(property) {
				this.dataObjects.sort(function(a, b) {
						if (a[property] < b[property]) return -1;
						if (a[property] == b[property]) return 0;
						if (a[property] > b[property]) return 1;
				});
		},

		//Sort data by the return value of a function which takes as an argument an element of the data array. 
		sortByFunction: function(sortFn) {
				this.dataObjects.sort(function(a, b) {
						if (sortFn(a) < sortFn(b)) return -1;
						if (sortFn(a) == sortFn(b)) return 0;
						if (sortFn(a) > sortFn(b)) return 1;
				});
		},

		//Get the maximum value of the values in the data table.
		getMaxValue: function(seriesToInclude) {
				return this._getExtreme('max', seriesToInclude, pv.max);
		},
		
		//Get the peak sum of the values in a given object in the data table.
		getPeakSum: function(seriesToInclude) {
				return this._getExtreme('peak', seriesToInclude, pv.max);
		},
		
		//Get min value of the values in the data table.
		getMinValue: function(seriesToInclude) {
				return this._getExtreme('min', seriesToInclude, pv.min);
		},
		
		//Get the min sum of the values in a 
		getMinSum: function(seriesToInclude) {
				return this._getExtreme('valley', seriesToInclude, pv.min);
		},
		
		getSeriesSum: function(series) {
				return pv.sum(this.dataObjects, function(d) { return d[series]; });
		},
			   
		//Get an extreme value from the data table.
		//seriesToInclude can be a single field in the data object or an array of fields. 
		_getExtreme:  function(type, seriesToInclude, extremeFn) {
				seriesToInclude = $splat(seriesToInclude);
				//Use extremeFn, which should be either pv.min or pv.max to iterate over data objects.
				return extremeFn(this.dataObjects, function(d) {
						//If looking for min, initialize currentExtreme to max value.
						//If looking for max, initialize currentExtreme to min value.
						var currentExtreme = (extremeFn == pv.min ? Number.MAX_VALUE : Number.MIN_VALUE);
						//Iterate through the data object
						Hash.each(d, function(value, key) {
								//If the key is one of the fields we're inspecting.
								if (seriesToInclude.contains(key)) {
										switch (type){
												case 'max':
														if (Number(value) > currentExtreme) currentExtreme = Number(value);
														break;
												case 'min':
														if (Number(value) < currentExtreme) currentExtreme = Number(value);
														break;
												case 'peak':
														currentExtreme += Number(value);
														break;
												case 'valley':
														currentExtreme += Number(value);
														break;
										}

								};
						});
						return currentExtreme; 
				});
		},
		
		//Return the array of data objects
		getObjects: function() {
				return this.dataObjects;
		},

		//Uses the protovis pv.normalize function to return an array containing values which sum to 1
		//Essentially returns an array containing the percentage that each dataObject's field value
		//contributes to the sum of the dataObjects' array field values.

		getNormalizedForField: function(field) {
				pv.normalize(this.dataObjects, function(d) { return d[field]; });        
		},

		getLength: function() {
				return this.dataObjects.length;
		},

		//Return a HueChart.Data object containing the dataObjects from the first index to the last index.
		//Optional argument flatArray - boolean.  If true, will return a flatArray object. 
		getRange: function(first, last, flatArray) {
				var sliced = this.dataObjects.slice(first, last);
				if (flatArray) return sliced;
				return new HueChart.Data(sliced);
		},
		

		// TODO: This should become class static constant instead of object property
		tickIntervals: {
			ms: [1, 10, 100, 500],
			second: [1, 5, 10, 15, 30],
			minute: [1, 2, 5, 10, 15, 30],
			hour: [1, 3, 6, 12],
			day: [1, 3, 7, 14, 28],
			month: [1, 2, 3, 6],
			year: [1, 2, 5, 10, 20, 50, 100]
		},
		tickUniformUnits: ['ms','second','minute','hour','day'],
		
		// TODO: This should become class static constant instead of object property
		
		
		dataMsProperty: "ms",
		/* getTicks --
				Returns an array of data objects to be marked as ticks on the domain (x) axis.
				Arguments:
				maxTickCount (integer) - the upper bound on size of the return array
				dateProperty (string) - the property which stores date objects
				startMs (integer) - milliseconds since some reference time
				endMs (integer) - milliseconds since the same reference time
		*/
		getTicks: function(maxTickCount, dateProperty, startMs, endMs) {
			var maxIntervalCount = maxTickCount + 1;
			
			if (!$defined(startMs)) {
				startMs = this.dataObjects[0][this.dataMsProperty];
				endMs = this.dataObjects.getLast()[this.dataMsProperty];
			}
			
			var domainMs = endMs - startMs;
			var adjustedDomainMs, unit, unitMs, intervals, interval, intervalMs, tickObject;
			
			var uniformUnitsLength = this.tickUniformUnits.length;
			unitsLoop:
				for (var i=0; i<uniformUnitsLength; i++) {
					unit = this.tickUniformUnits[i];
					unitMs = Date.units[unit]();
					intervals = this.tickIntervals[unit];
					if (intervals.getLast() * unitMs * maxIntervalCount > domainMs) {
						// Very good chance we've found the right unit; check each interval
						for (var j=0; j<intervals.length; j++) {
							interval = intervals[j];
							intervalMs = interval * unitMs;
							adjustedDomainMS = domainMs + startMs % unitMs;
							if (intervalMs * maxIntervalCount > adjustedDomainMS) {
								break unitsLoop;
							}
						}
					}
				}
			
			var ticksMs = [];
			
			if (i < uniformUnitsLength) {
				// Broke free from uniform unit loop; selected unit has uniform intervals.
				// Get tick marks with intervals aligned at 0 mod intervalMs
				var tickMs = startMs + intervalMs - startMs % intervalMs;
				var tickDate = Date.parse(tickMs);
				while (tickMs < endMs) {
					tickObject = {};
					tickObject[this.dataMsProperty] = tickMs;
					tickObject[dateProperty] = tickDate;
					tickMs += intervalMs;
					tickDate = tickDate.clone().increment('ms', intervalMs);
					ticksMs.push(tickObject);
				}
			} else {
				// Months/year tick intervals not uniform in number of days (or ms)
				unit = null;
				
				var date = Date.parse(startMs);
				var endDate = Date.parse(endMs);
				
				var startUnitIndex = date.get('month');
				var domainSize = (endDate.get('year') - date.get('year')) * 12 +
					endDate.get('month') - startUnitIndex;
				
				intervals = this.tickIntervals['month'];
				if (intervals.getLast() * maxIntervalCount > domainSize) {
					// Very good chance we should use months; check each interval
					for (j=0; j<intervals.length; j++) {
						interval = intervals[j];
						adjustedDomainSize = domainSize + startUnitIndex % interval;
						if (interval * maxIntervalCount > adjustedDomainSize) {
							unit = 'month';
							break;
						}
					}
				}
				
				if (!unit) {
					startUnitIndex = date.get('year');
					domainSize = endDate.get('year') - startUnitIndex;
					
					intervals = this.tickIntervals['year'];
					for (j=0; true; j++) {
						// If max interval not big enough, then double interval until big enough
						interval = intervals[j] || interval * 2;
						adjustedDomainSize = domainSize + startUnitIndex % interval;
						if (interval * maxIntervalCount > adjustedDomainSize) {
							unit = 'year';
							break;
						}
					}
				}
				
				// Adjust date to align tick marks at 0 mod interval
				date.increment(unit, interval - startUnitIndex % interval);
				
				// Get tick marks using Date.increment and convert each to ms
				var dateMs;
				tickObjects = [];
				do {
					tickObject = {};
					dateMs = date.valueOf();
					tickObject[this.dataMsProperty] = dateMs;
					tickObject[dateProperty] = date.clone();
					ticksMs.push(tickObject);
					date.increment(unit, interval);
				} while (dateMs < endMs);
			}
			
			return {
				'ticks': ticksMs,
				'unit': unit
			};
		}
});

//Function to build an array of data objects from a table.
//The headers of the table are used as the property names of the data objects.
//Table format
/*
   Header1 Header2 Header3 Header4
   val1-1  va11-2  value1-3  value1-4
   val2-1  val2-2  val2-3  val2-4
*/
HueChart.buildDataFromTable = function(table) {
		data = [];
		//Iterate through headers.
		var headers = $$(table.getElements('th')).map(function(header) {
			   return header.get('text');
		});
		//Iterate through table row and cells.
		$$(table.getElements('tbody tr')).each(function(row) {
				var datum = {};
				$$(row.getElements('td')).each(function(cell, i) {
					   datum[headers[i]] = cell.get('text'); 
				});
				data.push(datum);
		});
		return data;
};

})();
