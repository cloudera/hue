/*
---

script: HueChart.Circle.js

description: Defines HueChart.Circle, a base class for circular charts, which builds on HueChart.

license: MIT-style license

authors:
- Marcus McLaughlin

requires:
- ccs-shared/HueChart

provides: [HueChart.Circle]

...
*/


HueChart.Circle = new Class({
        
        Extends: HueChart,

        options: {
                radius: null// the radius of the chart, (will default to width/2)
                //graphField: '' // the field in the data object that should be graphed,
                /*
                onWedgeOver: function to be executed when the mouse is moved over a wedge of the chart, 
                onWedgeOut: function to be executed when the mouse is moved off of a wedge of the chart,
                onWedgeClick: function to be executed when a wedge of the chart is clicked
                */
        }, 

        initialize: function(element, options) {
                this.parent(element, options);
                var requiredOptions = ["graphField"];
                requiredOptions.each(function(opt) {
                        if (!$defined(this.options[opt])) console.error("The required option " + opt + " is missing from a HueChart.Box instantiation.");
                }.bind(this));
                this.selected_index = -1;
                this.radius = this.options.radius || this.width/2;
                this.addEvent('setupChart', function(vis) {
                        this.addGraph(vis);
                });
        },

        addGraph: function(vis) {
                //Hm...should this happen here or somewhere else ?
                var valueSum = this.data.getSeriesSum(this.options.graphField);
                //Put selected index, color array, and hue chart in scope
                var get_selected_index = this.getSelectedIndex.bind(this);
                var colorArray = this.options.colorArray;
                var hueChart = this;
                vis.add(pv.Wedge)
                        .data(this.data.getObjects())
                        .bottom(this.radius)
                        .left(this.radius)
                        .outerRadius(this.radius)
                        .angle(function(d) { 
                                return (d[this.options.graphField]/valueSum) * 2 * Math.PI; 
                        }.bind(this))
                        .fillStyle(function() {
                                return this.index == get_selected_index() ? '#fff' : colorArray[this.index % colorArray.length];  
                        }).event("mouseover", function() {
                                hueChart.fireEvent('wedgeOver', this.index);
                        }).event("mouseout", function() {
                                hueChart.fireEvent('wedgeOut');
                        }).event("click", function(d) {
                                hueChart.fireEvent('wedgeClick', d);
                        });                
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
