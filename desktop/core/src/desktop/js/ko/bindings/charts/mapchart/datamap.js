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

import d3v3 from 'd3v3';
import jQuery from 'jquery';
import topojson from 'ext/topojson.v1.min';

import apiHelper from 'api/apiHelper';

const d3 = d3v3;

const defaultOptions = {
  scope: 'world',
  setProjection: setProjection,
  projection: 'equirectangular',
  dataType: 'json',
  onClick: function() {},
  done: function() {},
  legendData: [],
  fills: {
    defaultFill: '#ABDDA4'
  },
  geographyConfig: {
    dataUrl: null,
    hideAntarctica: true,
    borderWidth: 1,
    borderColor: '#FDFDFD',
    popupTemplate: function(geography, data) {
      return '<div class="hoverinfo"><strong>' + geography.properties.name + '</strong></div>';
    },
    popupOnHover: true,
    highlightOnHover: true,
    highlightFillColor: '#FC8D59',
    highlightBorderColor: 'rgba(250, 15, 160, 0.2)',
    selectedFillColor: '#666666',
    selectedBorderColor: '#666666',
    highlightBorderWidth: 2
  },
  bubblesConfig: {
    borderWidth: 2,
    borderColor: '#FFFFFF',
    popupOnHover: true,
    popupTemplate: function(geography, data) {
      return '<div class="hoverinfo"><strong>' + data.name + '</strong></div>';
    },
    fillOpacity: 0.75,
    animate: true,
    highlightOnHover: true,
    highlightFillColor: '#FC8D59',
    highlightBorderColor: 'rgba(250, 15, 160, 0.2)',
    highlightBorderWidth: 2,
    highlightFillOpacity: 0.85,
    exitDelay: 100
  },
  arcConfig: {
    strokeColor: '#DD1C77',
    strokeWidth: 1,
    arcSharpness: 1,
    animationSpeed: 600
  }
};

function addContainer(element) {
  this.svg = d3
    .select(element)
    .append('svg')
    .attr('width', element.offsetWidth)
    .attr('class', 'datamap')
    .attr('height', element.offsetHeight);

  return this.svg;
}

// setProjection takes the svg element and options
function setProjection(element, options) {
  let projection;
  if (options && typeof options.scope === 'undefined') {
    options.scope = 'world';
  }

  const defaultTranslate = [
    element.offsetWidth / 2,
    element.offsetHeight / (options.projection === 'mercator' ? 1.45 : 1.8)
  ];

  switch (options.scope) {
    case 'usa':
      projection = d3.geo
        .albersUsa()
        .scale(element.offsetWidth)
        .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
      break;
    case 'world':
      projection = d3.geo[options.projection]()
        .scale((element.offsetWidth + 1) / 2 / Math.PI)
        .translate(defaultTranslate);
      break;
    case 'europe':
      projection = d3.geo[options.projection]()
        .center([8.43727461750008, 51.16822764400005])
        .scale(380)
        .translate(defaultTranslate);
      break;
    case 'chn':
      projection = d3.geo[options.projection]()
        .center([104.18741784700012, 34.672410587000066])
        .rotate([0, 0])
        .scale(380)
        .translate(defaultTranslate);
      break;
    case 'aus':
      projection = d3.geo[options.projection]()
        .center([136.0129500660001, -31.995293877999913])
        .rotate([0, 0])
        .scale(350)
        .translate(defaultTranslate);
      break;
    case 'bra':
      projection = d3.geo[options.projection]()
        .center([-51.447769636499956, -14.23752777099994])
        .rotate([0, 0])
        .scale(320)
        .translate(defaultTranslate);
      break;
    case 'can':
      projection = d3.geo[options.projection]()
        .center([-96.81107793155442, 62.3928040600001])
        .rotate([0, 0])
        .scale(300)
        .translate(defaultTranslate);
      break;
    case 'fra':
      projection = d3.geo[options.projection]()
        .center([2, 46])
        .rotate([0, 0])
        .scale(1300)
        .translate(defaultTranslate);
      break;
    case 'deu':
      projection = d3.geo[options.projection]()
        .center([10.43727461750008, 51.16822764400005])
        .rotate([0, 0])
        .scale(1600)
        .translate(defaultTranslate);
      break;
    case 'ita':
      projection = d3.geo[options.projection]()
        .center([12.560077144500099, 41.287229413500036])
        .rotate([0, 0])
        .scale(1300)
        .translate(defaultTranslate);
      break;
    case 'jpn':
      projection = d3.geo[options.projection]()
        .center([138.4618839855001, 34.779750881000126])
        .rotate([0, 0])
        .scale(700)
        .translate(defaultTranslate);
      break;
    case 'gbr':
      projection = d3.geo[options.projection]()
        .center([-3, 54.501734])
        .rotate([0, 0])
        .scale(1300)
        .translate(defaultTranslate);
      break;
  }

  const path = d3.geo.path().projection(projection);

  return { path: path, projection: projection };
}

function addStyleBlock() {
  if (d3.select('.datamaps-style-block').empty()) {
    d3.select('head')
      .attr('class', 'datamaps-style-block')
      .append('style')
      .html(
        '.datamap path {stroke: #FFFFFF; stroke-width: 1px;} .datamaps-legend dt, .datamaps-legend dd { float: left; margin: 0 3px 0 0;} .datamaps-legend dd {width: 20px; margin-right: 3px; margin-left: 14px; border-radius: 3px;} .datamaps-legend {padding-bottom: 20px; z-index: 1001; font-size: 12px; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;} .datamaps-hoverover {display: none; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; } .hoverinfo {padding: 4px; border-radius: 1px; background-color: #FFF; box-shadow: 1px 1px 5px #CCC; font-size: 12px; border: 1px solid #CCC; } .hoverinfo hr {border:1px dotted #CCC; }'
      );
  }
}

function drawSubunits(data) {
  const fillData = this.options.fills,
    colorCodeData = this.options.data || {},
    geoConfig = this.options.geographyConfig,
    onClick = this.options.onClick;

  let subunits = this.svg.select('g.datamaps-subunits');
  if (subunits.empty()) {
    subunits = this.addLayer('datamaps-subunits', null, true);
  }

  let geoData = topojson.feature(data, data.objects[this.options.scope]).features;
  if (geoConfig.hideAntarctica) {
    geoData = geoData.filter(feature => {
      return feature.id !== 'ATA';
    });
  }

  const geo = subunits.selectAll('path.datamaps-subunit').data(geoData);

  geo
    .enter()
    .append('path')
    .attr('d', this.path)
    .attr('class', d => {
      return 'datamaps-subunit ' + d.id;
    })
    .attr('data-info', d => {
      return JSON.stringify(colorCodeData[d.id]);
    })
    .style('fill', d => {
      let fillColor;
      if (colorCodeData[d.id]) {
        fillColor = fillData[colorCodeData[d.id].fillKey];
        if (colorCodeData[d.id].selected) {
          fillColor = geoConfig.selectedFillColor;
        }
      }
      return fillColor || fillData.defaultFill;
    })
    .on('click', d => {
      if (colorCodeData[d.id] && typeof onClick != 'undefined') {
        onClick(colorCodeData[d.id]);
      }
    })
    .style('stroke-width', d => {
      let strokeWidth = geoConfig.borderWidth;
      if (colorCodeData[d.id] && colorCodeData[d.id].selected) {
        strokeWidth = 2;
      }
      return strokeWidth;
    })
    .style('stroke', d => {
      let strokeColor = geoConfig.borderColor;
      if (colorCodeData[d.id] && colorCodeData[d.id].selected) {
        strokeColor = geoConfig.selectedBorderColor;
      }
      return strokeColor;
    });
}

function handleGeographyConfig() {
  const svg = this.svg;
  const self = this;
  const options = this.options.geographyConfig;

  if (options.highlightOnHover || options.popupOnHover) {
    svg
      .selectAll('.datamaps-subunit')
      .on('mouseover', function(d) {
        const $this = d3.select(this);

        if (options.highlightOnHover) {
          const previousAttributes = {
            fill: $this.style('fill'),
            stroke: $this.style('stroke'),
            'stroke-width': $this.style('stroke-width'),
            'fill-opacity': $this.style('fill-opacity')
          };

          $this
            .style('fill', options.highlightFillColor)
            .style('stroke', options.highlightBorderColor)
            .style('stroke-width', options.highlightBorderWidth)
            .style('fill-opacity', options.highlightFillOpacity)
            .attr('data-previousAttributes', JSON.stringify(previousAttributes));

          //as per discussion on https://github.com/markmarkoh/datamaps/issues/19
          if (!/MSIE/.test(navigator.userAgent)) {
            moveToFront.call(this);
          }
        }

        if (options.popupOnHover) {
          self.updatePopup($this, d, options, svg);
        }
      })
      .on('mouseout', function() {
        const $this = d3.select(this);

        if (options.highlightOnHover) {
          //reapply previous attributes
          const previousAttributes = JSON.parse($this.attr('data-previousAttributes'));
          for (const attr in previousAttributes) {
            $this.style(attr, previousAttributes[attr]);
          }
        }
        $this.on('mousemove', null);
        d3.selectAll('.datamaps-hoverover').style('display', 'none');
      });
  }

  function moveToFront() {
    this.parentNode.appendChild(this);
  }
}

//plugin to add a simple map legend
function addLegend(layer, data, options) {
  data = data || {};
  if (!this.options.fills) {
    return;
  }

  function compareLegendValues(a, b) {
    if (a.idx < b.idx) {
      return -1;
    }
    if (a.idx > b.idx) {
      return 1;
    }
    return 0;
  }

  let html = '<dl>';
  const _fills = this.options.fills;

  this.options.legendData.sort(compareLegendValues).forEach(fill => {
    html += '<dd style="background-color:' + _fills['fill_' + fill.idx] + '">&nbsp;</dd>';
    html += '<dt>' + fill.cat + '</dt>';
  });

  html += '</dl>';

  d3.select(this.options.element)
    .append('div')
    .attr('class', 'datamaps-legend')
    .html(html);
}

function handleArcs(layer, data, options) {
  const self = this;

  if (!data || (data && !data.slice)) {
    throw 'Datamaps Error - arcs must be an array';
  }

  if (typeof options === 'undefined') {
    options = defaultOptions.arcConfig;
  }

  const arcs = layer.selectAll('path.datamaps-arc').data(data, JSON.stringify);

  arcs
    .enter()
    .append('svg:path')
    .attr('class', 'datamaps-arc')
    .style('stroke-linecap', 'round')
    .style('stroke', datum => {
      if (datum.options && datum.options.strokeColor) {
        return datum.options.strokeColor;
      }
      return options.strokeColor;
    })
    .style('fill', 'none')
    .style('stroke-width', datum => {
      if (datum.options && datum.options.strokeWidth) {
        return datum.options.strokeWidth;
      }
      return options.strokeWidth;
    })
    .attr('d', datum => {
      const originXY = self.latLngToXY(datum.origin.latitude, datum.origin.longitude);
      const destXY = self.latLngToXY(datum.destination.latitude, datum.destination.longitude);
      const midXY = [(originXY[0] + destXY[0]) / 2, (originXY[1] + destXY[1]) / 2];
      return (
        'M' +
        originXY[0] +
        ',' +
        originXY[1] +
        'S' +
        (midXY[0] + 50 * options.arcSharpness) +
        ',' +
        (midXY[1] - 75 * options.arcSharpness) +
        ',' +
        destXY[0] +
        ',' +
        destXY[1]
      );
    })
    .transition()
    .delay(100)
    .style('fill', function() {
      /*
         Thank you Jake Archibald, this is awesome.
         Source: http://jakearchibald.com/2013/animated-line-drawing-svg/
         */
      const length = this.getTotalLength();
      this.style.transition = this.style.WebkitTransition = 'none';
      this.style.strokeDasharray = length + ' ' + length;
      this.style.strokeDashoffset = length;
      this.getBoundingClientRect();
      this.style.transition = this.style.WebkitTransition =
        'stroke-dashoffset ' + options.animationSpeed + 'ms ease-out';
      this.style.strokeDashoffset = '0';
      return 'none';
    });

  arcs
    .exit()
    .transition()
    .style('opacity', 0)
    .remove();
}

function handleLabels(layer, options) {
  const self = this;
  options = options || {};
  const labelStartCoodinates = this.projection([-67.707617, 42.722131]);
  this.svg.selectAll('.datamaps-subunit').attr('data-foo', d => {
    const center = self.path.centroid(d);
    let xOffset = 7.5,
      yOffset = 5;

    if (['FL', 'KY', 'MI'].indexOf(d.id) > -1) {
      xOffset = -2.5;
    }
    if (d.id === 'NY') {
      xOffset = -1;
    }
    if (d.id === 'MI') {
      yOffset = 18;
    }
    if (d.id === 'LA') {
      xOffset = 13;
    }

    let x, y;

    x = center[0] - xOffset;
    y = center[1] + yOffset;

    const smallStateIndex = ['VT', 'NH', 'MA', 'RI', 'CT', 'NJ', 'DE', 'MD', 'DC'].indexOf(d.id);
    if (smallStateIndex > -1) {
      const yStart = labelStartCoodinates[1];
      x = labelStartCoodinates[0];
      y = yStart + smallStateIndex * (2 + (options.fontSize || 12));
      layer
        .append('line')
        .attr('x1', x - 3)
        .attr('y1', y - 5)
        .attr('x2', center[0])
        .attr('y2', center[1])
        .style('stroke', options.labelColor || '#000')
        .style('stroke-width', options.lineWidth || 1);
    }

    layer
      .append('text')
      .attr('x', x)
      .attr('y', y)
      .style('font-size', (options.fontSize || 10) + 'px')
      .style('font-family', options.fontFamily || 'Verdana')
      .style('fill', options.labelColor || '#000')
      .text(d.id);
    return 'bar';
  });
}

function handleBubbles(layer, data, options) {
  const self = this,
    fillData = this.options.fills,
    svg = this.svg;

  if (!data || (data && !data.slice)) {
    throw 'Datamaps Error - bubbles must be an array';
  }

  const bubbles = layer.selectAll('circle.datamaps-bubble').data(data, JSON.stringify);

  bubbles
    .enter()
    .append('svg:circle')
    .attr('class', 'datamaps-bubble')
    .attr('cx', datum => {
      let latLng;
      if (datumHasCoords(datum)) {
        latLng = self.latLngToXY(datum.latitude, datum.longitude);
      } else if (datum.centered) {
        latLng = self.path.centroid(svg.select('path.' + datum.centered).data()[0]);
      }
      if (latLng) {
        return latLng[0];
      }
    })
    .attr('cy', datum => {
      let latLng;
      if (datumHasCoords(datum)) {
        latLng = self.latLngToXY(datum.latitude, datum.longitude);
      } else if (datum.centered) {
        latLng = self.path.centroid(svg.select('path.' + datum.centered).data()[0]);
      }
      if (latLng) {
        return latLng[1];
      }
    })
    .attr('r', 0) //for animation purposes
    .attr('data-info', d => {
      return JSON.stringify(d);
    })
    .style('stroke', options.borderColor)
    .style('stroke-width', options.borderWidth)
    .style('fill-opacity', options.fillOpacity)
    .style('fill', datum => {
      const fillColor = fillData[datum.fillKey];
      return fillColor || fillData.defaultFill;
    })
    .on('mouseover', function(datum) {
      const $this = d3.select(this);

      if (options.highlightOnHover) {
        //save all previous attributes for mouseout
        const previousAttributes = {
          fill: $this.style('fill'),
          stroke: $this.style('stroke'),
          'stroke-width': $this.style('stroke-width'),
          'fill-opacity': $this.style('fill-opacity')
        };

        $this
          .style('fill', options.highlightFillColor)
          .style('stroke', options.highlightBorderColor)
          .style('stroke-width', options.highlightBorderWidth)
          .style('fill-opacity', options.highlightFillOpacity)
          .attr('data-previousAttributes', JSON.stringify(previousAttributes));
      }

      if (options.popupOnHover) {
        self.updatePopup($this, datum, options, svg);
      }
    })
    .on('mouseout', function(datum) {
      const $this = d3.select(this);

      if (options.highlightOnHover) {
        //reapply previous attributes
        const previousAttributes = JSON.parse($this.attr('data-previousAttributes'));
        for (const attr in previousAttributes) {
          $this.style(attr, previousAttributes[attr]);
        }
      }

      d3.selectAll('.datamaps-hoverover').style('display', 'none');
    })
    .transition()
    .duration(400)
    .attr('r', datum => {
      return datum.radius;
    });

  bubbles
    .exit()
    .transition()
    .delay(options.exitDelay)
    .attr('r', 0)
    .remove();

  function datumHasCoords(datum) {
    return (
      typeof datum !== 'undefined' &&
      typeof datum.latitude !== 'undefined' &&
      typeof datum.longitude !== 'undefined'
    );
  }
}

//stolen from underscore.js
function defaults(obj) {
  Array.prototype.slice.call(arguments, 1).forEach(source => {
    if (source) {
      for (const prop in source) {
        if (obj[prop] == null) {
          obj[prop] = source[prop];
        }
      }
    }
  });
  return obj;
}

/**************************************
 Public Functions
 ***************************************/

function Datamap(options) {
  if (typeof d3 === 'undefined' || typeof topojson === 'undefined') {
    throw new Error(
      'Include d3.js (v3.0.3 or greater) and topojson on this page before creating a new map'
    );
  }

  //set options for global use
  this.options = defaults(options, defaultOptions);
  this.options.geographyConfig = defaults(options.geographyConfig, defaultOptions.geographyConfig);
  this.options.bubblesConfig = defaults(options.bubblesConfig, defaultOptions.bubblesConfig);
  this.options.arcConfig = defaults(options.arcConfig, defaultOptions.arcConfig);

  //add the SVG container
  if (d3.select(this.options.element).select('svg').length > 0) {
    addContainer.call(this, this.options.element);
  }

  /* Add core plugins to this instance */
  this.addPlugin('bubbles', handleBubbles);
  this.addPlugin('legend', addLegend);
  this.addPlugin('arc', handleArcs);
  this.addPlugin('labels', handleLabels);

  //append style block with basic hoverover styles
  if (!this.options.disableDefaultStyles) {
    addStyleBlock();
  }

  return this.draw();
}

// actually draw the features(states & countries)
Datamap.prototype.draw = function() {
  //save off in a closure
  const self = this;
  const options = self.options;

  //set projections and paths based on scope
  const pathAndProjection = options.setProjection.apply(self, [options.element, options]);

  this.path = pathAndProjection.path;
  this.projection = pathAndProjection.projection;

  apiHelper
    .fetchTopo({ location: options.scope === 'europe' ? 'world' : options.scope })
    .done(topoData => {
      let topo = JSON.parse(topoData);

      if (options.scope === 'europe') {
        const europeTopo = jQuery.extend(true, {}, topo);
        europeTopo.objects['europe'] = europeTopo.objects['world'];
        delete europeTopo.objects['world'];
        topo = europeTopo;
      }
      self.customTopo = true;
      draw(topo);
    });

  return this;

  function draw(data) {
    // if fetching remote data, draw the map first then call `updateChoropleth`
    if (self.options.dataUrl) {
      //allow for csv or json data types
      d3[self.options.dataType](self.options.dataUrl, data => {
        //in the case of csv, transform data to object
        if (self.options.dataType === 'csv' && (data && data.slice)) {
          const tmpData = {};
          for (let i = 0; i < data.length; i++) {
            tmpData[data[i].id] = data[i];
          }
          data = tmpData;
        }
        Datamap.prototype.updateChoropleth.call(self, data);
      });
    }
    drawSubunits.call(self, data);
    handleGeographyConfig.call(self);

    if (self.options.geographyConfig.popupOnHover || self.options.bubblesConfig.popupOnHover) {
      d3.select(self.options.element)
        .append('div')
        .attr('class', 'datamaps-hoverover')
        .style('z-index', 10001)
        .style('position', 'absolute');
    }

    //fire off finished callback
    self.options.done(self);
  }
};

/**************************************
 Utilities
 ***************************************/

//convert lat/lng coords to X / Y coords
Datamap.prototype.latLngToXY = function(lat, lng) {
  return this.projection([lng, lat]);
};

//add <g> layer to root SVG
Datamap.prototype.addLayer = function(className, id, first) {
  let layer;
  if (first) {
    layer = this.svg.insert('g', ':first-child');
  } else {
    layer = this.svg.append('g');
  }
  return layer.attr('id', id || '').attr('class', className || '');
};

Datamap.prototype.updateChoropleth = function(data) {
  const svg = this.svg;
  for (const subunit in data) {
    if (data.hasOwnProperty(subunit)) {
      let color;
      const subunitData = data[subunit];
      if (!subunit) {
        continue;
      } else if (typeof subunitData === 'string') {
        color = subunitData;
      } else if (typeof subunitData.color === 'string') {
        color = subunitData.color;
      } else {
        color = this.options.fills[subunitData.fillKey];
      }
      //if it's an object, overriding the previous data
      if (subunitData === Object(subunitData)) {
        this.options.data[subunit] = defaults(subunitData, this.options.data[subunit] || {});
        this.svg
          .select('.' + subunit)
          .attr('data-info', JSON.stringify(this.options.data[subunit]));
      }
      svg
        .selectAll('.' + subunit)
        .transition()
        .style('fill', color);
    }
  }
};

Datamap.prototype.updatePopup = function(element, d, options) {
  const self = this;
  element.on('mousemove', null);
  element.on('mousemove', function() {
    const position = d3.mouse(this);
    const svgHeight = d3.select(self.svg[0][0].parentNode)[0][0].offsetHeight || -1;
    d3.select(self.svg[0][0].parentNode)
      .select('.datamaps-hoverover')
      .style('top', position[1] + 30 + 'px')
      .html(() => {
        const data = JSON.parse(element.attr('data-info'));
        //if ( !data ) return '';
        return options.popupTemplate(d, data);
      })
      .style('left', position[0] + 'px');
    const popupHeight = d3.select(self.svg[0][0].parentNode).select('.datamaps-hoverover')[0][0]
      .offsetHeight;
    if (position[1] + 30 + popupHeight > svgHeight) {
      d3.select(self.svg[0][0].parentNode)
        .select('.datamaps-hoverover')
        .style('top', position[1] - 10 - popupHeight + 'px');
    }
  });

  d3.select(self.svg[0][0].parentNode)
    .select('.datamaps-hoverover')
    .style('display', 'block');
};

Datamap.prototype.addPlugin = function(name, pluginFn) {
  if (typeof Datamap.prototype[name] === 'undefined') {
    Datamap.prototype[name] = function(data, options, callback, createNewLayer) {
      let layer;
      if (typeof createNewLayer === 'undefined') {
        createNewLayer = false;
      }

      if (typeof options === 'function') {
        callback = options;
        options = undefined;
      }

      options = defaults(options || {}, defaultOptions[name + 'Config']);

      //add a single layer, reuse the old layer
      if (!createNewLayer && this.options[name + 'Layer']) {
        layer = this.options[name + 'Layer'];
        options = options || this.options[name + 'Options'];
      } else {
        layer = this.addLayer(name);
        this.options[name + 'Layer'] = layer;
        this.options[name + 'Options'] = options;
      }
      pluginFn.apply(this, [layer, data, options]);
      if (callback) {
        callback(layer);
      }
    };
  }
};

jQuery.fn.datamaps = function(options, callback) {
  options = options || {};
  options.element = this[0];
  const datamap = new Datamap(options);
  if (typeof callback === 'function') {
    callback(datamap, options);
  }
  return this;
};

export default Datamap;
