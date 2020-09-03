/*
 *
 * HORTONWORKS DATAPLANE SERVICE AND ITS CONSTITUENT SERVICES
 *
 * (c) 2016-2018 Hortonworks, Inc. All rights reserved.
 *
 * This code is provided to you pursuant to your written agreement with Hortonworks, which may be the terms of the
 * Affero General Public License version 3 (AGPLv3), or pursuant to a written agreement with a third party authorized
 * to distribute this code.  If you do not have a written agreement with Hortonworks or with an authorized and
 * properly licensed third party, you do not have any rights to this code.
 *
 * If this code is provided to you under the terms of the AGPLv3:
 * (A) HORTONWORKS PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY KIND;
 * (B) HORTONWORKS DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT
 *   LIMITED TO IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE;
 * (C) HORTONWORKS IS NOT LIABLE TO YOU, AND WILL NOT DEFEND, INDEMNIFY, OR HOLD YOU HARMLESS FOR ANY CLAIMS ARISING
 *   FROM OR RELATED TO THE CODE; AND
 * (D) WITH RESPECT TO YOUR EXERCISE OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, HORTONWORKS IS NOT LIABLE FOR ANY
 *   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO,
 *   DAMAGES RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF BUSINESS ADVANTAGE OR UNAVAILABILITY,
 *   OR LOSS OR CORRUPTION OF DATA.
 *
 */
import Ember from 'ember';
import fullscreen from 'em-tgraph/utils/fullscreen';

export default Ember.Component.extend({
  selectedTable: null,
  metricsScaleHash: null,
  selectedCountType: null,
  classNames:['garland-layout'],

  sourceTable: Ember.computed('selectedTable', function () {
    return this.get('selectedTable');
  }),

  countTypes: Ember.computed('countTypes', function () {
    return this.get('countTypes');
  }),

  selectedCountType: Ember.computed('selectedCountType', function () {
    return this.get('selectedCountType');
  }),

  connectedNodes: Ember.computed('allTableList', 'sourceTable', function () {
    let sourceTable = this.get('sourceTable'), result;
    try {
      result = this.getConnectedNodes(sourceTable.tableId, sourceTable.linkedTo || []);
    } catch(e) {
    } finally {
      return result;
    }
  }),

  getConnectedNodes: function (sourceId, targetElementIds) {
    var targetElementIds = targetElementIds;
    var allElements = [];
    var list = this.allTableList;

    for (var i = 0; i < list.length; i++) {
      var elmt = list[i];
      targetElementIds.forEach(function (item, index) {
        if (elmt.tableId == item.node) {
          elmt.connections = item.connections;
          allElements.push(elmt);
        }
      });
    }
    return allElements;
  },

  alignRangeMetric() {
    Ember.$('.domain-range').css('margin-left', ($($('.splitter-pane')[1]).width() - 500) / 2 + 'px');
  },

  applyMetricsRange(d, countType="projectionCount") {
    let metricsScaleHash = this.get('metricsScaleHash');
    
    if (d[countType] <= metricsScaleHash.metricsScaleFourHigh && d[countType] >= metricsScaleHash.metricsScaleFourLow) {
      return 'more-frequent';
    } else if (d[countType] <= metricsScaleHash.metricsScaleThreeHigh && d[countType]>= metricsScaleHash.metricsScaleThreeLow) {
      return 'frequent';
    }
    else if (d[countType] <= metricsScaleHash.metricsScaleTwoHigh && d[countType] >= metricsScaleHash.metricsScaleTwoLow) {
      return 'less-frequent';
    }
    else if (d[countType] <= metricsScaleHash.metricsScaleOneHigh && d[countType] >= metricsScaleHash.metricsScaleOneLow) {
      return 'not-frequent';
    } else {
      //backup option
      return 'not-frequent';
    }
  },

  _generatePaths(connectedNodes) {
    var allTbls = connectedNodes;
    var allTblsLength = allTbls.length;

    var topRowTbls = d3.selectAll('table.top-row')[0]
    var topRowTblsLength = topRowTbls.length;

    var bottomRowTbls = d3.selectAll('table.bottom-row')[0]
    var bottomRowTblsLength = bottomRowTbls.length;

    var middleRowEvenTbls = d3.selectAll('table.middle-row-even')[0]
    var middleRowEvenTblLength = middleRowEvenTbls.length;

    var middleRowOddTbls = d3.selectAll('table.middle-row-odd')[0];
    var middleRowOddTblLength = middleRowOddTbls.length;

    var targetTblCoordinates = [];

    topRowTbls.forEach(function (item, index) {

      var temp = {};

      var tempX = $(item)[0].offsetLeft
      var tempY = $(item)[0].offsetTop;
      var tblHeight = $(item)[0].offsetHeight;
      var tblWidth = $(item)[0].offsetWidth;

      var tblid = topRowTbls[index].getAttribute('id');

      temp['connections'] = allTbls.filterBy('tableId', parseInt(tblid))[0].connections || null;
      if (index == 0) {
        temp['x'] = tempX + tblWidth;
        temp['y'] = tempY;
        temp['position'] = 'TL';
      } else if (index == 3) {
        temp['x'] = tempX;
        temp['y'] = tempY;
        temp['position'] = 'TR';

      } else {
        temp['x'] = tempX + tblWidth / 2;
        temp['y'] = tempY;
        temp['position'] = 'TC';
      }

      targetTblCoordinates.push(temp);

    });

    bottomRowTbls.forEach(function (item, index) {
      var temp = {};

      var tempX = $(item)[0].offsetLeft
      var tempY = $(item)[0].offsetTop;
      var tblHeight = $(item)[0].offsetHeight;
      var tblWidth = $(item)[0].offsetWidth;

      temp['connections'] = allTbls.filterBy('tableId', parseInt(bottomRowTbls[index].getAttribute('id')))[0].connections || null;

      if (index == 0) {
        temp['x'] = tempX + tblWidth;
        temp['y'] = tempY;
        temp['position'] = 'BL';

      } else if (index == 3) {
        temp['x'] = tempX;
        temp['y'] = tempY;
        temp['position'] = 'BR';

      } else {
        temp['x'] = tempX + tblWidth / 2;
        temp['y'] = tempY;
        temp['position'] = 'BC';
      }

      targetTblCoordinates.push(temp);

    });

    middleRowEvenTbls.forEach(function (item, index) {
      var temp = {};

      var tempX = $(item)[0].offsetLeft
      var tempY = $(item)[0].offsetTop;
      var tblHeight = $(item)[0].offsetHeight;
      var tblWidth = $(item)[0].offsetWidth;

      temp['connections'] = allTbls.filterBy('tableId', parseInt(middleRowEvenTbls[index].getAttribute('id')))[0].connections || null;

      temp['x'] = tempX + tblWidth;
      temp['y'] = tempY;
      temp['position'] = 'L';

      targetTblCoordinates.push(temp);

    });

    middleRowOddTbls.forEach(function (item, index) {
      var temp = {};

      var tempX = $(item)[0].offsetLeft
      var tempY = $(item)[0].offsetTop;
      var tblHeight = $(item)[0].offsetHeight;
      var tblWidth = $(item)[0].offsetWidth;

      temp['connections'] = allTbls.filterBy('tableId', parseInt(middleRowOddTbls[index].getAttribute('id')))[0].connections || null;

      temp['x'] = tempX;
      temp['y'] = tempY;
      temp['position'] = 'R';

      targetTblCoordinates.push(temp);

    });
    return targetTblCoordinates;
  },


  _fixTableCoordinates(connectedNodes) {

    var allTbls = connectedNodes;
    var allTblsLength = allTbls.length;

    var middleRowEvenTbls = d3.selectAll('table.middle-row-even')[0]
    var middleRowEvenTblLength = middleRowEvenTbls.length;

    var middleRowOddTbls = d3.selectAll('table.middle-row-odd')[0];
    var middleRowOddTblLength = middleRowOddTbls.length;

    /* fix Margin of Last Middle Even/left Row */
    if (middleRowEvenTblLength !== middleRowOddTblLength) {
      var lastMiddleRowTbl = d3.selectAll('table.middle-row-even')[0][middleRowEvenTblLength - 1];
      $(lastMiddleRowTbl).addClass('reset-margin');
    }

    /* fix bottom-row margin if there are less than 9 target tables */
    if (allTblsLength <= 9) {
      var bottomRowTblList = d3.selectAll('table.bottom-row')[0];
      bottomRowTblList.forEach(function (item, index) {
        $(item).addClass('fix-bottomrow-margin')
      })
    }

    /* fix top-margin of source table  */
    if (d3.selectAll('table.bottom-row')[0][0]) {
      var yCoord = $(d3.selectAll('table.bottom-row')[0][0])[0].offsetTop / 2 + 16;
      $(d3.selectAll('table.source-table')[0][0]).css('top', yCoord + 'px');
    } else {
      $(d3.selectAll('table.source-table')[0][0]).addClass('no-bottom-row');
    }

  },

  getPathArray(item){

    let soff = 0;

    let yOffset = 40,
    tt = 400,
    tb = 80,
    t2 = 90,
    t3 = 90;

    const pathArray = [];

    var sourceTbl = this.sourceHash();
    var targetTblCoord = { 'xT': item.x, 'yT': item.y };

    var sourceTblCoord = { 'xS': sourceTbl.x, 'yS': sourceTbl.y - soff };

    if (item.position == 'TL' || item.position == 'BL' || item.position == 'L') {

      pathArray.push({ 'x': targetTblCoord.xT, 'y': targetTblCoord.yT + yOffset });
      pathArray.push({ 'x': targetTblCoord.xT + t2, 'y': targetTblCoord.yT + yOffset });
      pathArray.push({ 'x': targetTblCoord.xT + t2, 'y': sourceTblCoord.yS });
      pathArray.push({ 'x': sourceTblCoord.xS, 'y': sourceTblCoord.yS });

      t2 = (t2 > 10) ? t2 - 10 : 90;
      soff = soff - 5;

    } else if (item.position == 'TR' || item.position == 'BR' || item.position == 'R') {

      pathArray.push({ 'x': targetTblCoord.xT, 'y': targetTblCoord.yT + yOffset });
      pathArray.push({ 'x': targetTblCoord.xT - t3, 'y': targetTblCoord.yT + yOffset });
      pathArray.push({ 'x': targetTblCoord.xT - t3, 'y': sourceTblCoord.yS });
      pathArray.push({ 'x': sourceTblCoord.xS, 'y': sourceTblCoord.yS });

      t3 = t3 - 10;

    } else if (item.position == 'TC') {

      pathArray.push({ 'x': targetTblCoord.xT, 'y': targetTblCoord.yT + yOffset });
      pathArray.push({ 'x': targetTblCoord.xT, 'y': targetTblCoord.yT + tt + yOffset });
      pathArray.push({ 'x': sourceTblCoord.xS, 'y': targetTblCoord.yT + tt + yOffset });
      pathArray.push({ 'x': sourceTblCoord.xS, 'y': sourceTblCoord.yS });

    } else if (item.position == 'BC') {

      pathArray.push({ 'x': targetTblCoord.xT, 'y': targetTblCoord.yT + yOffset });
      pathArray.push({ 'x': targetTblCoord.xT, 'y': targetTblCoord.yT - tb + yOffset });
      pathArray.push({ 'x': sourceTblCoord.xS, 'y': targetTblCoord.yT - tb + yOffset });
      pathArray.push({ 'x': sourceTblCoord.xS, 'y': sourceTblCoord.yS });

    }

    return pathArray;

  },

  sourceHash () {
    var source = d3.selectAll('table.source-table')[0][0];
    var sourceX = $(source)[0].offsetLeft + $(source)[0].offsetWidth / 2;
    var sourceY = $(source)[0].offsetTop + 40;
    var sourceHash = {};
    sourceHash['x'] = sourceX;
    sourceHash['y'] = sourceY;

    return sourceHash;
  },

  didInsertElement: Ember.observer("allTableList", "selectedTable", "sourceTable", "connectedNodes", "metricsScaleHash", "countTypes", "selectedCountType",  function () {
    this.alignRangeMetric();
    //clear the slate
    d3.select('.read-connected-nodes').select('*').remove();

    var svg = null,
      sourceTable = this.get('sourceTable'),
      d = sourceTable,
      rows = sourceTable,
      connectedNodes = this.get('connectedNodes'),
      dragOffsetX = 0,
      dragOffsetY = 0,
      dragOffSetSet = false,
      translateX = 0,
      translateY = 0,
      zoomInit = null,
      _self = this;


    // first, define your viewport dimensions
    var width = ($('.read-connected-nodes').width() > 1400) ? $('.read-connected-nodes').width() : '1400';
    var height = ($(window).height() > 1400) ? $(window).height() : '1400';


    if (connectedNodes.length > 8) {
      height = parseInt(height) + parseInt(Math.ceil((connectedNodes.length - 8) / 2) * 420);
    }

    svg = d3.select('.read-connected-nodes').append('svg')
      .attr("width", width)
      .attr("height", height)


    d3.select('.fa-plus').on('click', function () {
      transition(1.05); // increase on 0.2 each time
    });

    d3.select('.fa-minus').on('click', function () {
      transition(0.95); // deacrease on 0.2 each time
    });
    d3.select('.fa-expand').on('click', function () {
    });
    d3.select('.fa-eye').on('click', function () {
      zoomFit(0.95, 500);
    });

    function transition(zoomLevel) {

      zoomInit = zoomInit || 1;
      let newScale = parseFloat(zoomInit * zoomLevel).toFixed(5);

      if (newScale < 0.2) {
        newScale = 0.2;
      } else {
        newScale = newScale;
      }

      zoomInit = newScale;

      var finalX = translateX;
      var finalY = translateY;

      svg.transition()
        .duration(100)
        .attr("transform", [
          "translate(" + [finalX, finalY] + ")",
          "scale(" + newScale + ")"
        ].join(" "));

    }

    function zoomFit(paddingPercent, transitionDuration) {

      var bounds = svg.node().getBBox();
      var parent = svg.node().parentElement;
      var fullWidth = parent.clientWidth,
        fullHeight = parent.clientHeight;
      var width = bounds.width,
        height = bounds.height;
      var midX = bounds.x + width / 2,
        midY = bounds.y + height / 2;
      if (width == 0 || height == 0) return; // nothing to fit
      var scale = (paddingPercent || 0.75) / Math.max(width / fullWidth, height / fullHeight);
      var translate = [-bounds.x / 2, -bounds.y / 2]; //[fullWidth / 2 - scale * midX, fullHeight / 2 - scale * midY];

      zoomInit = scale;

      svg
        .transition()
        .duration(transitionDuration || 0) // milliseconds
        .call(zoom.translate(translate).scale(scale).event);
    }

    var zoom = d3.behavior.zoom()
      .scaleExtent([1 / 2, 10])
      .on("zoom", function () {

        var e = d3.event,
          tx = Math.min(0, Math.max(e.translate[0], width - width * e.scale)),
          ty = Math.min(0, Math.max(e.translate[1], height - height * e.scale));
        zoom.translate([tx, ty]);
        svg.attr("transform", [
          "translate(" + [tx, ty] + ")",
          "scale(" + e.scale + ")"
        ].join(" "));

      });

    var drag = d3.behavior.drag()
      .on("dragstart", (event) => {
        //console.log('drag starts here.');
      })
      .on("dragend", () => {
        console.log('drag ended!!!');
        dragOffSetSet = false;
        translateX = d3.transform(d3.select('body').select('svg').attr("transform")).translate[0];
        translateY = d3.transform(d3.select('body').select('svg').attr("transform")).translate[1];
        d3.select('svg').style("cursor", "default");
      })
      .on("drag", () => {

        d3.select('svg').style("cursor", "move");

        var currentScale = d3.transform(d3.select('body').select('svg').attr("transform")).scale[0];
        var x = d3.event.x;
        var y = d3.event.y;

        if (!dragOffSetSet) {
          dragOffsetX = x;
          dragOffsetY = y;
          dragOffSetSet = true;
        }

        var finalX = translateX + x - dragOffsetX;
        var finalY = translateY + y - dragOffsetY;

        d3.select('svg').attr("transform", [
          "translate(" + [finalX, finalY] + ")",
          "scale(" + currentScale + ")"
        ].join(" "));
      });

    var lineFunction = d3.svg.line()
      .x(function (d) {
        return d.x;
      })
      .y(function (d) {
        return d.y;
      })
      .interpolate('linear');

    var container = svg.append("g")
      .attr("width", width)
      .attr("height", height)
      .attr("id", "all-tbl-container")

    var fosvg = container.append("foreignObject")
      .attr("width", width)
      .attr("height", height);

    svg//.call(zoom)
      .call(drag);

    var table = fosvg.selectAll('table')
      .data(connectedNodes)
      .enter()
      .append('xhtml:table')
      .attr('class', function (d, i) {
        let tablesLength = d3.selectAll('.read-connected-nodes table')[0].length ;
        let remaining = tablesLength - i;
        if (i <= 3) {
          return 'top-row';
        } else if (remaining > 4 && i % 2 == 0) {
          return 'middle-row-even';
        } else if (remaining > 4 && i % 2 == 1) {
          return 'middle-row-odd';
        } else {
            
          if(tablesLength == 5){
            return `bottom-row clearboth`;
          } else if(tablesLength == 6){
            if(remaining == 2){
              return `bottom-row clearleft`;
            } else{
              return `bottom-row clearright`;
            }
          } else if(tablesLength == 7){
            if(remaining == 3){
              return `bottom-row clearleft`;
            } else if(remaining == 2){
              return `bottom-row`;
            } else{
              return `bottom-row clearright`;
            }
          } else {
            return `bottom-row last-${remaining}`;
          }
        }
      })
      .attr('id', function (d, i) {
        return d.tableId;
      })
      .on('click', function (d) {
        //_self.send('showPathDetails', (d.connections));
      });

    var tableHeader = table.selectAll('thead')
      .data(function (rows, i) {
        return [rows];
      })
      .enter()
      .append('thead');

    var tableInfoPanelRow = tableHeader.append('tr');

    tableInfoPanelRow.append('td')
      .append('span')
      .text(function (d) {
        return d.tableName + " [" + d.databaseName + "]";
      })
      .attr('title', function (d) {
        return d.databaseName + "." + d.tableName;
      })
      .attr('class', 'table-name-st');

    tableInfoPanelRow.append('td');

    var tableContent = table.append('tbody').selectAll('tr')
      .data(function (rows, i) {
        return rows.columns;
      })
      .enter()
      .append('tr')
      .attr('class', (d) => {
        return this.applyMetricsRange(d, this.get('selectedCountType').get('id'));
      });

    var desttd = tableContent.append('td');
    desttd.append('i')
      .filter(function (d) {
        return d.isPrimary;
      })
      .attr('class', 'fa fa-diamond keys-icon')
      .attr('aria-hidden', 'true');

    desttd.append('i')
      .filter(function (d) {
        return d.isPartitioned;
      })
      .attr('class', 'fa fa-cube keys-icon')
      .attr('aria-hidden', 'true');

    desttd.append('i')
      .filter(function (d) {
        return d.filterCount > 0;
      })
      .attr('class', 'fa fa-filter keys-icon')
      .attr('aria-hidden', 'true');


    desttd.append('i')
      .filter(function (d) {
        return d.joinCount > 0;
      })
      .attr('class', 'fa fa-link keys-icon')
      .attr('aria-hidden', 'true');

    desttd.append('i')
      .filter(function (d) {
        return d.aggregationCount > 0;
      })
      .attr('class', 'fa fa-sun-o keys-icon')
      .attr('aria-hidden', 'true');

    desttd.append('i')
      .filter(function (d) {
        return d.isKeys !== true;
      })
      .attr('class', 'dummy-icon');

    desttd.append('span')
      .text(function (d) {
        return d.name;
      })
      .attr('title', function (d) {
        return d.name;
      })
      .attr('class', 'table-label ellipsis-node');

    tableContent.append('td')
      // .attr('class', 'pull-right')
      .append('span')
      .text((d) => {
        let expr = this.get('selectedCountType').get('id');
        switch (expr) {
          case 'projectionCount':
            //console.log('projectionCount');
            return d.projectionCount;
            break;
          case 'filterCount':
            //console.log('filterCount');
            return d.filterCount;
            break;
          case 'joinCount':
            //console.log('joinCount');
            return d.joinCount;
            break;
          case 'aggregationCount':
            //console.log('aggregationCount');
            return d.aggregationCount;
            break;  
          default:
            //console.log('aggregationCount default');
            return d.aggregationCount;
            break;
        }
        
      })
      .attr('class', 'row-count');

    var sourceTableData = d;
    let shortMargin =  (Ember.$('.right-splitter-pane').height());

    var source = fosvg.append('xhtml:table')
      .attr('class', 'source-table')
      .attr('id', 'source-table')
      .style("left", function(d){
        return (connectedNodes.length == 0) ? shortMargin/3 + 'px' : '';
      })
      .style("top", function(d){
        return (connectedNodes.length == 0) ? shortMargin/3 + 'px' : '';
      });

    source.append('thead')
      .append('tr')
      .append('td')
      .append('span')
      .text(sourceTableData.tableName + " [" + sourceTableData.databaseName + "]" )
      .attr('class', 'table-name-st');


        

    var sourceTableContent = source.append('tbody').selectAll('tr')
      .data(sourceTableData.columns)
      .enter()
      .append('tr')
      .attr('class', (d) => {
        return this.applyMetricsRange(d, this.get('selectedCountType').get('id'));
      });

    var sourcemytd = sourceTableContent.append('td');
    sourcemytd.append('i')
      .filter(function (d) {
        return d.isPrimary;
      })
      .attr('class', 'fa fa-diamond keys-icon')
      .attr('aria-hidden', 'true');

    sourcemytd.append('i')
      .filter(function (d) {
        return d.isPartitioned;
      })
      .attr('class', 'fa fa-cube keys-icon')
      .attr('aria-hidden', 'true');

    sourcemytd.append('i')
      .filter(function (d) {
        return d.filterCount > 0;
      })
      .attr('class', 'fa fa-filter keys-icon')
      .attr('aria-hidden', 'true');

    sourcemytd.append('i')
      .filter(function (d) {
        return d.joinCount > 0;
      })
      .attr('class', 'fa fa-link keys-icon')
      .attr('aria-hidden', 'true');

    sourcemytd.append('i')
      .filter(function (d) {
        return d.aggregationCount > 0;
      })
      .attr('class', 'fa fa-sun-o keys-icon')
      .attr('aria-hidden', 'true');

    sourcemytd.append('i')
      .filter(function (d) {
        return d.isKeys !== true;
      })
      .attr('class', 'dummy-icon');

    sourcemytd.append('span')
      .text(function (d) {
        return d.name;
      })
      .attr('title', function (d) {
        return d.name;
      })
      .attr('class', 'table-label');

    sourceTableContent.append('td')
      // .attr('class', 'pull-right')
      .append('span')
      .text( d => {
        var expr = this.get('selectedCountType').get('id');
        switch (expr) {
          case 'projectionCount':
            //console.log('projectionCount');
            return d.projectionCount;
            break;
          case 'filterCount':
            //console.log('filterCount');
            return d.filterCount;
            break;
          case 'joinCount':
            //console.log('joinCount');
            return d.joinCount;
            break;
          case 'aggregationCount':
            //console.log('aggregationCount');
            return d.aggregationCount;
            break;  
          default:
            //console.log('aggregationCount default');
            return d.aggregationCount;
            break;
        }

      })
      .attr('class', 'row-count');

    this._fixTableCoordinates(connectedNodes);

    var finalTargetCoordinates = this._generatePaths(connectedNodes);

    finalTargetCoordinates.forEach( (item, index) => {
      const pathArray =  this.getPathArray(item);
      svg.insert("g", ":first-child") /* Firefox fix, since we have to render these paths before svg.  */
        .append("path")
        .attr("d", lineFunction(pathArray))
        .attr("stroke", "#A7A9AC")
        .attr("stroke-width", 3)
        .attr("fill", "none")
        .attr("connections", JSON.stringify(item.connections))
        .attr("title", "Show Join Details")
        .style("cursor", "pointer")
        .on('click', function (d) {
          _self.send('showPathDetails', JSON.parse($(this).attr('connections')));
        })
        .on('mouseover', function (d) {
          $(this).attr("stroke", "#000");
          $(this).attr("stroke-width", 5);
          
        })
        .on('mouseout', function (d) {
          $(this).attr("stroke", "#A7A9AC");
          $(this).attr("stroke-width", 3);
        });
    })

  
  }),

  actions: {
    showRelations(sourceTableId) {
      this.sendAction('showRelations', sourceTableId);
    },

    showPathDetails(pathJson) {
      this.sendAction('showPathDetails', pathJson);
    },

    fullScreen(){
      let rightSplitterPane = Ember.$(".rw-table-graph").get(0);
      const totalMargin  = 0 + Ember.$(".rw-table-graph").width() - Ember.$(".domain-range").width();
      if(rightSplitterPane){
        fullscreen.toggle(rightSplitterPane);
      }
    },

    countTypeChange(type){

      this.sendAction('updateCountTypes', type);
    }
  }

});
