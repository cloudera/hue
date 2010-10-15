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
        } 
});

//Wrapper for data object to be charted.
//Adds various functions on the data.
HueChart.Data = new Class({
        
        initialize: function(dataArray) {
                this.dataObjects = dataArray;
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

        getLength: function() {
                return this.dataObjects.length;
        },
        
        //Need to figure out an answer for this.  This is very date specific.  
        //Possibly need to genericize a bit more.
        /* Get Ticks --
                take this data array and give me back an array of data objects to use as ticks.
                this array should contain no more than num_ticks values.
                the increment in which the values should be shown is timespan
        */
        //Currently requires the dates in the data object to be exact days.

        createTickArray: function(numTicks, timespan) {
                //Get the largest number of seconds.
                var mostSeconds = this.dataObjects.getLast().seconds_from_first;
                var secondsInSpan;
                //Choose the timespan -- currently only day
                switch (timespan) {
                        case 'day': 
                                secondsInSpan = 86400;
                                break;
                }
                var xTicks = [];
                //If the number of ticks that would be generated for the timespan is less than the number of ticks requested, use the current data array.
                if (mostSeconds/secondsInSpan <= numTicks) {
                        xTicks = this.dataObjects;
                } else {
                //Generate ticks.
                        //Calculate the size of the increment between ticks to produce the number of ticks. 
                        var dateIncrement = mostSeconds/numTicks;
                        var firstDate = this.dataObjects[0].sample_date;
                        //Add ticks to the xTicks array.
                        //Sample date - firstDate cloned and incremented by the increment times the iteration number.
                        //Seconds_from_first - dateIncrement multiplied by the iteration number.
                        for (var i = 0; i <= numTicks; i++) {
                                xTicks.push({
                                        sample_date: firstDate.clone().increment('second', dateIncrement * i),
                                        seconds_from_first: dateIncrement * i
                                });
                        }
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

