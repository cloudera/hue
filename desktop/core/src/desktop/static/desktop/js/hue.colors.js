// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

var HueColors = {
  hexToR: function (h) {
    return parseInt((this.cutHex(h)).substring(0, 2), 16)
  },
  hexToG: function (h) {
    return parseInt((this.cutHex(h)).substring(2, 4), 16)
  },
  hexToB: function (h) {
    return parseInt((this.cutHex(h)).substring(4, 6), 16)
  },
  cutHex: function (h) {
    return (h.charAt(0) == "#") ? h.substring(1, 7) : h
  },
  decToHex: function (i) {
    return (i + 0x100).toString(16).substr(-2).toUpperCase();
  },
  scale: function (from, to, bands) {
    var _fromRGB = [this.hexToR(from), this.hexToG(from), this.hexToB(from)],
      _toRGB = [this.hexToR(to), this.hexToG(to), this.hexToB(to)],
      _i,
      _delta = [],
      _bands = [];

    for (_i = 0; _i < 4; _i++) {
      _delta[_i] = (_fromRGB[_i] - _toRGB[_i]) / (bands + 1);
    }

    for (_i = 0; _i < bands; _i++) {
      var r = Math.round(_fromRGB[0] - _delta[0] * _i);
      var g = Math.round(_fromRGB[1] - _delta[1] * _i);
      var b = Math.round(_fromRGB[2] - _delta[2] * _i);
      _bands.push("#" + this.decToHex(r) + this.decToHex(g) + this.decToHex(b));
    }
    return _bands;
  },
  d3Scale: function () {
    return d3.scale.category20().range().concat(d3.scale.category20b().range().concat(d3.scale.category20c().range()));
  },
  LIGHT_BLUE: "#DBE8F1",
  BLUE: "#87BAD5",
  DARK_BLUE: "#338BB8",
  DARKER_BLUE: "#205875",
  PURPLE: "#C0B1E9",
  GRAY: "#666666",
  WHITE: "#FFFFFF",
  ORANGE: "#FF7F0E"
};