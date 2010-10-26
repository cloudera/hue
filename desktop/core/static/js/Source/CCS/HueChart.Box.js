/*
---

script: HueChart.Box.js

description: Defines HueChart.Box, which builds on HueChart and serves as a base class to build charts which are rectangular in nature, having x and y axes.

license: MIT-style license

authors:
- Marcus McLaughlin

requires:
- protovis/Protovis
- More/Date
- Core/Events
- Core/Options
- ccs-shared/Number.Files
- ccs-shared/HueChart

provides: [ HueChart.Box ]

...
*/

HueChart.Box = new Class({

        Extends: HueChart,

         options: {
                //series: [], //the array of data series which are found in the chart data,
                //xField: '', //the field in the data table which should be used as the xAxis label, and for determining where points are on the xAxis
                xIsDate: false, //is the xField a date ?
                positionIndicator: false, //should the position indicator be shown ?
                ticks: false, //should tick marks be shown ?
                labels: false, //should axis labels be shown ?
                tickColor: "#555", //the color of the tick marks
                dateFormat: "%b %d", //the format that should be used when displaying dates
                verticalTickSpacing: 35, //the distance between vertical ticks
                yFieldDisplayProcessor: function(field) {
                        return field.replace("_", " ").capitalize();
                }, //fn to use to process the yField for display, field is this.options.yField
                xTickHeight: 10,
                xLabel: "Date"
                /*
                onPointMouseOut: function that should be run when the mouse is moved out of the chart
                onPointMouseOver: function that should be run when the mouse is moved over a datapoint, takes the dataPoint and index as arguments
                onPointClick: function that should be run when the mouse is clicked on a datapoint, takes the dataPoint and index as arguments
                */
        },
        

        initialize: function(element, options) {
                this.parent(element, options);
                var requiredOptions = ["series", "xField"];
                requiredOptions.each(function(opt) {
                        if (!$defined(this.options[opt])) console.error("The required option " + opt + " is missing from a HueChart.Box instantiation.");
                }.bind(this));
                this.selected_index = -1;
                if(this.options.xIsDate) {
                        //If the xField is a date property, prepare the dates for sorting
                        //Change the xField to the new property designed for sorting dates
                        this.getData(true).prepareDates(this.options.xField);
                        this.options.xField = 'seconds_from_first';
                } else {
                        //Otherwise sort by the x property.
                        this.getData(true).sortByProperty(this.options.xField);
                }
                //When the setupChart event is fired, the full ProtoVis visualization is being set up, in preparation for render.
                //The addGraph function is responsible for adding the actual representation of the data, be that a group of lines, or a group of area graphs.
                this.addEvent('setupChart', function(vis) {
                        //Set up the scales which will be used to convert values into positions for graphing.
                        this.setScales(vis);
                        //Add representation of the data.
                        this.addGraph(vis);
                        //Add tick marks (rules on side and bottom) if enabled
                        if (this.options.ticks) this.setTicks(vis);
                        //Add axis labels if enabled
                        if (this.options.labels) this.setLabels(vis);
                        //Add position indicator if enabled
                        if (this.options.positionIndicator) this.setPositionIndicator(vis);
                        //If there's an event, add the event bar to capture these events.
                        if (this.$events.pointMouseOut && this.$events.pointMouseOver || this.$events.pointClick) this.addEventBar(vis);
                }.bind(this));
        },
        
        //Set the scales which will be used to convert data values into positions for graph objects
        setScales: function(vis) {
                //Get the minimum and maximum x values.
                var xMin = this.getData(true).getMinValue(this.options.xField);
                var xMax = this.getData(true).getMaxValue(this.options.xField);
                //Get the maximum of the values that are to be graphed
                var maxValue = this.getData(true).getMaxValue(this.options.series);
                this.xScale = pv.Scale.linear(xMin, xMax).range(this.options.leftPadding, this.width - this.options.rightPadding);
                this.yScale = pv.Scale.linear(0, maxValue * 1.2).range(this.options.bottomPadding, (this.height - (this.options.topPadding)));
        },
        
        //Draw the X and Y tick marks.
        setTicks:function(vis) {
                //Add X-Ticks.
                //Create tick array.
                var xTicks = (this.options.xIsDate ? this.getData(true).createTickArray(7, 'day') : this.xScale.ticks(7));
                //Create rules (lines intended to denote scale)
                vis.add(pv.Rule)
                        //Use the tick array as data.
                        .data(xTicks)
                        //The bottom of the rule should be at the bottomPadding - the height of the rule.  
                        .bottom(this.options.bottomPadding - this.options.xTickHeight)
                        //The left of the rule should be at the data object's xField value scaled to pixels.
                        .left(function(d) { return this.xScale(d[this.options.xField]); }.bind(this))
                        //Set the height of the rule to the xTickHeight
                        .height(this.options.xTickHeight)
                        .strokeStyle(this.options.ruleColor)
                        //Add label to bottom of each rule
                        .anchor("bottom").add(pv.Label)
                                .text(function(d) {
                                        //If the option is a date, format the date property field.
                                        //Otherwise, simply show it.
                                        if(this.options.xIsDate) {
                                                return d.sample_date.format(this.options.dateFormat);
                                        } else {
                                                return d[this.options.xField];
                                        }
                                }.bind(this));
               
                //Add Y-Ticks
                //Calculate number of yTicks to show.
                //Approximate goal of 35 pixels between yTicks.
                var yTickCount = (this.height - (this.options.bottomPadding + this.options.topPadding))/this.options.verticalTickSpacing;
                //In some box-style charts, there is a need to have a different scale for yTicks and for y values.
                //If there is a scale defined for yTicks, use it, otherwise use the standard yScale.
                var tickScale = this.yScaleTicks || this.yScale;
                //Create rules
                vis.add(pv.Rule)
                        //Always show at least two ticks.
                        //tickScale.ticks returns an array of values which are evenly spaced to be used as tick marks.
                        .data(tickScale.ticks(yTickCount > 1 ? yTickCount : 2))
                        //The left side of the rule should be at leftPadding pixels.
                        .left(this.options.leftPadding)
                        //The bottom of the rule should be at the tickScale.ticks value scaled to pixels.
                        .bottom(function(d) {return tickScale(d);}.bind(this))
                        //The width of the rule should be the width minuis the hoizontal padding.
                        .width(this.width - this.options.leftPadding - this.options.rightPadding + 1)
                        .strokeStyle("#555")
                        //Add label to the left which shows the number of bytes.
                        .anchor("left").add(pv.Label)
                                .text(function(d) { 
                                        if(this.options.yField == 'bytes') return d.convertFileSize(); 
                                        return d;
                                }.bind(this));
        },
        
        //Add X and Y axis labels.
        setLabels: function(vis) {
                //Add Y-Label to center of chart. 
                vis.anchor("center").add(pv.Label)
                        .textAngle(-Math.PI/2)
                        .text(function() {
                                return this.options.yFieldDisplayProcessor(this.options.yField.replace("_", " ").capitalize());
                        }.bind(this))
                        .font(this.options.labelFont)
                        .left(12);
                
                //Add X-Label to center of chart.
                vis.anchor("bottom").add(pv.Label)
                        .text(this.options.xLabel)
                        .font(this.options.labelFont)
                        .bottom(0);
        },

        //Add a bar which indicates the position which is currently selected on the bar graph.
        setPositionIndicator: function(vis) {
                //Put selected_index in scope.
                get_selected_index = this.getSelectedIndex.bind(this);
                //Add a thin black bar which is approximately the height of the graphing area for each item on the graph.
                vis.add(pv.Bar)
                        .data(this.getData(true).getObjects())
                        .left(function(d) { 
                                return this.xScale(d[this.options.xField]); 
                        }.bind(this))
                        .height(this.height - (this.options.bottomPadding + this.options.topPadding))
                        .bottom(this.options.bottomPadding)
                        .width(2)
                        //Show bar if its index is selected, otherwise hide it.
                        .fillStyle(function() {
                                if(this.index == get_selected_index()) return "black";
                                else return null;
                        });
        },
        
        //Add bar detecting mouse events.
        addEventBar: function(vis) {
                //Create functions which handle the graph specific aspects of the event and call the event arguments.
                var outVisFn = function() {
                        this.fireEvent('pointMouseOut');
                        return vis;
                }.bind(this);
                var getDataIndexFromMouse = function() {
                        //Convert the mouse's xValue into its corresponding data value on the xScale. 
                        var mx = this.xScale.invert(vis.mouse().x);
                        //Search the data for the index of the element at this data value.
                        var i = pv.search(this.data.getObjects().map(function(d){ return d[this.options.xField]; }.bind(this)), Math.round(mx));
                        //Adjust for ProtoVis search
                        i = i < 0 ? (-i - 2) : i;
                        return (i >= 0 && i < this.data.getLength() ? i : null);
                }.bind(this);
                var moveVisFn = function() {
                        var dataIndex = getDataIndexFromMouse();
                        //Fire pointMouseOver if the item exists
                        if(dataIndex) {
                                this.fireEvent('pointMouseOver', [this.getData(true).getObjects()[dataIndex], dataIndex]);
                        }
                        return vis;
                }.bind(this);
                var clickFn = function() {
                        var dataIndex = getDataIndexFromMouse();
                        //Fire pointClick if the item exists
                        if(dataIndex != null) {
                                this.fireEvent('pointClick', [ this.data.getObjects()[dataIndex], dataIndex ]);
                                        this.fireEvent('pointClick', [ this.getData(true).getObjects()[dataIndex], dataIndex ]);
                        }
                        return vis;
                }.bind(this);
                vis.add(pv.Bar)
                        .fillStyle("rgba(0,0,0,.001)")
                        .event("mouseout", outVisFn)
                        .event("mousemove", moveVisFn)
                        .event("click", clickFn);
        }
        
});


