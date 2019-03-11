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

import $ from 'jquery';
import d3v3 from 'd3v3';

import HueColors from 'utils/hueColors';
import huePubSub from 'utils/huePubSub';

const HUE_CHARTS = {
  TYPES: {
    COUNTER: 'counter',
    LINECHART: 'lines',
    BARCHART: 'bars',
    TIMELINECHART: 'timeline',
    TEXTSELECT: 'textselect',
    POINTCHART: 'points',
    PIECHART: 'pie',
    MAP: 'map',
    GRADIENTMAP: 'gradientmap',
    SCATTERCHART: 'scatter'
  }
};

window.HUE_CHARTS = HUE_CHARTS;

huePubSub.subscribe('charts.state', state => {
  const opacity = state && state.updating ? '0.5' : '1';
  $('.nvd3')
    .parents('svg')
    .css('opacity', opacity);
});

const tipBuilder = () => {
  let direction = d3_tip_direction;
  let offset = d3_tip_offset;
  let html = d3_tip_html;
  const node = initNode();
  let svg = null;
  let point = null;
  let target = null;

  function tip(vis) {
    svg = getSVGNode(vis);
    point = svg.createSVGPoint();
    document.body.appendChild(node);
  }

  // Public - show the tooltip on the screen
  //
  // Returns a tip
  tip.show = function() {
    const args = Array.prototype.slice.call(arguments);
    if (args[args.length - 1] instanceof SVGElement) {
      target = args.pop();
    }

    const content = html.apply(this, args);
    const poffset = offset.apply(this, args);
    const dir = direction.apply(this, args);
    const nodel = d3v3.select(node);
    let i = 0;

    nodel.html(content).style({ opacity: 1, 'pointer-events': 'all' });

    while (i--) {
      nodel.classed(directions[i], false);
    }
    const coords = direction_callbacks.get(dir).apply(this);
    nodel.classed(dir, true).style({
      top: coords.top + poffset[0] + 'px',
      left: coords.left + poffset[1] + 'px'
    });

    return tip;
  };

  // Public - hide the tooltip
  //
  // Returns a tip
  tip.hide = function() {
    const nodel = d3v3.select(node);
    nodel.style({ opacity: 0, 'pointer-events': 'none' });
    return tip;
  };

  // Public: Proxy attr calls to the d3 tip container.  Sets or gets attribute value.
  //
  // n - name of the attribute
  // v - value of the attribute
  //
  // Returns tip or attribute value
  tip.attr = function(n, v) {
    if (arguments.length < 2 && typeof n === 'string') {
      return d3v3.select(node).attr(n);
    } else {
      const args = Array.prototype.slice.call(arguments);
      d3v3.selection.prototype.attr.apply(d3v3.select(node), args);
    }

    return tip;
  };

  // Public: Proxy style calls to the d3 tip container.  Sets or gets a style value.
  //
  // n - name of the property
  // v - value of the property
  //
  // Returns tip or style property value
  tip.style = function(n, v) {
    if (arguments.length < 2 && typeof n === 'string') {
      return d3v3.select(node).style(n);
    } else {
      const args = Array.prototype.slice.call(arguments);
      d3v3.selection.prototype.style.apply(d3v3.select(node), args);
    }

    return tip;
  };

  // Public: Set or get the direction of the tooltip
  //
  // v - One of n(north), s(south), e(east), or w(west), nw(northwest),
  //     sw(southwest), ne(northeast) or se(southeast)
  //
  // Returns tip or direction
  tip.direction = function(v) {
    if (!arguments.length) {
      return direction;
    }
    direction = v == null ? v : d3v3.functor(v);

    return tip;
  };

  // Public: Sets or gets the offset of the tip
  //
  // v - Array of [x, y] offset
  //
  // Returns offset or
  tip.offset = function(v) {
    if (!arguments.length) {
      return offset;
    }
    offset = v == null ? v : d3v3.functor(v);

    return tip;
  };

  // Public: sets or gets the html value of the tooltip
  //
  // v - String value of the tip
  //
  // Returns html value or tip
  tip.html = function(v) {
    if (!arguments.length) {
      return html;
    }
    html = v == null ? v : d3v3.functor(v);

    return tip;
  };

  function d3_tip_direction() {
    return 'n';
  }

  function d3_tip_offset() {
    return [0, 0];
  }

  function d3_tip_html() {
    return ' ';
  }

  const direction_callbacks = d3v3.map({
      n: direction_n,
      s: direction_s,
      e: direction_e,
      w: direction_w,
      nw: direction_nw,
      ne: direction_ne,
      sw: direction_sw,
      se: direction_se
    }),
    directions = direction_callbacks.keys();

  function direction_n() {
    const bbox = getScreenBBox();
    return {
      top: bbox.n.y - node.offsetHeight,
      left: bbox.n.x - node.offsetWidth / 2
    };
  }

  function direction_s() {
    const bbox = getScreenBBox();
    return {
      top: bbox.s.y,
      left: bbox.s.x - node.offsetWidth / 2
    };
  }

  function direction_e() {
    const bbox = getScreenBBox();
    return {
      top: bbox.e.y - node.offsetHeight / 2,
      left: bbox.e.x
    };
  }

  function direction_w() {
    const bbox = getScreenBBox();
    return {
      top: bbox.w.y - node.offsetHeight / 2,
      left: bbox.w.x - node.offsetWidth
    };
  }

  function direction_nw() {
    const bbox = getScreenBBox();
    return {
      top: bbox.nw.y - node.offsetHeight,
      left: bbox.nw.x - node.offsetWidth
    };
  }

  function direction_ne() {
    const bbox = getScreenBBox();
    return {
      top: bbox.ne.y - node.offsetHeight,
      left: bbox.ne.x
    };
  }

  function direction_sw() {
    const bbox = getScreenBBox();
    return {
      top: bbox.sw.y,
      left: bbox.sw.x - node.offsetWidth
    };
  }

  function direction_se() {
    const bbox = getScreenBBox();
    return {
      top: bbox.se.y,
      left: bbox.e.x
    };
  }

  function initNode() {
    const node = d3v3.select(document.createElement('div'));
    node.style({
      position: 'absolute',
      background: HueColors.cuiD3Scale()[0],
      padding: '4px',
      color: HueColors.WHITE,
      opacity: 0,
      pointerEvents: 'none',
      boxSizing: 'border-box'
    });

    return node.node();
  }

  function getSVGNode(el) {
    el = el.node();
    if (el != null) {
      if (el.tagName != null && el.tagName.toLowerCase() === 'svg') {
        return el;
      }

      return el.ownerSVGElement;
    }
  }

  // Private - gets the screen coordinates of a shape
  //
  // Given a shape on the screen, will return an SVGPoint for the directions
  // n(north), s(south), e(east), w(west), ne(northeast), se(southeast), nw(northwest),
  // sw(southwest).
  //
  //    +-+-+
  //    |   |
  //    +   +
  //    |   |
  //    +-+-+
  //
  // Returns an Object {n, s, e, w, nw, sw, ne, se}
  function getScreenBBox() {
    const targetel = target || d3v3.event.target,
      bbox = {},
      matrix = targetel.getScreenCTM(),
      tbbox = targetel.getBBox(),
      width = tbbox.width,
      height = tbbox.height,
      x = tbbox.x,
      y = tbbox.y,
      scrollTop = document.documentElement.scrollTop || document.body.scrollTop,
      scrollLeft = document.documentElement.scrollLeft || document.body.scrollLeft;

    point.x = x + scrollLeft;
    point.y = y + scrollTop;
    bbox.nw = point.matrixTransform(matrix);
    point.x += width;
    bbox.ne = point.matrixTransform(matrix);
    point.y += height;
    bbox.se = point.matrixTransform(matrix);
    point.x -= width;
    bbox.sw = point.matrixTransform(matrix);
    point.y -= height / 2;
    bbox.w = point.matrixTransform(matrix);
    point.x += width;
    bbox.e = point.matrixTransform(matrix);
    point.x -= width / 2;
    point.y -= height / 2;
    bbox.n = point.matrixTransform(matrix);
    point.y += height;
    bbox.s = point.matrixTransform(matrix);

    return bbox;
  }

  return tip;
};

if (typeof d3v3 !== 'undefined') {
  d3v3.tip = tipBuilder;
}
