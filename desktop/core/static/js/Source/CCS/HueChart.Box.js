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
- More/DynamicTips

provides: [ HueChart.Box ]
...
*/
(function() {
var getXValueFn = function(field) {
        return function(data) {
                if (field) return data[field];
                else return data;
        };
};

HueChart.Box = new Class({

        Extends: HueChart,

         options: {
                series: [], //the array of data series which are found in the chart data,
                xProperty: 'x', //the field in the data table which should be used for determining where points are on the xAxis
                dates: {x: false, y: false}, //is the data in an axis a date ? 
                dateSpans:{x: 'day'}, //if an axis is a date, what time span should the tick marks for that axis be shown in
                positionIndicator: false, //should the position indicator be shown ?
                ticks: {x: false, y: false}, //should tick marks be shown ?
                showLabels: false, //should axis labels be shown ?
                tickColor: "#555", //the color of the tick marks
                dateFormat: "%b %d", //the format that should be used when displaying dates
                verticalTickSpacing: 35, //the distance between vertical ticks
                xTickHeight: 10, //the height of the xTick marks.
                labels:{x:"X", y: "Y"}, //the labels that should be used for each axis
                selectBarColor: "rgba(0, 0, 0, .2)", //the color that should be used to fill selections in this chart
                selectBarBorderColor: "rgba(0, 0, 0, 1)", //the color that should be used as a border for selections in this chart
                selectedIndicatorColor: "black", //color that should be used to show the position of the selected index, when using the position indicator
                highlightedIndicatorColor: "rgba(255, 255, 255, .5)",
                yType: 'string', //the type of value that is being graphed on the y-axis,
                showPointValue: false, //show the value at the point when moused over
                selectable: false, //make the chart selectable
                //initialSelectValue: {left: 0, right: 0}, //the initial chart selection, must be same type as x values 
                draggable: false, //make the chart selection draggable,
                fireSelectOnDrag: true //fires the select event on completion of a drag
                /*
                onPointMouseOut: function that should be run when the mouse is moved out of the chart
                onPointMouseOver: function that should be run when the mouse is moved over a datapoint, takes the dataPoint and index as arguments
                onPointClick: function that should be run when the mouse is clicked on a datapoint, takes the dataPoint and index as arguments
                onSeriesMouseOver: function that should be run when the mouse is moved over a dataSeries, takes an object containing the seriesName and value at that point as argument.
                onSeriesClick: function that should be run when the mouse is clicked on a data series, takes an object containing the seriesName and value at that as an argument.
                onSpanSelect: function that should be run when a segment of the chart is selected.  Takes a left object and a right object as arguments, each of which contains the corresponding index and data object. 
                */
        },
        
        initialize: function(element, options) {
                this.parent(element, options);
                this.selected_index = -1;
                this.highlighted_index = -1;
                if(this.options.dates.x) {
                        //If the xProperty is a date property, prepare the dates for sorting
                        //Change the xProperty to the new property designed for sorting dates
                        this.getData(true).prepareDates(this.options.xProperty);
                        //Set dateProperty to the initial xProperty, this will hold a date object which will be used for rendering dates as strings 
                        this.dateProperty = this.options.xProperty;
                        this.options.xProperty = 'ms_from_first';
                } else {
                        //Otherwise sort by the x property.
                        this.getData(true).sortByProperty(this.options.xProperty);
                }
                //Create tip to show if showPointValue is true.
                if (this.options.showPointValue) {
                        this.tip = new DynamicTips(this.element, {
                                className: 'huechart tip-wrap',
                                title: $lambda("Title"),
                                text: $lambda("Text"),
                                showOnEnter: false
                        });
                        this.tip.hide();
                        this.addEvent('seriesMouseOver', this.updatePointValue);
                }
                //Initialize dragState and selectState
                this.dragState = {x: 0, y: 0};
                this.selectState = {x: 0, dx: 0};
                //Set this.draggable and this.selectable to reflect whether or not the chart has these capabilities, based on the existence of events and/or options.
                this.draggable = this.options.draggable || this.hasEvent('drag') || this.hasEvent('dragStart') || this.hasEvent('dragEnd');
                this.selectable = this.options.selectable || this.draggable || this.hasEvent('spanSelect') || this.hasEvent('select') || this.hasEvent('selectStart') || this.hasEvent('selectEnd');
                //When the setupChart event is fired, the full ProtoVis visualization is being set up, in preparation for render.
                //The addGraph function is responsible for adding the actual representation of the data, be that a group of lines, or a group of area graphs.
                this.addEvent('setupChart', function(vis) {
                        //Set up the scales which will be used to convert values into positions for graphing.
                        this.setScales(vis);
                        //Add representation of the data.
                        this.addGraph(vis);
                        //Add tick marks (rules on side and bottom) if enabled
                        if (this.options.ticks.x || this.options.ticks.y) this.setTicks(vis);
                        //Add axis labels if enabled
                        if (this.options.showLabels) this.setLabels(vis);
                        //Add position indicator if enabled
                        if (this.options.positionIndicator) this.setPositionIndicators(vis);
                        //Create panel for capture of events
                        this.eventPanel = vis.add(pv.Panel).fillStyle("rgba(0,0,0,.001)");
                        //If there's a mouse event, add the functionality to capture these events.
                        if (this.hasEvent('pointMouseOut') && this.hasEvent('pointMouseOver') || this.hasEvent('pointClick') || this.options.showPointValue) this.addMouseEvents(vis);
                        //If there is a selection or drag event of any sort make the graph selectable.
                        if (this.selectable) this.makeSelectable(vis);
                }.bind(this));
        },
        
        //Set the scales which will be used to convert data values into positions for graph objects
        setScales: function(vis) {
                //Get the minimum and maximum x values.
                var xMin = this.getData(true).getMinValue(this.options.xProperty);
                var xMax = this.getData(true).getMaxValue(this.options.xProperty);
                //Get the maximum of the values that are to be graphed
                var maxValue = this.getData(true).getMaxValue(this.options.series);
                this.xScale = pv.Scale.linear(xMin, xMax).range(this.options.leftPadding, this.width - this.options.rightPadding);
                this.yScale = pv.Scale.linear(0, maxValue * 1.2).range(this.options.bottomPadding, (this.height - (this.options.topPadding)));
                //Defining a yValueReverse function here, since it is so closely related to the scale.
                //This function reverses a value returned by yScale.invert to a value that corresponds to the scale from 0 to maxValue, rathen than from maxValue to 0.
                this.yValueReverse = function(reversedValue) {
                        var paddingBasedDifference = this.yScale.invert(this.options.bottomPadding - this.options.topPadding) - this.yScale.invert(0);
                        return ((reversedValue - maxValue * 1.2) * -1) - paddingBasedDifference;
                };
        },
        
        //Draw the X and Y tick marks.
        setTicks:function(vis) {
                if (this.options.ticks.x) {
                        //Add X-Ticks.
                        //Create tick array.
                        var xTicks = (this.options.dates.x ? this.getData(true).createTickArray(7, this.options.dateSpans.x, this.dateProperty) : this.xScale.ticks(7));
                        //Function will return the correct xValue dependent on whether or not x is a date
                        var getXValue = getXValueFn(this.options.dates.x ? this.options.xProperty : null);
                        //Create rules (lines intended to denote scale)
                        vis.add(pv.Rule)
                                //Use the tick array as data.
                                .data(xTicks)
                                //The bottom of the rule should be at the bottomPadding - the height of the rule.  
                                .bottom(this.options.bottomPadding - this.options.xTickHeight)
                                //The left of the rule should be at the data object's xProperty value scaled to pixels.
                                .left(function(d) { return this.xScale(getXValue(d)); }.bind(this))
                                //Set the height of the rule to the xTickHeight
                                .height(this.options.xTickHeight)
                                .strokeStyle(this.options.tickColor)
                                //Add label to bottom of each rule
                                .anchor("bottom").add(pv.Label)
                                        .text(function(d) {
                                                //If the option is a date, format the date property field.
                                                //Otherwise, simply show it.
                                                if(this.options.dates.x) {
                                                        return d[this.dateProperty].format(this.options.dateFormat);
                                                } else {
                                                        return getXValue(d);
                                                }
                                        }.bind(this));
                }
                
                if (this.options.ticks.y) {      
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
                                //The width of the rule should be the width minus the hoizontal padding.
                                .width(this.width - this.options.leftPadding - this.options.rightPadding + 1)
                                .strokeStyle(this.options.tickColor)
                                //Add label to the left which shows the number of bytes.
                                .anchor("left").add(pv.Label)
                                        .text(function(d) { 
                                                if(this.options.yType == 'bytes') return d.convertFileSize(); 
                                                return d;
                                        }.bind(this));
                }
        },
        
        //Add X and Y axis labels.
        setLabels: function(vis) {
                //Add Y-Label to center of chart. 
                vis.anchor("center").add(pv.Label)
                        .textAngle(-Math.PI/2)
                        .text(this.options.labels.y)
                        .font(this.options.labelFont)
                        .left(12);
                
                //Add X-Label to center of chart.
                vis.anchor("bottom").add(pv.Label)
                        .text(this.options.labels.x)
                        .font(this.options.labelFont)
                        .bottom(0);
        },

        //Add bars which indicate the positions which are currently selected and/or highlighted on the box graph.
        setPositionIndicators: function(vis) {
                //Put selected_index and highlighted_index in scope.
                get_selected_index = this.getSelectedIndex.bind(this);
                get_highlighted_index = this.getHighlightedIndex.bind(this);
                var selectedColor = this.options.selectedIndicatorColor;
                var highlightedColor = this.options.highlightedIndicatorColor;
                //Add a thin bar which is approximately the height of the graphing area for each item on the graph.
                vis.add(pv.Bar)
                        .data(this.getData(true).getObjects())
                        .left(function(d) { 
                                return this.xScale(d[this.options.xProperty]); 
                        }.bind(this))
                        .height(this.height - (this.options.bottomPadding + this.options.topPadding))
                        .bottom(this.options.bottomPadding)
                        .width(2)
                        //Show bar if its index is selected or highlighted, otherwise hide it.
                        .fillStyle(function() {
                                if (this.index == get_selected_index()) return selectedColor;
                                if (this.index == get_highlighted_index()) return highlightedColor;
                                else return null;
                        });
        },

        getDataIndexFromPoint: function(axis, x) {
                if(axis == 'x') {
                        //Convert the passedin in xValue into its corresponding data value on the xScale. 
                        var mx = this.xScale.invert(x);
                        //Search the data for the index of the element at this data value.
                        var i = pv.search(this.getData(true).getObjects().map(function(d){ return d[this.options.xProperty]; }.bind(this)), Math.round(mx));
                        //Adjust for ProtoVis search
                        i = i < 0 ? (-i - 2) : i;
                        return (i >= 0 && i < this.getData(true).getLength() ? i : null);
                }
        },

        getYRange: function(y, inversionScale) {
                var scale = inversionScale || this.yScale;
                var yBuffer = 5; //Pixel buffer for usability.
                //Must use yValueReverse to reverse the mouse value because drawing happens from the bottom up.  Mouse position is from the top down.
                var invertedYValue = scale.invert(y);
                //Since range will be inverted, the array goes from greatest to least initially.
                var invertedYRange = [scale.invert(y + yBuffer), scale.invert(y - yBuffer)];
                var yValue = this.yValueReverse(invertedYValue); 
                //Convert the inverted yRange to a non-inverted yRange.
                var yRange = invertedYRange.map(function(value) { return this.yValueReverse(value); }.bind(this));
                return yRange;
        },

        getDataSeriesFromPointAndY: function(dataPoint, y) {
                var yRange = this.getYRange(y);
                //Find closest y-values
                for (var i = 0; i < this.options.series.length; i++) {
                        var item = this.options.series[i];
                        if(yRange[0] < dataPoint[item] && dataPoint[item] < yRange[1]) {
                                return {'name': item, 'value': dataPoint[item]};
                        }  
                }
                return null;
        },
         
        //Add handlers to detect mouse events.
        addMouseEvents: function(vis) {
                //Function that controls the search for data points and fires mouse positioning events. 
                var mousePositionEvent = function(eventName, position) {
                        var dataIndex = this.getDataIndexFromPoint('x', position.x);
                        if(dataIndex != null) {
                                var dataPoint = this.getData(true).getObjects()[dataIndex];
                                this.fireEvent('point' + eventName.capitalize(), [ dataPoint, dataIndex ]);
                                var dataSeries = this.getDataSeriesFromPointAndY(dataPoint, position.y);

                                this.fireEvent('series' + eventName.capitalize(), dataSeries);
                        }
                }.bind(this);
                //Create functions which handle the graph specific aspects of the event and call the event arguments.
                var outVisFn = function() {
                        this.fireEvent('pointMouseOut');
                        return vis;
                }.bind(this);
                var moveVisFn = function() {
                        mousePositionEvent('mouseOver', vis.mouse());
                        return vis;
                }.bind(this);
                var clickFn = function() {
                        //Only click if the movement is clearly not a drag.
                        if (!this.selectState || this.selectState.dx < 2) {
                                mousePositionEvent('click', vis.mouse());
                                return vis;
                        }
                }.bind(this);

                
                this.eventPanel
                        .events("all")
                        .event("mouseout", outVisFn)
                        .event("mousemove", moveVisFn)
                        .event("click", clickFn);

        },
        
        //Given points on an axis, return an array of data objects for each point
        getObjectsForPoints: function(axis /*points*/) {
                var argArray = $A(arguments).slice(1);
                return argArray.map(function(point) {
                        var toGraph = this.adjustToGraph(axis, point);
                        var index = this.getDataIndexFromPoint(axis, toGraph);
                        return { index: index, data: this.getData(true).getObjects()[index] };
                }.bind(this));
                
        },
        
        //Make selection in graph draggable
        makeSelectionDraggable: function() {
                //Attach the ProtoVis drag behavior to the select bar and attach events for drag occurrences
                this.selectBar = this.selectBar 
                //Set cursor to be a mouse pointer
                .cursor("move")
                .event("mousedown", pv.Behavior.drag())
                        .event("drag", function() {
                                this.fireEvent('drag');
                        }.bind(this))
                        .event("dragstart", function() {
                                this.fireEvent('dragStart');
                        }.bind(this))
                        .event("dragend", function() {
                                if (this.options.fireSelectOnDrag) {
                                        //Get objects for edge points
                                        var leftPoint = this.dragState.x;
                                        var rightPoint = this.dragState.x + this.selectWidth;
                                        var objectArray = this.getObjectsForPoints('x', leftPoint, rightPoint);
                                        this.fireEvent('spanSelect', objectArray);
                                }
                                this.fireEvent('dragEnd');
                        }.bind(this));
        },
        
        //Make graph selectable
        makeSelectable: function(){
                //Create select bar
                this.selectBar = this.eventPanel.add(pv.Bar);
                
                //If there is a need for draggability, make the selection draggable.
                if (this.draggable) this.makeSelectionDraggable();
                
                //Set the basic settings for the selectBar 
                this.selectBar = this.selectBar
                                //Initialize dragState as selectBar's data.
                                .data([this.dragState])
                                //Set fillStyle to the selectBarColor
                                .fillStyle(this.options.selectBarColor)
                                //Set height so that it only covers the chart
                                .height(this.height - (this.options.bottomPadding + this.options.topPadding))
                                //Set top to start at top padding
                                .top(this.options.topPadding)
                                //Set line width to 1 pixel
                                .lineWidth(1)
                                //Set the left value to the dragState's x value.
                                .left(function(d) {
                                        return d.x;
                                });
                
                //Initialize selection to nothing
                this.selectRange(0, 0);
                //If the initialSelectValue has been set, select that range.
                if(this.options.initialSelectValue) {
                        //If date, convert to date
                        if (this.options.dates.x) {
                                startValue = this.data.getMsFromFirst(this.data.parseDate(this.options.initialSelectValue.start));
                                endValue = this.data.getMsFromFirst(this.data.parseDate(this.options.initialSelectValue.end));
                        }
                        //Convert to points on xScale
                        startX = this.xScale(startValue);
                        endX = this.xScale(endValue);
                        this.selectRange(startX, endX);
                        this.selectBar.strokeStyle(this.options.selectBarBorderColor);
                }
                //Initialize eventPanel's select events.
                this.eventPanel
                        .data([this.selectState])
                        .event("mousedown", pv.Behavior.select());
                         
                //If d.dx has a value greater than 0...meaning we're in the middle of a
                //drag, adjust the width value to the graph.
                //Otherwise give it a width of 0.
                this.eventPanel
                        .event("selectstart", function() {
                                this.selectBar.width(0);
                                this.selectBar.strokeStyle(this.options.selectBarBorderColor);
                                this.fireEvent('selectStart');
                        }.bind(this))
                        .event("select", function() {
                                this.selectRange(this.adjustToGraph('x', this.selectState.x), this.adjustToGraph('x', this.selectState.x + this.selectState.dx));
                                this.fireEvent('select');
                        }.bind(this))
                        .event("selectend", function() {
                                if (this.selectState.dx > 2) {
                                        //Get objects for edge points
                                        //left - this.selectState.x
                                        //right - this.selectState.dx
                                        var objectArray = this.getObjectsForPoints('x', this.selectState.x, this.selectState.x + this.selectState.dx);
                                        this.fireEvent('spanSelect', objectArray);
                                }
                                this.fireEvent('selectEnd');
                        }.bind(this));
        },
        
        //Selects a pixel range in the graph.
        selectRange: function(leftValue, rightValue) {
                this.dragState.x = this.adjustToGraph('x', leftValue);
                this.selectWidth = rightValue - leftValue;
                this.selectBar
                        .width(rightValue - leftValue);
        },

        //Adjusts a point to the graph.  Ie...if you give it a point that's greater than or less than
        //points in the graph, it will reset it to points within the graph.
        //This is easily accomplished using the range of the graphing scales.
        adjustToGraph: function(axis, point){
                var scale;
                switch(axis){
                        case 'x': scale = this.xScale;
                                    break;
                        case 'y': scale = this.yScale;
                                    break;
                        //Return if axis is not x or y.
                        default: return;
                }
                //scale.range() returns an array of two values.
                //The first is the low end of the range, while the second is the highest.
                var low = scale.range()[0];
                var high = scale.range()[1];
                //Return low or high is the value is outside their interval.  Otherwise, return point.
                if (point < low) return low;
                if (point > high) return high;
                return point;
        },
        
        //Updates the display of the currently visible tip
        updatePointValue: function(series) {
                if (series != null) {
                        var tipColor = new Element('div', {'class': 'tip-series-color'});
                        var tipBlock = new Element('div', {'class': 'tip-block'});
                        tipBlock.set('text', series.name);
                        tipColor.inject(tipBlock, 'top');
                        tipColor.setStyle('background-color', this.getColor(series.name));
                        this.tip.setTitle(tipBlock);
                        this.tip.setText(this.options.yType == 'bytes' ? series.value.toInt().convertFileSize() : series.value);
                        var tipElem = this.tip.toElement();
                        if(!tipElem.getParent() || !document.body.hasChild(tipElem))tipElem.dispose();
                        this.tip.show();
                } else {
                        this.tip.hide();
                }
        }, 

        //Returns highlighted data index
        getHighlightedIndex: function() {
                return this.highlighted_index;
        },

        //Sets higlighted data index
        setHighlightedIndex: function(index) {
                this.highlighted_index = index;
        },

        //Do any cleanup necessary of chart
        destroy: function() {
                if(this.tip) {
                         this.tip.toElement().destroy();
                         delete this.tip;
                }
        } 
});
})();

