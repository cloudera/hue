/*
---
script: HueChart.GroupValueManager.js


description: Defines GroupValueManager, a support class for HueChart which manages the application of colors to various data series.

license: MIT-style license

authors:
 - Marcus McLaughlin

provides: [HueChart.GroupValueManager]

requires: 
- Core/Hash
...
*/

var GroupValueManager  = {

        groups: {
                /*
                //example
                someKey: { values: [color1, color2], map: {foo: color1, bar: color2}}
                */
        },

        //Set the value array for a groupKey.
        define: function(groupKey, values) {
                var group = this._getGroup(groupKey);
                group.values = values;
        },

        //Get the value for a given groupKey and name. 
        /*
                groupKey - the unique key for the given group, as defined with define
                name - an identifier for a value, typically a string but could be an integer.
        */
        get: function(groupKey, name) {
                //get the group for the groupKey
                var group = this._getGroup(groupKey);
                //if there is no value defined for the name in this group, define one
                if (!group.map[name]) {
                        //get the number of times that we have assigned a value
                        var used = Hash.getLength(group.map);
                        //assign the value
                        group.map[name] = group.values[used % group.values.length];  
                }
                return group.map[name];
        },

        //INTERNAL FN
        //Given a key, get group, defining it if it doesn't exist.
        _getGroup: function(key) {
                if (!this.groups[key]) {
                        this.groups[key] = {
                                map: {}
                        };
                }
                return this.groups[key];
        }

};
