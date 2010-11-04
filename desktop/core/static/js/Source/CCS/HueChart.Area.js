/*
---

script: HueChart.Area.js

description: Defines HueChart.Area, builds on HueChart.Box to produce stacked area graphs.

license: MIT-style license

authors:
 - Marcus McLaughlin

requires:
 - ccs-shared/HueChart.Box

provides: [HueChart.Area]
...
*/

//Builds a stacked area graph.
HueChart.Area = new Class({

        Extends: HueChart.Box,

        initialize: function(element, options) {
                this.parent(element, options);
                this.render();
                return;
        },

        setScales: function(vis) {
                this.parent();
                //Scale with peakSum as max, since this is a stacked chart.
                var peakSum = this.getData(true).getPeakSum(this.options.series);
                //Start yScale range from 0, rather than from the bottom padding, since the areas will be stacked on top of one another.
                this.yScale = pv.Scale.linear(0, peakSum * 1.2).range(0, (this.height - (this.options.topPadding + this.options.bottomPadding)));
                //Create yScaleTicks which has a domain which goes up to a function of peakSum and a range from the bottomPadding, to the bottom of the topPadding. 
                this.yScaleTicks = pv.Scale.linear(0, peakSum * 1.2).range(this.options.bottomPadding, this.height-this.options.topPadding);
        },

        //Build stacked area graph.
        addGraph: function(vis) {
                //Put colorArray in scope for fillStyle fn.
                var stack = vis.add(pv.Layout.Stack);
                /*  [{'date': 10, 'series1': 5, 'series2': 10, 'series3': 15},
                     {'date': 20, 'series1': 7, 'series2': 14, 'series3': 21},
                     {'date': 30, 'series1': 12, 'series2': 24, 'series3': 36}]
                From a data object which looks like the one above, create a graph
                using the values in each series[1-3] as a layer, stacked on the previous layers.
                */
                //Create a stack with its bottom at the bottom padding
                stack = stack.bottom(this.options.bottomPadding)
                        //Using as layers the values in the this.series array.
                        .layers(this.options.series)
                        //And as values the this.getData() array
                        .values(this.getData(true).getObjects())
                        //The two commands below will be run this.series.length * this.getData().length times.
                        //The x-value, in pixels, is calculated as a conversion of the data object's xProperty value using the xScale.
                        .x(function(d) {
                                return this.xScale(d[this.options.xProperty]);
                        }.bind(this))
                        //The y-value, in pixels, is calculated as a conversion of the data object's layer field value using the yScale.
                        .y(function(d, layer) {
                                return this.yScale(d[layer]);
                        }.bind(this));  
                
                //In the stack, add an area graph for every layer.
                //The stack object contains the data which was added above.
                //The stack is a layout which says, for every layer defined (above), add an area graph, offsetting it based on the layers below.
                //Appears as a signle contiguous object, but is actually a bunch of different area graphs.
                stack.layer.add(pv.Area)
                        .fillStyle(function(d, layer) {
                                return this.getColor(layer);
                        }.bind(this));
        }

});

