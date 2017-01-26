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

(function () {
  var svg;

  //save off default references
  var d3 = window.d3v3, topojson = window.topojson;

  var defaultOptions = {
    scope: 'world',
    setProjection: setProjection,
    projection: 'equirectangular',
    dataType: 'json',
    onClick: function () {
    },
    done: function () {
    },
    legendData: [],
    fills: {
      defaultFill: '#ABDDA4'
    },
    geographyConfig: {
      dataUrl: null,
      hideAntarctica: true,
      borderWidth: 1,
      borderColor: '#FDFDFD',
      popupTemplate: function (geography, data) {
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
      popupTemplate: function (geography, data) {
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
    this.svg = d3.select(element).append('svg')
        .attr('width', element.offsetWidth)
        .attr('class', 'datamap')
        .attr('height', element.offsetHeight);

    return this.svg;
  }

  // setProjection takes the svg element and options
  function setProjection(element, options) {
    var projection, path;
    if (options && typeof options.scope === 'undefined') {
      options.scope = 'world';
    }

    var defaultTranslate = [element.offsetWidth / 2, element.offsetHeight / (options.projection === "mercator" ? 1.45 : 1.8)];

    switch (options.scope) {
      case "usa":
        projection = d3.geo.albersUsa()
          .scale(element.offsetWidth)
          .translate([element.offsetWidth / 2, element.offsetHeight / 2]);
        break;
      case "world":
        projection = d3.geo[options.projection]()
          .scale((element.offsetWidth + 1) / 2 / Math.PI)
          .translate(defaultTranslate);
        break;
      case "europe":
        projection = d3.geo[options.projection]()
          .center([8.43727461750008, 51.16822764400005])
          .scale(380)
          .translate(defaultTranslate);
        break;
      case "chn":
        projection = d3.geo[options.projection]()
          .center([104.18741784700012,34.672410587000066])
          .rotate([0, 0])
          .scale(380)
          .translate(defaultTranslate);
        break;
      case "aus":
        projection = d3.geo[options.projection]()
          .center([136.0129500660001, -31.995293877999913])
          .rotate([0, 0])
          .scale(350)
          .translate(defaultTranslate);
        break;
      case "bra":
        projection = d3.geo[options.projection]()
          .center([-51.447769636499956, -14.23752777099994])
          .rotate([0, 0])
          .scale(320)
          .translate(defaultTranslate);
        break;
      case "can":
        projection = d3.geo[options.projection]()
          .center([-96.81107793155442, 62.3928040600001])
          .rotate([0, 0])
          .scale(300)
          .translate(defaultTranslate);
        break;
      case "fra":
        projection = d3.geo[options.projection]()
          .center([2, 46])
          .rotate([0, 0])
          .scale(1300)
          .translate(defaultTranslate);
        break;
      case "deu":
        projection = d3.geo[options.projection]()
          .center([10.43727461750008, 51.16822764400005])
          .rotate([0, 0])
          .scale(1600)
          .translate(defaultTranslate);
        break;
      case "ita":
        projection = d3.geo[options.projection]()
          .center([12.560077144500099, 41.287229413500036])
          .rotate([0, 0])
          .scale(1300)
          .translate(defaultTranslate);
        break;
      case "jpn":
        projection = d3.geo[options.projection]()
          .center([138.4618839855001, 34.779750881000126])
          .rotate([0, 0])
          .scale(700)
          .translate(defaultTranslate);
        break;
      case "gbr":
        projection = d3.geo[options.projection]()
          .center([-3, 54.501734])
          .rotate([0, 0])
          .scale(1300)
          .translate(defaultTranslate);
        break;
    }

    path = d3.geo.path()
        .projection(projection);

    return {path: path, projection: projection};
  }

  function addStyleBlock() {
    if (d3.select('.datamaps-style-block').empty()) {
      d3.select('head').attr('class', 'datamaps-style-block').append('style')
          .html('.datamap path {stroke: #FFFFFF; stroke-width: 1px;} .datamaps-legend dt, .datamaps-legend dd { float: left; margin: 0 3px 0 0;} .datamaps-legend dd {width: 20px; margin-right: 3px; margin-left: 14px; border-radius: 3px;} .datamaps-legend {padding-bottom: 20px; z-index: 1001; font-size: 12px; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;} .datamaps-hoverover {display: none; font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; } .hoverinfo {padding: 4px; border-radius: 1px; background-color: #FFF; box-shadow: 1px 1px 5px #CCC; font-size: 12px; border: 1px solid #CCC; } .hoverinfo hr {border:1px dotted #CCC; }');
    }
  }

  function drawSubunits(data) {
    var fillData = this.options.fills,
        colorCodeData = this.options.data || {},
        geoConfig = this.options.geographyConfig,
        onClick = this.options.onClick;


    var subunits = this.svg.select('g.datamaps-subunits');
    if (subunits.empty()) {
      subunits = this.addLayer('datamaps-subunits', null, true);
    }

    var geoData = topojson.feature(data, data.objects[ this.options.scope ]).features;
    if (geoConfig.hideAntarctica) {
      geoData = geoData.filter(function (feature) {
        return feature.id !== "ATA";
      });
    }

    var geo = subunits.selectAll('path.datamaps-subunit').data(geoData);

    geo.enter()
        .append('path')
        .attr('d', this.path)
        .attr('class', function (d) {
          return 'datamaps-subunit ' + d.id;
        })
        .attr('data-info', function (d) {
          return JSON.stringify(colorCodeData[d.id]);
        })
        .style('fill', function (d) {
          var fillColor;
          if (colorCodeData[d.id]) {
            fillColor = fillData[ colorCodeData[d.id].fillKey ];
            if (colorCodeData[d.id].selected) {
              fillColor = geoConfig.selectedFillColor;
            }
          }
          return fillColor || fillData.defaultFill;
        })
        .on('click', function (d) {
          if (colorCodeData[d.id] && typeof onClick != "undefined") {
            onClick(colorCodeData[d.id]);
          }
        })
        .style('stroke-width', function (d) {
          var strokeWidth = geoConfig.borderWidth;
          if (colorCodeData[d.id] && colorCodeData[d.id].selected) {
            strokeWidth = 2;
          }
          return strokeWidth;
        })
        .style('stroke', function (d) {
          var strokeColor = geoConfig.borderColor;
          if (colorCodeData[d.id] && colorCodeData[d.id].selected) {
            strokeColor = geoConfig.selectedBorderColor;
          }
          return strokeColor;
        });
  }

  function handleGeographyConfig() {
    var hoverover;
    var svg = this.svg;
    var self = this;
    var options = this.options.geographyConfig;

    if (options.highlightOnHover || options.popupOnHover) {
      svg.selectAll('.datamaps-subunit')
          .on('mouseover', function (d) {
            var $this = d3.select(this);

            if (options.highlightOnHover) {
              var previousAttributes = {
                'fill': $this.style('fill'),
                'stroke': $this.style('stroke'),
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
          .on('mouseout', function () {
            var $this = d3.select(this);

            if (options.highlightOnHover) {
              //reapply previous attributes
              var previousAttributes = JSON.parse($this.attr('data-previousAttributes'));
              for (var attr in previousAttributes) {
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
      if (a.idx < b.idx)
        return -1;
      if (a.idx > b.idx)
        return 1;
      return 0;
    }

    var html = '<dl>';
    var _fills = this.options.fills;

    this.options.legendData.sort(compareLegendValues).forEach(function (fill) {
      html += '<dd style="background-color:' + _fills["fill_" + fill.idx] + '">&nbsp;</dd>';
      html += '<dt>' + fill.cat + '</dt>';
    });


    html += '</dl>';

    var hoverover = d3.select(this.options.element).append('div')
        .attr('class', 'datamaps-legend')
        .html(html);
  }

  function handleArcs(layer, data, options) {
    var self = this,
        svg = this.svg;

    if (!data || (data && !data.slice)) {
      throw "Datamaps Error - arcs must be an array";
    }

    if (typeof options === "undefined") {
      options = defaultOptions.arcConfig;
    }

    var arcs = layer.selectAll('path.datamaps-arc').data(data, JSON.stringify);

    arcs
        .enter()
        .append('svg:path')
        .attr('class', 'datamaps-arc')
        .style('stroke-linecap', 'round')
        .style('stroke', function (datum) {
          if (datum.options && datum.options.strokeColor) {
            return datum.options.strokeColor;
          }
          return  options.strokeColor
        })
        .style('fill', 'none')
        .style('stroke-width', function (datum) {
          if (datum.options && datum.options.strokeWidth) {
            return datum.options.strokeWidth;
          }
          return options.strokeWidth;
        })
        .attr('d', function (datum) {
          var originXY = self.latLngToXY(datum.origin.latitude, datum.origin.longitude);
          var destXY = self.latLngToXY(datum.destination.latitude, datum.destination.longitude);
          var midXY = [ (originXY[0] + destXY[0]) / 2, (originXY[1] + destXY[1]) / 2];
          return "M" + originXY[0] + ',' + originXY[1] + "S" + (midXY[0] + (50 * options.arcSharpness)) + "," + (midXY[1] - (75 * options.arcSharpness)) + "," + destXY[0] + "," + destXY[1];
        })
        .transition()
        .delay(100)
        .style('fill', function () {
          /*
           Thank you Jake Archibald, this is awesome.
           Source: http://jakearchibald.com/2013/animated-line-drawing-svg/
           */
          var length = this.getTotalLength();
          this.style.transition = this.style.WebkitTransition = 'none';
          this.style.strokeDasharray = length + ' ' + length;
          this.style.strokeDashoffset = length;
          this.getBoundingClientRect();
          this.style.transition = this.style.WebkitTransition = 'stroke-dashoffset ' + options.animationSpeed + 'ms ease-out';
          this.style.strokeDashoffset = '0';
          return 'none';
        })

    arcs.exit()
        .transition()
        .style('opacity', 0)
        .remove();
  }

  function handleLabels(layer, options) {
    var self = this;
    options = options || {};
    var labelStartCoodinates = this.projection([-67.707617, 42.722131]);
    this.svg.selectAll(".datamaps-subunit")
        .attr("data-foo", function (d) {
          var center = self.path.centroid(d);
          var xOffset = 7.5, yOffset = 5;

          if (["FL", "KY", "MI"].indexOf(d.id) > -1) xOffset = -2.5;
          if (d.id === "NY") xOffset = -1;
          if (d.id === "MI") yOffset = 18;
          if (d.id === "LA") xOffset = 13;

          var x, y;

          x = center[0] - xOffset;
          y = center[1] + yOffset;

          var smallStateIndex = ["VT", "NH", "MA", "RI", "CT", "NJ", "DE", "MD", "DC"].indexOf(d.id);
          if (smallStateIndex > -1) {
            var yStart = labelStartCoodinates[1];
            x = labelStartCoodinates[0];
            y = yStart + (smallStateIndex * (2 + (options.fontSize || 12)));
            layer.append("line")
                .attr("x1", x - 3)
                .attr("y1", y - 5)
                .attr("x2", center[0])
                .attr("y2", center[1])
                .style("stroke", options.labelColor || "#000")
                .style("stroke-width", options.lineWidth || 1)
          }

          layer.append("text")
              .attr("x", x)
              .attr("y", y)
              .style("font-size", (options.fontSize || 10) + 'px')
              .style("font-family", options.fontFamily || "Verdana")
              .style("fill", options.labelColor || "#000")
              .text(d.id);
          return "bar";
        });
  }


  function handleBubbles(layer, data, options) {
    var self = this,
        fillData = this.options.fills,
        svg = this.svg;

    if (!data || (data && !data.slice)) {
      throw "Datamaps Error - bubbles must be an array";
    }

    var bubbles = layer.selectAll('circle.datamaps-bubble').data(data, JSON.stringify);

    bubbles
        .enter()
        .append('svg:circle')
        .attr('class', 'datamaps-bubble')
        .attr('cx', function (datum) {
          var latLng;
          if (datumHasCoords(datum)) {
            latLng = self.latLngToXY(datum.latitude, datum.longitude);
          }
          else if (datum.centered) {
            latLng = self.path.centroid(svg.select('path.' + datum.centered).data()[0]);
          }
          if (latLng) return latLng[0];
        })
        .attr('cy', function (datum) {
          var latLng;
          if (datumHasCoords(datum)) {
            latLng = self.latLngToXY(datum.latitude, datum.longitude);
          }
          else if (datum.centered) {
            latLng = self.path.centroid(svg.select('path.' + datum.centered).data()[0]);
          }
          if (latLng) return latLng[1];
          ;
        })
        .attr('r', 0) //for animation purposes
        .attr('data-info', function (d) {
          return JSON.stringify(d);
        })
        .style('stroke', options.borderColor)
        .style('stroke-width', options.borderWidth)
        .style('fill-opacity', options.fillOpacity)
        .style('fill', function (datum) {
          var fillColor = fillData[ datum.fillKey ];
          return fillColor || fillData.defaultFill;
        })
        .on('mouseover', function (datum) {
          var $this = d3.select(this);

          if (options.highlightOnHover) {
            //save all previous attributes for mouseout
            var previousAttributes = {
              'fill': $this.style('fill'),
              'stroke': $this.style('stroke'),
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
        .on('mouseout', function (datum) {
          var $this = d3.select(this);

          if (options.highlightOnHover) {
            //reapply previous attributes
            var previousAttributes = JSON.parse($this.attr('data-previousAttributes'));
            for (var attr in previousAttributes) {
              $this.style(attr, previousAttributes[attr]);
            }
          }

          d3.selectAll('.datamaps-hoverover').style('display', 'none');
        })
        .transition().duration(400)
        .attr('r', function (datum) {
          return datum.radius;
        });

    bubbles.exit()
        .transition()
        .delay(options.exitDelay)
        .attr("r", 0)
        .remove();

    function datumHasCoords(datum) {
      return typeof datum !== 'undefined' && typeof datum.latitude !== 'undefined' && typeof datum.longitude !== 'undefined';
    }

  }

  //stolen from underscore.js
  function defaults(obj) {
    Array.prototype.slice.call(arguments, 1).forEach(function (source) {
      if (source) {
        for (var prop in source) {
          if (obj[prop] == null) obj[prop] = source[prop];
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
      throw new Error('Include d3.js (v3.0.3 or greater) and topojson on this page before creating a new map');
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
  Datamap.prototype.draw = function () {
    //save off in a closure
    var self = this;
    var options = self.options;

    //set projections and paths based on scope
    var pathAndProjection = options.setProjection.apply(self, [options.element, options]);

    this.path = pathAndProjection.path;
    this.projection = pathAndProjection.projection;

    //if custom URL for topojson data, retrieve it and render
    if (options.geographyConfig.dataUrl) {
      d3.json(options.geographyConfig.dataUrl, function (error, results) {
        if (error) throw new Error(error);
        self.customTopo = typeof results;
        draw(results);
      });
    }
    else {
      draw(this[options.scope + 'Topo']);
    }

    return this;

    function draw(data) {
      // if fetching remote data, draw the map first then call `updateChoropleth`
      if (self.options.dataUrl) {
        //allow for csv or json data types
        d3[self.options.dataType](self.options.dataUrl, function (data) {
          //in the case of csv, transform data to object
          if (self.options.dataType === 'csv' && (data && data.slice)) {
            var tmpData = {};
            for (var i = 0; i < data.length; i++) {
              tmpData[data[i].id] = data[i];
            }
            data = tmpData;
          }
          Datamaps.prototype.updateChoropleth.call(self, data);
        });
      }
      drawSubunits.call(self, data);
      handleGeographyConfig.call(self);

      if (self.options.geographyConfig.popupOnHover || self.options.bubblesConfig.popupOnHover) {
        hoverover = d3.select(self.options.element).append('div')
            .attr('class', 'datamaps-hoverover')
            .style('z-index', 10001)
            .style('position', 'absolute');
      }

      //fire off finished callback
      self.options.done(self);
    }
  };
  /**************************************
   TopoJSON
   ***************************************/

  var EUROPE_TOPO = {};
  if (typeof  WORLD_TOPO != "undefined"){
    EUROPE_TOPO = jQuery.extend(true, {}, WORLD_TOPO);
    EUROPE_TOPO.objects["europe"] =   EUROPE_TOPO.objects["world"];
    delete EUROPE_TOPO.objects["world"];
  }

  Datamap.prototype.worldTopo = typeof WORLD_TOPO != "undefined" ? WORLD_TOPO : {};
  Datamap.prototype.europeTopo = EUROPE_TOPO;
  Datamap.prototype.abwTopo = typeof ABW_TOPO != "undefined" ? ABW_TOPO : {};
  Datamap.prototype.afgTopo = typeof AFG_TOPO != "undefined" ? AFG_TOPO : {};
  Datamap.prototype.agoTopo = typeof AGO_TOPO != "undefined" ? AGO_TOPO : {};
  Datamap.prototype.aiaTopo = typeof AIA_TOPO != "undefined" ? AIA_TOPO : {};
  Datamap.prototype.albTopo = typeof ALB_TOPO != "undefined" ? ALB_TOPO : {};
  Datamap.prototype.aldTopo = typeof ALD_TOPO != "undefined" ? ALD_TOPO : {};
  Datamap.prototype.andTopo = typeof AND_TOPO != "undefined" ? AND_TOPO : {};
  Datamap.prototype.areTopo = typeof ARE_TOPO != "undefined" ? ARE_TOPO : {};
  Datamap.prototype.argTopo = typeof ARG_TOPO != "undefined" ? ARG_TOPO : {};
  Datamap.prototype.armTopo = typeof ARM_TOPO != "undefined" ? ARM_TOPO : {};
  Datamap.prototype.asmTopo = typeof ASM_TOPO != "undefined" ? ASM_TOPO : {};
  Datamap.prototype.ataTopo = typeof ATA_TOPO != "undefined" ? ATA_TOPO : {};
  Datamap.prototype.atcTopo = typeof ATC_TOPO != "undefined" ? ATC_TOPO : {};
  Datamap.prototype.atfTopo = typeof ATF_TOPO != "undefined" ? ATF_TOPO : {};
  Datamap.prototype.atgTopo = typeof ATG_TOPO != "undefined" ? ATG_TOPO : {};
  Datamap.prototype.ausTopo = typeof AUS_TOPO != "undefined" ? AUS_TOPO : {};
  Datamap.prototype.autTopo = typeof AUT_TOPO != "undefined" ? AUT_TOPO : {};
  Datamap.prototype.azeTopo = typeof AZE_TOPO != "undefined" ? AZE_TOPO : {};
  Datamap.prototype.bdiTopo = typeof BDI_TOPO != "undefined" ? BDI_TOPO : {};
  Datamap.prototype.belTopo = typeof BEL_TOPO != "undefined" ? BEL_TOPO : {};
  Datamap.prototype.benTopo = typeof BEN_TOPO != "undefined" ? BEN_TOPO : {};
  Datamap.prototype.bfaTopo = typeof BFA_TOPO != "undefined" ? BFA_TOPO : {};
  Datamap.prototype.bgdTopo = typeof BGD_TOPO != "undefined" ? BGD_TOPO : {};
  Datamap.prototype.bgrTopo = typeof BGR_TOPO != "undefined" ? BGR_TOPO : {};
  Datamap.prototype.bhrTopo = typeof BHR_TOPO != "undefined" ? BHR_TOPO : {};
  Datamap.prototype.bhsTopo = typeof BHS_TOPO != "undefined" ? BHS_TOPO : {};
  Datamap.prototype.bihTopo = typeof BIH_TOPO != "undefined" ? BIH_TOPO : {};
  Datamap.prototype.bjnTopo = typeof BJN_TOPO != "undefined" ? BJN_TOPO : {};
  Datamap.prototype.blmTopo = typeof BLM_TOPO != "undefined" ? BLM_TOPO : {};
  Datamap.prototype.blrTopo = typeof BLR_TOPO != "undefined" ? BLR_TOPO : {};
  Datamap.prototype.blzTopo = typeof BLZ_TOPO != "undefined" ? BLZ_TOPO : {};
  Datamap.prototype.bmuTopo = typeof BMU_TOPO != "undefined" ? BMU_TOPO : {};
  Datamap.prototype.bolTopo = typeof BOL_TOPO != "undefined" ? BOL_TOPO : {};
  Datamap.prototype.braTopo = typeof BRA_TOPO != "undefined" ? BRA_TOPO : {};
  Datamap.prototype.brbTopo = typeof BRB_TOPO != "undefined" ? BRB_TOPO : {};
  Datamap.prototype.brnTopo = typeof BRN_TOPO != "undefined" ? BRN_TOPO : {};
  Datamap.prototype.btnTopo = typeof BTN_TOPO != "undefined" ? BTN_TOPO : {};
  Datamap.prototype.norTopo = typeof NOR_TOPO != "undefined" ? NOR_TOPO : {};
  Datamap.prototype.bwaTopo = typeof BWA_TOPO != "undefined" ? BWA_TOPO : {};
  Datamap.prototype.cafTopo = typeof CAF_TOPO != "undefined" ? CAF_TOPO : {};
  Datamap.prototype.canTopo = typeof CAN_TOPO != "undefined" ? CAN_TOPO : {};
  Datamap.prototype.cheTopo = typeof CHE_TOPO != "undefined" ? CHE_TOPO : {};
  Datamap.prototype.chlTopo = typeof CHL_TOPO != "undefined" ? CHL_TOPO : {};
  Datamap.prototype.chnTopo = typeof CHN_TOPO != "undefined" ? CHN_TOPO : {};
  Datamap.prototype.civTopo = typeof CIV_TOPO != "undefined" ? CIV_TOPO : {};
  Datamap.prototype.clpTopo = typeof CLP_TOPO != "undefined" ? CLP_TOPO : {};
  Datamap.prototype.cmrTopo = typeof CMR_TOPO != "undefined" ? CMR_TOPO : {};
  Datamap.prototype.codTopo = typeof COD_TOPO != "undefined" ? COD_TOPO : {};
  Datamap.prototype.cogTopo = typeof COG_TOPO != "undefined" ? COG_TOPO : {};
  Datamap.prototype.cokTopo = typeof COK_TOPO != "undefined" ? COK_TOPO : {};
  Datamap.prototype.colTopo = typeof COL_TOPO != "undefined" ? COL_TOPO : {};
  Datamap.prototype.comTopo = typeof COM_TOPO != "undefined" ? COM_TOPO : {};
  Datamap.prototype.cpvTopo = typeof CPV_TOPO != "undefined" ? CPV_TOPO : {};
  Datamap.prototype.criTopo = typeof CRI_TOPO != "undefined" ? CRI_TOPO : {};
  Datamap.prototype.csiTopo = typeof CSI_TOPO != "undefined" ? CSI_TOPO : {};
  Datamap.prototype.cubTopo = typeof CUB_TOPO != "undefined" ? CUB_TOPO : {};
  Datamap.prototype.cuwTopo = typeof CUW_TOPO != "undefined" ? CUW_TOPO : {};
  Datamap.prototype.cymTopo = typeof CYM_TOPO != "undefined" ? CYM_TOPO : {};
  Datamap.prototype.cynTopo = typeof CYN_TOPO != "undefined" ? CYN_TOPO : {};
  Datamap.prototype.cypTopo = typeof CYP_TOPO != "undefined" ? CYP_TOPO : {};
  Datamap.prototype.czeTopo = typeof CZE_TOPO != "undefined" ? CZE_TOPO : {};
  Datamap.prototype.deuTopo = typeof DEU_TOPO != "undefined" ? DEU_TOPO : {};
  Datamap.prototype.djiTopo = typeof DJI_TOPO != "undefined" ? DJI_TOPO : {};
  Datamap.prototype.dmaTopo = typeof DMA_TOPO != "undefined" ? DMA_TOPO : {};
  Datamap.prototype.dnkTopo = typeof DNK_TOPO != "undefined" ? DNK_TOPO : {};
  Datamap.prototype.domTopo = typeof DOM_TOPO != "undefined" ? DOM_TOPO : {};
  Datamap.prototype.dzaTopo = typeof DZA_TOPO != "undefined" ? DZA_TOPO : {};
  Datamap.prototype.ecuTopo = typeof ECU_TOPO != "undefined" ? ECU_TOPO : {};
  Datamap.prototype.egyTopo = typeof EGY_TOPO != "undefined" ? EGY_TOPO : {};
  Datamap.prototype.eriTopo = typeof ERI_TOPO != "undefined" ? ERI_TOPO : {};
  Datamap.prototype.esbTopo = typeof ESB_TOPO != "undefined" ? ESB_TOPO : {};
  Datamap.prototype.espTopo = typeof ESP_TOPO != "undefined" ? ESP_TOPO : {};
  Datamap.prototype.estTopo = typeof EST_TOPO != "undefined" ? EST_TOPO : {};
  Datamap.prototype.ethTopo = typeof ETH_TOPO != "undefined" ? ETH_TOPO : {};
  Datamap.prototype.finTopo = typeof FIN_TOPO != "undefined" ? FIN_TOPO : {};
  Datamap.prototype.fjiTopo = typeof FJI_TOPO != "undefined" ? FJI_TOPO : {};
  Datamap.prototype.flkTopo = typeof FLK_TOPO != "undefined" ? FLK_TOPO : {};
  Datamap.prototype.fraTopo = typeof FRA_TOPO != "undefined" ? FRA_TOPO : {};
  Datamap.prototype.froTopo = typeof FRO_TOPO != "undefined" ? FRO_TOPO : {};
  Datamap.prototype.fsmTopo = typeof FSM_TOPO != "undefined" ? FSM_TOPO : {};
  Datamap.prototype.gabTopo = typeof GAB_TOPO != "undefined" ? GAB_TOPO : {};
  Datamap.prototype.psxTopo = typeof PSX_TOPO != "undefined" ? PSX_TOPO : {};
  Datamap.prototype.gbrTopo = typeof GBR_TOPO != "undefined" ? GBR_TOPO : {};
  Datamap.prototype.geoTopo = typeof GEO_TOPO != "undefined" ? GEO_TOPO : {};
  Datamap.prototype.ggyTopo = typeof GGY_TOPO != "undefined" ? GGY_TOPO : {};
  Datamap.prototype.ghaTopo = typeof GHA_TOPO != "undefined" ? GHA_TOPO : {};
  Datamap.prototype.gibTopo = typeof GIB_TOPO != "undefined" ? GIB_TOPO : {};
  Datamap.prototype.ginTopo = typeof GIN_TOPO != "undefined" ? GIN_TOPO : {};
  Datamap.prototype.gmbTopo = typeof GMB_TOPO != "undefined" ? GMB_TOPO : {};
  Datamap.prototype.gnbTopo = typeof GNB_TOPO != "undefined" ? GNB_TOPO : {};
  Datamap.prototype.gnqTopo = typeof GNQ_TOPO != "undefined" ? GNQ_TOPO : {};
  Datamap.prototype.grcTopo = typeof GRC_TOPO != "undefined" ? GRC_TOPO : {};
  Datamap.prototype.grdTopo = typeof GRD_TOPO != "undefined" ? GRD_TOPO : {};
  Datamap.prototype.grlTopo = typeof GRL_TOPO != "undefined" ? GRL_TOPO : {};
  Datamap.prototype.gtmTopo = typeof GTM_TOPO != "undefined" ? GTM_TOPO : {};
  Datamap.prototype.gumTopo = typeof GUM_TOPO != "undefined" ? GUM_TOPO : {};
  Datamap.prototype.guyTopo = typeof GUY_TOPO != "undefined" ? GUY_TOPO : {};
  Datamap.prototype.hkgTopo = typeof HKG_TOPO != "undefined" ? HKG_TOPO : {};
  Datamap.prototype.hmdTopo = typeof HMD_TOPO != "undefined" ? HMD_TOPO : {};
  Datamap.prototype.hndTopo = typeof HND_TOPO != "undefined" ? HND_TOPO : {};
  Datamap.prototype.hrvTopo = typeof HRV_TOPO != "undefined" ? HRV_TOPO : {};
  Datamap.prototype.htiTopo = typeof HTI_TOPO != "undefined" ? HTI_TOPO : {};
  Datamap.prototype.hunTopo = typeof HUN_TOPO != "undefined" ? HUN_TOPO : {};
  Datamap.prototype.idnTopo = typeof IDN_TOPO != "undefined" ? IDN_TOPO : {};
  Datamap.prototype.imnTopo = typeof IMN_TOPO != "undefined" ? IMN_TOPO : {};
  Datamap.prototype.indTopo = typeof IND_TOPO != "undefined" ? IND_TOPO : {};
  Datamap.prototype.ioaTopo = typeof IOA_TOPO != "undefined" ? IOA_TOPO : {};
  Datamap.prototype.iotTopo = typeof IOT_TOPO != "undefined" ? IOT_TOPO : {};
  Datamap.prototype.irlTopo = typeof IRL_TOPO != "undefined" ? IRL_TOPO : {};
  Datamap.prototype.irnTopo = typeof IRN_TOPO != "undefined" ? IRN_TOPO : {};
  Datamap.prototype.irqTopo = typeof IRQ_TOPO != "undefined" ? IRQ_TOPO : {};
  Datamap.prototype.islTopo = typeof ISL_TOPO != "undefined" ? ISL_TOPO : {};
  Datamap.prototype.isrTopo = typeof ISR_TOPO != "undefined" ? ISR_TOPO : {};
  Datamap.prototype.itaTopo = typeof ITA_TOPO != "undefined" ? ITA_TOPO : {};
  Datamap.prototype.jamTopo = typeof JAM_TOPO != "undefined" ? JAM_TOPO : {};
  Datamap.prototype.jeyTopo = typeof JEY_TOPO != "undefined" ? JEY_TOPO : {};
  Datamap.prototype.jorTopo = typeof JOR_TOPO != "undefined" ? JOR_TOPO : {};
  Datamap.prototype.jpnTopo = typeof JPN_TOPO != "undefined" ? JPN_TOPO : {};
  Datamap.prototype.kabTopo = typeof KAB_TOPO != "undefined" ? KAB_TOPO : {};
  Datamap.prototype.kasTopo = typeof KAS_TOPO != "undefined" ? KAS_TOPO : {};
  Datamap.prototype.kazTopo = typeof KAZ_TOPO != "undefined" ? KAZ_TOPO : {};
  Datamap.prototype.kenTopo = typeof KEN_TOPO != "undefined" ? KEN_TOPO : {};
  Datamap.prototype.kgzTopo = typeof KGZ_TOPO != "undefined" ? KGZ_TOPO : {};
  Datamap.prototype.khmTopo = typeof KHM_TOPO != "undefined" ? KHM_TOPO : {};
  Datamap.prototype.kirTopo = typeof KIR_TOPO != "undefined" ? KIR_TOPO : {};
  Datamap.prototype.knaTopo = typeof KNA_TOPO != "undefined" ? KNA_TOPO : {};
  Datamap.prototype.korTopo = typeof KOR_TOPO != "undefined" ? KOR_TOPO : {};
  Datamap.prototype.kosTopo = typeof KOS_TOPO != "undefined" ? KOS_TOPO : {};
  Datamap.prototype.kwtTopo = typeof KWT_TOPO != "undefined" ? KWT_TOPO : {};
  Datamap.prototype.laoTopo = typeof LAO_TOPO != "undefined" ? LAO_TOPO : {};
  Datamap.prototype.lbnTopo = typeof LBN_TOPO != "undefined" ? LBN_TOPO : {};
  Datamap.prototype.lbrTopo = typeof LBR_TOPO != "undefined" ? LBR_TOPO : {};
  Datamap.prototype.lbyTopo = typeof LBY_TOPO != "undefined" ? LBY_TOPO : {};
  Datamap.prototype.lcaTopo = typeof LCA_TOPO != "undefined" ? LCA_TOPO : {};
  Datamap.prototype.lieTopo = typeof LIE_TOPO != "undefined" ? LIE_TOPO : {};
  Datamap.prototype.lkaTopo = typeof LKA_TOPO != "undefined" ? LKA_TOPO : {};
  Datamap.prototype.lsoTopo = typeof LSO_TOPO != "undefined" ? LSO_TOPO : {};
  Datamap.prototype.ltuTopo = typeof LTU_TOPO != "undefined" ? LTU_TOPO : {};
  Datamap.prototype.luxTopo = typeof LUX_TOPO != "undefined" ? LUX_TOPO : {};
  Datamap.prototype.lvaTopo = typeof LVA_TOPO != "undefined" ? LVA_TOPO : {};
  Datamap.prototype.macTopo = typeof MAC_TOPO != "undefined" ? MAC_TOPO : {};
  Datamap.prototype.mafTopo = typeof MAF_TOPO != "undefined" ? MAF_TOPO : {};
  Datamap.prototype.marTopo = typeof MAR_TOPO != "undefined" ? MAR_TOPO : {};
  Datamap.prototype.mcoTopo = typeof MCO_TOPO != "undefined" ? MCO_TOPO : {};
  Datamap.prototype.mdaTopo = typeof MDA_TOPO != "undefined" ? MDA_TOPO : {};
  Datamap.prototype.mdgTopo = typeof MDG_TOPO != "undefined" ? MDG_TOPO : {};
  Datamap.prototype.mdvTopo = typeof MDV_TOPO != "undefined" ? MDV_TOPO : {};
  Datamap.prototype.mexTopo = typeof MEX_TOPO != "undefined" ? MEX_TOPO : {};
  Datamap.prototype.mhlTopo = typeof MHL_TOPO != "undefined" ? MHL_TOPO : {};
  Datamap.prototype.mkdTopo = typeof MKD_TOPO != "undefined" ? MKD_TOPO : {};
  Datamap.prototype.mliTopo = typeof MLI_TOPO != "undefined" ? MLI_TOPO : {};
  Datamap.prototype.mltTopo = typeof MLT_TOPO != "undefined" ? MLT_TOPO : {};
  Datamap.prototype.mmrTopo = typeof MMR_TOPO != "undefined" ? MMR_TOPO : {};
  Datamap.prototype.mneTopo = typeof MNE_TOPO != "undefined" ? MNE_TOPO : {};
  Datamap.prototype.mngTopo = typeof MNG_TOPO != "undefined" ? MNG_TOPO : {};
  Datamap.prototype.mnpTopo = typeof MNP_TOPO != "undefined" ? MNP_TOPO : {};
  Datamap.prototype.mozTopo = typeof MOZ_TOPO != "undefined" ? MOZ_TOPO : {};
  Datamap.prototype.mrtTopo = typeof MRT_TOPO != "undefined" ? MRT_TOPO : {};
  Datamap.prototype.msrTopo = typeof MSR_TOPO != "undefined" ? MSR_TOPO : {};
  Datamap.prototype.musTopo = typeof MUS_TOPO != "undefined" ? MUS_TOPO : {};
  Datamap.prototype.mwiTopo = typeof MWI_TOPO != "undefined" ? MWI_TOPO : {};
  Datamap.prototype.mysTopo = typeof MYS_TOPO != "undefined" ? MYS_TOPO : {};
  Datamap.prototype.namTopo = typeof NAM_TOPO != "undefined" ? NAM_TOPO : {};
  Datamap.prototype.nclTopo = typeof NCL_TOPO != "undefined" ? NCL_TOPO : {};
  Datamap.prototype.nerTopo = typeof NER_TOPO != "undefined" ? NER_TOPO : {};
  Datamap.prototype.nfkTopo = typeof NFK_TOPO != "undefined" ? NFK_TOPO : {};
  Datamap.prototype.ngaTopo = typeof NGA_TOPO != "undefined" ? NGA_TOPO : {};
  Datamap.prototype.nicTopo = typeof NIC_TOPO != "undefined" ? NIC_TOPO : {};
  Datamap.prototype.niuTopo = typeof NIU_TOPO != "undefined" ? NIU_TOPO : {};
  Datamap.prototype.nldTopo = typeof NLD_TOPO != "undefined" ? NLD_TOPO : {};
  Datamap.prototype.nplTopo = typeof NPL_TOPO != "undefined" ? NPL_TOPO : {};
  Datamap.prototype.nruTopo = typeof NRU_TOPO != "undefined" ? NRU_TOPO : {};
  Datamap.prototype.nulTopo = typeof NUL_TOPO != "undefined" ? NUL_TOPO : {};
  Datamap.prototype.nzlTopo = typeof NZL_TOPO != "undefined" ? NZL_TOPO : {};
  Datamap.prototype.omnTopo = typeof OMN_TOPO != "undefined" ? OMN_TOPO : {};
  Datamap.prototype.pakTopo = typeof PAK_TOPO != "undefined" ? PAK_TOPO : {};
  Datamap.prototype.panTopo = typeof PAN_TOPO != "undefined" ? PAN_TOPO : {};
  Datamap.prototype.pcnTopo = typeof PCN_TOPO != "undefined" ? PCN_TOPO : {};
  Datamap.prototype.perTopo = typeof PER_TOPO != "undefined" ? PER_TOPO : {};
  Datamap.prototype.pgaTopo = typeof PGA_TOPO != "undefined" ? PGA_TOPO : {};
  Datamap.prototype.phlTopo = typeof PHL_TOPO != "undefined" ? PHL_TOPO : {};
  Datamap.prototype.plwTopo = typeof PLW_TOPO != "undefined" ? PLW_TOPO : {};
  Datamap.prototype.pngTopo = typeof PNG_TOPO != "undefined" ? PNG_TOPO : {};
  Datamap.prototype.polTopo = typeof POL_TOPO != "undefined" ? POL_TOPO : {};
  Datamap.prototype.priTopo = typeof PRI_TOPO != "undefined" ? PRI_TOPO : {};
  Datamap.prototype.prkTopo = typeof PRK_TOPO != "undefined" ? PRK_TOPO : {};
  Datamap.prototype.prtTopo = typeof PRT_TOPO != "undefined" ? PRT_TOPO : {};
  Datamap.prototype.pryTopo = typeof PRY_TOPO != "undefined" ? PRY_TOPO : {};
  Datamap.prototype.pyfTopo = typeof PYF_TOPO != "undefined" ? PYF_TOPO : {};
  Datamap.prototype.qatTopo = typeof QAT_TOPO != "undefined" ? QAT_TOPO : {};
  Datamap.prototype.rouTopo = typeof ROU_TOPO != "undefined" ? ROU_TOPO : {};
  Datamap.prototype.rusTopo = typeof RUS_TOPO != "undefined" ? RUS_TOPO : {};
  Datamap.prototype.rwaTopo = typeof RWA_TOPO != "undefined" ? RWA_TOPO : {};
  Datamap.prototype.sahTopo = typeof SAH_TOPO != "undefined" ? SAH_TOPO : {};
  Datamap.prototype.sauTopo = typeof SAU_TOPO != "undefined" ? SAU_TOPO : {};
  Datamap.prototype.scrTopo = typeof SCR_TOPO != "undefined" ? SCR_TOPO : {};
  Datamap.prototype.sdnTopo = typeof SDN_TOPO != "undefined" ? SDN_TOPO : {};
  Datamap.prototype.sdsTopo = typeof SDS_TOPO != "undefined" ? SDS_TOPO : {};
  Datamap.prototype.senTopo = typeof SEN_TOPO != "undefined" ? SEN_TOPO : {};
  Datamap.prototype.serTopo = typeof SER_TOPO != "undefined" ? SER_TOPO : {};
  Datamap.prototype.sgpTopo = typeof SGP_TOPO != "undefined" ? SGP_TOPO : {};
  Datamap.prototype.sgsTopo = typeof SGS_TOPO != "undefined" ? SGS_TOPO : {};
  Datamap.prototype.shnTopo = typeof SHN_TOPO != "undefined" ? SHN_TOPO : {};
  Datamap.prototype.slbTopo = typeof SLB_TOPO != "undefined" ? SLB_TOPO : {};
  Datamap.prototype.sleTopo = typeof SLE_TOPO != "undefined" ? SLE_TOPO : {};
  Datamap.prototype.slvTopo = typeof SLV_TOPO != "undefined" ? SLV_TOPO : {};
  Datamap.prototype.smrTopo = typeof SMR_TOPO != "undefined" ? SMR_TOPO : {};
  Datamap.prototype.solTopo = typeof SOL_TOPO != "undefined" ? SOL_TOPO : {};
  Datamap.prototype.somTopo = typeof SOM_TOPO != "undefined" ? SOM_TOPO : {};
  Datamap.prototype.spmTopo = typeof SPM_TOPO != "undefined" ? SPM_TOPO : {};
  Datamap.prototype.srbTopo = typeof SRB_TOPO != "undefined" ? SRB_TOPO : {};
  Datamap.prototype.stpTopo = typeof STP_TOPO != "undefined" ? STP_TOPO : {};
  Datamap.prototype.surTopo = typeof SUR_TOPO != "undefined" ? SUR_TOPO : {};
  Datamap.prototype.svkTopo = typeof SVK_TOPO != "undefined" ? SVK_TOPO : {};
  Datamap.prototype.svnTopo = typeof SVN_TOPO != "undefined" ? SVN_TOPO : {};
  Datamap.prototype.sweTopo = typeof SWE_TOPO != "undefined" ? SWE_TOPO : {};
  Datamap.prototype.swzTopo = typeof SWZ_TOPO != "undefined" ? SWZ_TOPO : {};
  Datamap.prototype.sxmTopo = typeof SXM_TOPO != "undefined" ? SXM_TOPO : {};
  Datamap.prototype.sycTopo = typeof SYC_TOPO != "undefined" ? SYC_TOPO : {};
  Datamap.prototype.syrTopo = typeof SYR_TOPO != "undefined" ? SYR_TOPO : {};
  Datamap.prototype.tcaTopo = typeof TCA_TOPO != "undefined" ? TCA_TOPO : {};
  Datamap.prototype.tcdTopo = typeof TCD_TOPO != "undefined" ? TCD_TOPO : {};
  Datamap.prototype.tgoTopo = typeof TGO_TOPO != "undefined" ? TGO_TOPO : {};
  Datamap.prototype.thaTopo = typeof THA_TOPO != "undefined" ? THA_TOPO : {};
  Datamap.prototype.tjkTopo = typeof TJK_TOPO != "undefined" ? TJK_TOPO : {};
  Datamap.prototype.tkmTopo = typeof TKM_TOPO != "undefined" ? TKM_TOPO : {};
  Datamap.prototype.tlsTopo = typeof TLS_TOPO != "undefined" ? TLS_TOPO : {};
  Datamap.prototype.tonTopo = typeof TON_TOPO != "undefined" ? TON_TOPO : {};
  Datamap.prototype.ttoTopo = typeof TTO_TOPO != "undefined" ? TTO_TOPO : {};
  Datamap.prototype.tunTopo = typeof TUN_TOPO != "undefined" ? TUN_TOPO : {};
  Datamap.prototype.turTopo = typeof TUR_TOPO != "undefined" ? TUR_TOPO : {};
  Datamap.prototype.tuvTopo = typeof TUV_TOPO != "undefined" ? TUV_TOPO : {};
  Datamap.prototype.twnTopo = typeof TWN_TOPO != "undefined" ? TWN_TOPO : {};
  Datamap.prototype.tzaTopo = typeof TZA_TOPO != "undefined" ? TZA_TOPO : {};
  Datamap.prototype.ugaTopo = typeof UGA_TOPO != "undefined" ? UGA_TOPO : {};
  Datamap.prototype.ukrTopo = typeof UKR_TOPO != "undefined" ? UKR_TOPO : {};
  Datamap.prototype.umiTopo = typeof UMI_TOPO != "undefined" ? UMI_TOPO : {};
  Datamap.prototype.uryTopo = typeof URY_TOPO != "undefined" ? URY_TOPO : {};
  Datamap.prototype.usaTopo = typeof USA_TOPO != "undefined" ? USA_TOPO : {};
  Datamap.prototype.usgTopo = typeof USG_TOPO != "undefined" ? USG_TOPO : {};
  Datamap.prototype.uzbTopo = typeof UZB_TOPO != "undefined" ? UZB_TOPO : {};
  Datamap.prototype.vatTopo = typeof VAT_TOPO != "undefined" ? VAT_TOPO : {};
  Datamap.prototype.vctTopo = typeof VCT_TOPO != "undefined" ? VCT_TOPO : {};
  Datamap.prototype.venTopo = typeof VEN_TOPO != "undefined" ? VEN_TOPO : {};
  Datamap.prototype.vgbTopo = typeof VGB_TOPO != "undefined" ? VGB_TOPO : {};
  Datamap.prototype.virTopo = typeof VIR_TOPO != "undefined" ? VIR_TOPO : {};
  Datamap.prototype.vnmTopo = typeof VNM_TOPO != "undefined" ? VNM_TOPO : {};
  Datamap.prototype.vutTopo = typeof VUT_TOPO != "undefined" ? VUT_TOPO : {};
  Datamap.prototype.wlfTopo = typeof WLF_TOPO != "undefined" ? WLF_TOPO : {};
  Datamap.prototype.wsbTopo = typeof WSB_TOPO != "undefined" ? WSB_TOPO : {};
  Datamap.prototype.wsmTopo = typeof WSM_TOPO != "undefined" ? WSM_TOPO : {};
  Datamap.prototype.yemTopo = typeof YEM_TOPO != "undefined" ? YEM_TOPO : {};
  Datamap.prototype.zafTopo = typeof ZAF_TOPO != "undefined" ? ZAF_TOPO : {};
  Datamap.prototype.zmbTopo = typeof ZMB_TOPO != "undefined" ? ZMB_TOPO : {};
  Datamap.prototype.zweTopo = typeof ZWE_TOPO != "undefined" ? ZWE_TOPO : {};




  /**************************************
   Utilities
   ***************************************/

    //convert lat/lng coords to X / Y coords
  Datamap.prototype.latLngToXY = function (lat, lng) {
    return this.projection([lng, lat]);
  };

  //add <g> layer to root SVG
  Datamap.prototype.addLayer = function (className, id, first) {
    var layer;
    if (first) {
      layer = this.svg.insert('g', ':first-child')
    }
    else {
      layer = this.svg.append('g')
    }
    return layer.attr('id', id || '')
        .attr('class', className || '');
  };

  Datamap.prototype.updateChoropleth = function (data) {
    var svg = this.svg;
    for (var subunit in data) {
      if (data.hasOwnProperty(subunit)) {
        var color;
        var subunitData = data[subunit]
        if (!subunit) {
          continue;
        }
        else if (typeof subunitData === "string") {
          color = subunitData;
        }
        else if (typeof subunitData.color === "string") {
          color = subunitData.color;
        }
        else {
          color = this.options.fills[ subunitData.fillKey ];
        }
        //if it's an object, overriding the previous data
        if (subunitData === Object(subunitData)) {
          this.options.data[subunit] = defaults(subunitData, this.options.data[subunit] || {});
          var geo = this.svg.select('.' + subunit).attr('data-info', JSON.stringify(this.options.data[subunit]));
        }
        svg
            .selectAll('.' + subunit)
            .transition()
            .style('fill', color);
      }
    }
  };

  Datamap.prototype.updatePopup = function (element, d, options) {
    var self = this;
    element.on('mousemove', null);
    element.on('mousemove', function () {
      var position = d3.mouse(this);
      var svgHeight = d3.select(self.svg[0][0].parentNode)[0][0].offsetHeight || -1;
      d3.select(self.svg[0][0].parentNode).select('.datamaps-hoverover')
        .style('top', ( (position[1] + 30)) + "px")
        .html(function () {
          var data = JSON.parse(element.attr('data-info'));
          //if ( !data ) return '';
          return options.popupTemplate(d, data);
        })
        .style('left', ( position[0]) + "px");
      var popupHeight = d3.select(self.svg[0][0].parentNode).select('.datamaps-hoverover')[0][0].offsetHeight;
      if (position[1] + 30 + popupHeight > svgHeight) {
        d3.select(self.svg[0][0].parentNode).select('.datamaps-hoverover').style('top', ( (position[1] - 10 - popupHeight)) + "px")
      }
    });

    d3.select(self.svg[0][0].parentNode).select('.datamaps-hoverover').style('display', 'block');
  };

  Datamap.prototype.addPlugin = function (name, pluginFn) {
    var self = this;
    if (typeof Datamap.prototype[name] === "undefined") {
      Datamap.prototype[name] = function (data, options, callback, createNewLayer) {
        var layer;
        if (typeof createNewLayer === "undefined") {
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
        }
        else {
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

  // expose library
  if (typeof define === "function" && define.amd) {
    define("datamaps", function (require) {
      d3 = require('d3');
      topojson = require('topojson');
      return Datamap;
    });
  }
  else {
    window.Datamap = window.Datamaps = Datamap;
  }

  if (window.jQuery) {
    window.jQuery.fn.datamaps = function (options, callback) {
      options = options || {};
      options.element = this[0];
      var datamap = new Datamap(options);
      if (typeof callback === "function") {
        callback(datamap, options);
      }
      return this;
    };
  }
})();