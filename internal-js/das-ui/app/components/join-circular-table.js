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

export default Ember.Component.extend({

  tableList: null,
  joinList: null,
  tableNameLength: 12,

  didInsertElement: Ember.observer("joinList", function () {
    //clear the slate every time
    d3.select('#bundle').select('*').remove();
    let lenOfTableName = this.get('tableNameLength');
    var allColumns = this.get('joinList');
    const linkColor = "#32abdf", linkHighlightColor = "red";
    var containerWidth = Ember.$('.join-reports').width() || 1200;
    var containerHeight = Ember.$('.join-reports').height() || 1200;

    var w = 940,
      h = 800,
      rx = w / 2,
      ry = h / 2,
      m0,
      rotate = 0,
      pi = Math.PI,
      zoomInit = 1;

    var translateX = containerWidth/2, translateY = containerHeight/2,
      dragOffsetX = 0,
      dragOffsetY = 0,
      dragOffSetSet = false;
    var startX, startY;
    var splines = [];

    var cluster = d3.layout.cluster()
      .size([360, ry - 180])
      .sort(function (a, b) { return d3.ascending(a.key, b.key); });

    var bundle = d3.layout.bundle();

    var line = d3.svg.line.radial()
      .interpolate("bundle")
      .tension(.85)
      .radius(function (d) { return d.y; })
      .angle(function (d) { return d.x / 180 * Math.PI; });

    var drag = d3.behavior.drag()
      .on("dragend", () => {
        dragOffSetSet = false;
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
          "translate(" + [finalX, finalY] + ")"
          ,"scale(" + currentScale + ")"
        ].join(" "));
        translateX = d3.transform(d3.select('body').select('svg').attr("transform")).translate[0];
        translateY = d3.transform(d3.select('body').select('svg').attr("transform")).translate[1];
      });

    // Chrome 15 bug: <http://code.google.com/p/chromium/issues/detail?id=98951>
    var div = d3.select("#bundle")

    var svg = div.append("svg:svg")
      .attr("width", containerWidth)
      .attr("height", containerHeight)
      .append("svg:g")
      .attr("transform", "translate(" + (containerWidth/2) + "," + (containerHeight/2 - 100) + ")")
      .call(drag);

    svg.append("svg:path")
      .attr("class", "arc")
      .attr("d", function () {
        //return d3.svg.arc().outerRadius(ry - 180).innerRadius(0).startAngle(0).endAngle(2 * Math.PI)
      })
      .on("mousedown", mousedown);


    d3.select('.fa-plus').on('click', function () {
      console.log('id', this.id);
      transition(1.05); // increase on 0.2 each time
    });

    d3.select('.fa-minus').on('click', function () {
      console.log('id', this.id);
      transition(0.95); // deacrease on 0.2 each time
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

      if (!(!!startX && !!startY)) {
        translateX = containerWidth/2;
        translateY = containerHeight/2;
      }
      svg.transition()
        .duration(100)
        .attr("transform", "translate(" + zoom.translate()[0] + translateX + "," + zoom.translate()[1] + translateY + ")scale(" + newScale + ")");;

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



    (function (classes) {

      var nodes = cluster.nodes(packages.root(classes)),
          links = packages.imports(nodes),
          splines = bundle(links);

      var linkHashArr = Ember.A();
      let maxJoinCount = 0;
      let maxStrokeWidth = 4;
      let sigmaJoins = 0;
      let joinCoint = 0;

      links = links.map((link)=>{
        let totalJoinCount = 0;
        if(!linkHashArr.filterBy('key',link.target.name + '-' + link.source.name ).get('firstObject')){
          //does'nt exist already
          linkHashArr.pushObject({ key: link.source.name + '-' + link.target.name , value:  link.source.importsHash.filterBy('hashKey',link.target.name)[0].value });
          totalJoinCount = link.source.importsHash.filterBy('hashKey',link.target.name)[0].value;
        } else{
          //exist already
          totalJoinCount = linkHashArr.filterBy('key', link.target.name + '-' + link.source.name).get('firstObject').value 
                            + link.source.importsHash.filterBy('hashKey',link.target.name)[0].value;
        }
        maxJoinCount = (maxJoinCount >= totalJoinCount) ? maxJoinCount : totalJoinCount;
        sigmaJoins = sigmaJoins + totalJoinCount;
        joinCoint = joinCoint + 1;
        return {
                source : link.source,
                target : link.target,
                totalJoinCount: totalJoinCount
              };
      })

      let meanJoins = parseFloat(sigmaJoins/joinCoint).toFixed(2);

      let sigmaWeightsMinusMean = 0;
      links.forEach((link)=>{
        let localVar = Math.abs(link.totalJoinCount - meanJoins).toFixed(2);
        sigmaWeightsMinusMean = sigmaWeightsMinusMean + localVar*localVar;
      });

      let standardDeviation = Math.sqrt(sigmaWeightsMinusMean/joinCoint);
      let minScaleJoin;

      //joinStrokeWidth scale mapping
      links= links.map((link)=>{
        let scaledJoin = parseFloat((link.totalJoinCount - meanJoins)/standardDeviation).toFixed(2);
        minScaleJoin = (!!minScaleJoin) ? (parseFloat(scaledJoin) < parseFloat(minScaleJoin)? scaledJoin:  minScaleJoin)  : scaledJoin ;
        return {
          source : link.source,
          target : link.target,
          totalJoinCount: link.totalJoinCount,
          scaledJoin: scaledJoin
        };
      });

      let maxScaleFacor;
      let scaleFacor = 1 - parseFloat(minScaleJoin).toFixed(2);

      links= links.map((link)=>{
        let totalScale = parseFloat(link.scaledJoin) + parseFloat(scaleFacor) ;
        maxScaleFacor = (!!maxScaleFacor) ? (parseFloat(totalScale) > parseFloat(maxScaleFacor)? totalScale:  maxScaleFacor)  : totalScale;

        return {
          source : link.source,
          target : link.target,
          totalJoinCount: link.totalJoinCount,
          scaledJoin: link.scaledJoin,
          scale: totalScale
        };
      })
      .map((link)=>{
        return {
          source : link.source,
          target : link.target,
          totalJoinCount: link.totalJoinCount,
          scaledJoin: link.scaledJoin,
          joinStrokeWidth: parseFloat((link.scale/maxScaleFacor)*maxStrokeWidth).toFixed(2)
        };
      });

      var path = svg.selectAll("path.link")
        .data(links)
        .enter().append("svg:path")
        .attr("class", function (d) { return "link" })
        .attr("source", function (d) {
          return formKey(d.source.name);
        })
        .attr("title", function (d) {
          return "Total JoinCount : "+ d.totalJoinCount;
        })
        .attr("target", function (d) {
          return formKey(d.target.name);

        })
        .style("stroke-width", function (d) { return d.joinStrokeWidth + 'px' })
        .attr("totalJoinCount", function (d) { return d.totalJoinCount })
        .attr("d", function (d, i) { return line(splines[i]); })
        .on("mouseover", function(d, i) {
          this.style.stroke = linkHighlightColor;
        })
        .on("mouseout", function(d, i) {
          this.style.stroke = linkColor;
        });

      var allTables = [];
      classes.forEach((column) => {
        allTables.push(column.name.split('.')[1]);
      });

      var uniqueTables = allTables.unique();
      var uniqueTablesGroups = nodes.filter((d) => {
        return (uniqueTables.indexOf(d.key) > -1) && d.children;
      });

      var groupData = svg.selectAll("g.group")
        .data(uniqueTablesGroups)
        .enter().append("group")
        .attr("class", "group");

      var groupArc = d3.svg.arc()
        .innerRadius(ry - 177 + 120)
        .outerRadius(ry - 157 + 120)
        .startAngle(function (d) {
          return (findStartAngle(d.__data__.children) - 2) * pi / 180;
        })
        .endAngle(function (d) {
          return (findEndAngle(d.__data__.children) + 2) * pi / 180
        });

      svg.selectAll("g.arc")
        .data(groupData[0])
        .enter().append("svg:path")
        .attr('stroke-width', '1px').attr('stroke-linejoin', 'round')
        .attr("d", groupArc)
        .attr("id", function (d) {
          var arr = d.__data__.name.split('.');
          return arr[arr.length - 1];
        })
        .attr("class", "groupArc")
        .style("fill", "#32ABDF")
        .style("stroke", "#32ABDF")
        .style("fill-opacity", 1);

      var pathArcData = [];
      var pathArc = d3.selectAll('path.groupArc')[0];
      pathArc.forEach(function (item, index) {
        var pathCoordinates = $(item).attr('d').toString().split(',');
        var locPath = {
          groupName: item.__data__.__data__.key,
          displayName: item.__data__.__data__.name,
          transX: (parseFloat(pathCoordinates[0].substr(1, pathCoordinates[0].length - 1)) + parseFloat(pathCoordinates[7].substr(2, pathCoordinates[0].length - 1))) / 2,
          transY: (parseFloat(pathCoordinates[1]) + parseFloat(pathCoordinates[8])) / 2,
          groupD: $(item).attr('d')
        };
        pathArcData.push(locPath);
      });

      svg.selectAll("g.node")
        .data(nodes.filter(function (n) { return !n.children; }))
        .enter().append("text")
        .attr("class", function (d, index) {
          return 'parent-' + d.name.split('.')[0] + "-"+ d.name.split('.')[1] + ' node';
        })
        .attr("source", function (d) {
          return formKey(d.name);
        })
        .attr("target", function (d) {
          return formKey(d.name);

        })
        .attr("id", function (d, index) {
          return 'parent-' + d.name.split('.')[1] + '_' + index;
        })
        .style("fill", "#6D6D6F")
        .attr("dy", "0.31em")
        .attr("transform", function (d, index) {
          return "rotate(" + (d.x - 90) + ")translate(" + (d.y + 10) + ",0)" + (d.x < 180 ? "" : "rotate(180)");
        })
        .attr("table-transform", function (d, index) {
          return "rotate(" + (d.x - 90) + ")translate(" + (d.x < 180 ? d.y + 160 : d.y + 230) + ",0)" + (d.x < 180 ? "" : "rotate(180)");
        })
        .attr("text-anchor", function (d) {
          return d.x < 180 ? "start" : "end";
        })
        .attr("parent-table", function (d) {
          return d.parent.key;
        })
        .attr("title", function (d) {
          return d.key;
        })
        .text(function (d) {
          return formElipsisText(d.key);
        })
        .on("mouseover", mouseover)
        .on("mouseout", mouseout);

      d3.select("input[type=range]").on("change", function () {
        line.tension(this.value / 100);
        path.attr("d", function (d, i) { return line(splines[i]); });
      });

      svg.selectAll("g.arc")
        .data(pathArcData)
        .enter().append("svg:text")
        .attr("dy", "0.31em")
        .attr("class", "outside-node")
        .attr("title", function (d) {
          let tableName = d.displayName.split(".")[1];
          let dbName = d.displayName.split(".")[0];
          let displayName = tableName + " [" + dbName + "]";
          return displayName;
        })
        .attr("transform", (d) => {
          let t = d3.selectAll('text.' + 'parent-' + d.displayName.replace(".", "-"))[0][0].getAttribute('table-transform');
          return t;
        })
        .html((d) => {

          let t = d3.selectAll('text.' + 'parent-' + d.displayName.replace(".", "-"))[0][0].getAttribute('table-transform');
          let x = d3.transform(t).translate[0];
          let y = d3.transform(t).translate[1];
          let dbNameOrientation = d3.transform(t).rotate >=0 ? '-4.13em' : '-4.13em';
          let tableName = d.displayName.split(".")[1];
          let dbName = d.displayName.split(".")[0];
          let displayName = "<tspan dy='0.13em'>" + trimName(tableName, x, y, lenOfTableName) +"</tspan>\n <br/><tspan dx='"+dbNameOrientation+"' dy='1em'>("+ trimName(dbName, x, y, lenOfTableName) + ")</tspan>";
          return displayName;
        });
    })(allColumns);

    d3.select(window)
      .on("mousemove", mousemove)
      .on("mouseup", mouseup);
    function mouse(e) {
      return [e.pageX - rx, e.pageY - ry];
    }
    function trimName(name, x, y, lenOfTableName) {
      if(name.length > lenOfTableName && (x < 0 && y<0)) {
        return name.substr(0, lenOfTableName - 3)+"...";
      }
      return name;
    }
    function mousedown() {
      m0 = mouse(d3.event);
      d3.event.preventDefault();
    }
    function mousemove() {
      if (m0) {
        var m1 = mouse(d3.event),
          dm = Math.atan2(cross(m0, m1), dot(m0, m1)) * 180 / Math.PI;
        div.style("-webkit-transform", "translate3d(0," + (ry - rx) + "px,0)rotate3d(0,0,0," + dm + "deg)translate3d(0," + (rx - ry) + "px,0)");
      }
    }
    function mouseup() {
      if (m0) {

        var m1 = mouse(d3.event),
          dm = Math.atan2(cross(m0, m1), dot(m0, m1)) * 180 / Math.PI;
        rotate += dm;
        if (rotate > 360) rotate -= 360;
        else if (rotate < 0) rotate += 360;
        m0 = null;
        div.style("-webkit-transform", "rotate3d(0,0,0,0deg)");
        svg.attr("transform", "translate(" + rx + "," + ry + ")rotate(" + rotate + ")")
          .selectAll("g.node text")
          .attr("dx", function (d) { return (d.x + rotate) % 360 < 180 ? 25 : -25; })
          .attr("text-anchor", function (d) { return (d.x + rotate) % 360 < 180 ? "start" : "end"; })
          .attr("transform", function (d) { return (d.x + rotate) % 360 < 180 ? null : "rotate(180)"; });
      }
    }

    function formKey(key) {
      let src = key, srcList, index1 = src.indexOf('('), index2 = src.indexOf(')');
      if(index1 > -1) {
        src = src.replace("(", '');
        src = src.replace(")", '');
        srcList = src.split(',');
        return srcList.join('_');
      }
      return key;
    }

    function formElipsisText(text) {
      let elipsisText = "", elipsisLength = 25;
      if(text.length > elipsisLength) {
        return text.substring(0, elipsisLength-3)+ "...";
      }
      return text;
    }

    function mouseover(d) {
      let key = formKey(d.key);
      this.style.fill = linkHighlightColor;
      higlightPathsOnLabelHighlight(formKey(d.name));
      svg.selectAll("path.link.target-" + key)
        .classed("target", true)
        .each(updateNodes("source", true));
      svg.selectAll("path.link.source-" + key)
        .classed("source", true)
        .each(updateNodes("target", true));
    }


    function mouseout(d) {
      let key = formKey(d.key);
      this.style.fill = "rgb(109, 109, 111)";
      unHiglightPathsOnLabelHighlight(formKey(d.name));
      svg.selectAll("path.link.source-" + key)
        .classed("source", false)
        .each(updateNodes("target", false));
      svg.selectAll("path.link.target-" + key)
        .classed("target", false)
        .each(updateNodes("source", false));
    }
    function updateNodes(name, value) {
      return function (d) {
        if (value) this.parentNode.appendChild(this);
        svg.select("#node-" + d[name].key).classed(name, value);
      };
    }
    function higlightPathsOnLabelHighlight(key) {
      let src = svg.selectAll(`path.link[source='${key}']`);
      let trg = svg.selectAll(`path.link[target='${key}']`);
      src.style("stroke", linkHighlightColor);
      trg.style("stroke", linkHighlightColor);
      if(src[0]) {
        src[0].forEach(function (item, index) {
          if(item) {
            svg.selectAll('text[source=\'' + item.getAttribute("target") + '\']').style("fill", linkHighlightColor);
            svg.selectAll('text[source=\'' + item.getAttribute("source") + '\']').style("fill", linkHighlightColor);
          }
        });
      }
      if(trg[0]) {
        trg[0].forEach(function (item, index) {
          if(item) {
            svg.selectAll('text[source=\'' + item.getAttribute("target") + '\']').style("fill", linkHighlightColor);
            svg.selectAll('text[source=\'' + item.getAttribute("source") + '\']').style("fill", linkHighlightColor);
          }
        });
      }
    }

    function unHiglightPathsOnLabelHighlight(key) {
      svg.selectAll(`path.link[source='${key}']`).style("stroke", linkColor);
      svg.selectAll(`path.link[target='${key}']`).style("stroke", linkColor);

      let src = svg.selectAll(`path.link[source='${key}']`);
      let trg = svg.selectAll(`path.link[target='${key}']`);
      const columnColor = "rgb(109, 109, 111)"
      src.style("stroke", linkColor);
      trg.style("stroke", linkColor);

      if(src[0]) {
        src[0].forEach(function (item, index) {
          if(item) {
            svg.selectAll('text[source=\'' + item.getAttribute("target") + '\']').style("fill", columnColor);
            svg.selectAll('text[source=\'' + item.getAttribute("source") + '\']').style("fill", columnColor);
          }
        });
      }
      if(trg[0]) {
        trg[0].forEach(function (item, index) {
          if(item) {
            svg.selectAll('text[source=\'' + item.getAttribute("target") + '\']').style("fill", columnColor);
            svg.selectAll('text[source=\'' + item.getAttribute("source") + '\']').style("fill", columnColor);
          }
        });
      }
    }

    function cross(a, b) {
      return a[0] * b[1] - a[1] * b[0];
    }
    function dot(a, b) {
      return a[0] * b[0] + a[1] * b[1];
    }
    function findStartAngle(children) {
      var min = children[0].x;
      children.forEach(function (d) {
        if (d.x < min)
          min = d.x;
      });
      return min;
    }
    function findEndAngle(children) {
      var max = children[0].x;
      children.forEach(function (d) {
        if (d.x > max)
          max = d.x;
      });
      return max;
    }

  })
});
