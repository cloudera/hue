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

provides: [ HueChart ]

...
*/
//
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
                /*width: the initial width of the chart (required),
                  height: the initial height of the chart (required),
                  dataTable: the table containing the chart data,
                  dataObject: array of data objects,
                  One of dataTable or dataObject is required
                  onSetupChart: function that runs when the protovis rendering information is being set up, but before the protovis object is rendered, takes the protovis objects as an argument
                */
                  bottomPadding: 0, // the padding between the bottom of the element, and the bottom of the graph,
                  topPadding: 0, // the padding between the top of the element, and the left of the graph,
                  leftPadding: 0, // the padding between the left of the element, and the left of the graph,
                  rightPadding: 0 // the padding between the right of the element, and the right of the graph,
        },


        initialize: function(element, options) {
                this.setOptions(options);
                this.element = document.id(element);
                //Check for required options
                var requiredOptions = ["width", "height"];
                requiredOptions.each(function(opt) {
                        if (!$defined(this.options[opt])) console.error("The required option " + opt + " is missing from a HueChart instantiation.");
                }.bind(this));
                if (!(this.options.dataTable || this.options.dataObject)) {
                        console.error("There is a HueChart instantiation which has no data source.");
                }
                //Width and height will potentially change often, make them instance variables.
                this.width = this.options.width;
                this.height = this.options.height;
                
                var table = document.id(this.options.dataTable);
                if (table) {
                        this.data = new HueChart.Data(HueChart.buildData(table));
                        table.hide();
                } else {
                        this.data = new HueChart.Data(this.options.dataObject);
                }
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

        //Check that there is an event handler registered for an event
        hasEvent: function(name) {
                return this.$events[name] && this.$events[name].length;
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
        
        //Function to sort by dates and convert date strings into date objects.
        //Also creates seconds_from_first, a useful integer value for graphing.
        prepareDates: function(dateProperty) {
                //Convert date string to date object.
                this.dataObjects.each(function(d) {
                        d[dateProperty] = new Date().parse(d[dateProperty]);
                });
                //Sort data by date property.
                this.sortByProperty(dateProperty);
                //Store first date for comparison.
                var firstDate = this.dataObjects[0][dateProperty];
                //Create seconds from first, for comparison sake.
                this.dataObjects.each(function(d) {
                        d.seconds_from_first = firstDate.diff(d[dateProperty], 'second');
                });
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
        
        //Need to figure out an answer for this.  This is very date specific.  
        //Possibly need to genericize a bit more.
        /* Get Ticks --
                take this data array and give me back an array of data objects to use as ticks (lines representing scale).
                this array should contain no more than num_ticks values.
                the increment in which the values should be shown is timespan
        */
        //Currently requires the dates in the data object to be exact days.

        createTickArray: function(numTicks, timespan) {
                //Get the largest number of seconds.
                var mostSeconds = this.dataObjects.getLast().seconds_from_first;
                //Get the smallest number of seconds.
                var leastSeconds = this.dataObjects[0].seconds_from_first;
                //Get the total number of seconds spanned by the array.
                var totalSeconds = mostSeconds - leastSeconds;
                var secondsInSpan;
                //Choose the timespan -- currently only day
                switch (timespan) {
                        case 'day': 
                                secondsInSpan = 86400;
                                break;
                }
                var xTicks = [];
                //If the number of ticks that would be generated for the timespan is less than the number of ticks requested, use the current data array.
                if (totalSeconds/secondsInSpan <= numTicks) {
                        xTicks = this.dataObjects;
                } else {
                //Generate ticks.
                        //Calculate the size of the increment between ticks to produce the number of ticks. 
                        //Find number of timespans in an increment.
                        var spansInIncrement = parseInt((totalSeconds/secondsInSpan)/numTicks, 10);
                        //Find secondsToIncrement each value by
                        var secondsInIncrement = spansInIncrement * secondsInSpan; 
                        var firstDate = this.dataObjects[0].sample_date;
                        var firstSeconds = this.dataObjects[0].seconds_from_first;
                        //Add ticks to the xTicks array.
                        //Sample date - firstDate cloned and incremented by the increment times the iteration number.
                        //Seconds_from_first - dateIncrement multiplied by the iteration number.
                        for (var i = 0; i <= numTicks; i++) {
                                xTicks.push({
                                        sample_date: firstDate.clone().increment('second', secondsInIncrement * i),
                                        seconds_from_first: firstSeconds + (secondsInIncrement * i)
                                });
                        }
                        //Center tick marks.
                        var lastTick = xTicks.getLast();
                        var lastDataPoint = this.dataObjects.getLast();
                        //Get the number of spans between the lastDataPoint and the lastTick
                        var spansAtEnd = (lastDataPoint.seconds_from_first - lastTick.seconds_from_first)/secondsInSpan;
                        //Get number of spans to move ticks forward to result in evenly spaced, centered ticks.
                        var centerAdjustment = parseInt(spansAtEnd/2, 10);
                        xTicks.each(function(tick) {
                                tick.sample_date.increment('second', secondsInSpan * centerAdjustment);
                                tick.seconds_from_first += secondsInSpan * centerAdjustment;
                        });
                }
                return xTicks;
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
HueChart.buildData = function(table) {
        data = [];
        //Iterate through headers.
        var headers = $$(table.getElements('th')).map(function(header) {
               return header.get('text');
        });
        //Iterate through table row and cells.
        $$(table.getElements('tr')).each(function(row) {
                var datum = {};
                $$(row.getElements('td')).each(function(cell, i) {
                       datum[headers[i]] = cell.get('text'); 
                });
                data.push(datum);        
        });
        return data;
};

