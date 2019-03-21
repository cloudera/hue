/* Builds and then renders a plan graph using Dagre / D3. The JSON for the current query
is retrieved by an HTTP call, and then the graph of nodes and edges is built by walking
over each plan fragment in turn. Plan fragments are connected wherever a node has a
data_stream_target attribute.
<script src="desktop/ext/js/d3.v3.js"></script>
<script src="desktop/ext/js/dagre-d3-min.js"></script>
Copied from https://github.com/apache/incubator-impala/blob/master/www/query_plan.tmpl
*/
function impalaDagre(id) {

  var PROFILE_I18n = {
    timeline: window.I18n('Timeline'),
    metrics: window.I18n('Metrics'),
    cpu: window.I18n('CPU'),
    io: window.I18n('IO'),
    execution: window.I18n('Execution'),
    codegen: window.I18n('CodeGen'),
    overview: window.I18n('Overview'),
    topnodes: window.I18n('Top Nodes'),
    compilation: window.I18n('Compilation'),
    planning: window.I18n('Planning'),
    risks: window.I18n('Risks')
  }

  var d3 = window.d3v3;
  var dagreD3 = window.dagreD3;
  var g = new dagreD3.graphlib.Graph().setGraph({rankDir: "BT"});
  var svg = d3.select("#"+id + " svg");
  var inner = svg.select("g");
  var states_by_name = { };
  var colors = HueColors.cuiD3Scale();
  var _impalaDagree = {
    _metrics: {},
    init: function (initialScale) {
      clearSelection();
      zoom.translate([((svg.attr("width") || $("#"+id).width()) - g.graph().width * initialScale) / 2, 20])
      .scale(initialScale)
      .event(svg);
    },
    metrics: function(data) {
      _impalaDagree._metrics = data;
    },
    update: function(plan) {
      _impalaDagree._plan = plan;
      renderGraph();
      _impalaDagree._width = $(svg[0]).width();
    },
    height: function(value) {
      var scale = zoom.scale() || 1;
      var height = value || 600;
      _impalaDagree._height = height;
      svg.attr('height', height);
    },
    action: function(type) {
      if (type == 'plus') {
        zoom.scale(zoom.scale() + 0.25)
        .event(svg);
      } else if (type == 'minus') {
        zoom.scale(zoom.scale() - 0.25)
        .event(svg);
      } else if (type == 'reset') {
        _impalaDagree.init(1);
      }
    },
    moveTo: function(id) {
      zoomToNode(id);
    },
    select: function(id) {
      select(id);
    }
  };
  createActions();

  function createActions () {
    svg.on('click', function () {
      clearSelection();
      showDetailGlobal();
    });
    d3.select("#"+id)
      .style('position', 'relative')
    .append('div')
      .classed('buttons', true)
    .selectAll('button').data([{ type: 'reset', svg: 'hi-crop-free', divider: true }, { type: 'plus', font: 'fa-plus', divider: true }, { type: 'minus', font: 'fa-minus' }])
    .enter()
    .append(function (data) {
      var text = "";
      text += '<div>';
      text += getIcon(data);
      if (data.divider) {
        text += '<div class="divider"></div>';
      }
      text += '</div>';
      var button = $(text)[0];
      $(button).on('click', function () {
        _impalaDagree.action(data.type);
      });
      return button;
    });

    $parent = $("#"+id);
    d3.select("#"+id)
    .append('div')
      .classed('resizer', true);
    d3.select("#"+id)
    .append('div')
      .classed('details', true);

    $( '#'+id + ' .resizer' ).draggable({
      axis: 'x',
      containment: 'parent',
      scroll: false,
      cursor: 'col-resize',
      drag: function(e, ui) {
        updateDetailsPosition(ui.position.left);
      }
    });
  }

  // Set up zoom support
  var zoom = d3.behavior.zoom().on("zoom", function() {
    var e = d3.event,
        scale = Math.min(Math.max(e.scale, Math.min(Math.min(_impalaDagree._width / g.graph().width, _impalaDagree._height / g.graph().height), 1)), 2),
        tx = Math.min(40, Math.max(e.translate[0], _impalaDagree._width - 40 - g.graph().width * scale)),
        ty = Math.min(40, Math.max(e.translate[1], _impalaDagree._height - 40 - g.graph().height * scale));
    zoom.translate([tx, ty]);
    zoom.scale(scale);
    inner.attr("transform", "translate(" + [tx, ty] + ")" +
               "scale(" + scale + ")");
  });
  svg.call(zoom);

  // Set of colours to use, with the same colour used for every node in the same plan
  // fragment.
  var colours = ["#A0A0A0", "#E99F01", "#7B46AD", "#A60115", "#00008B", "#006400",
                 "#228B22", "#4B0082", "#DAA520", "#008B8B", "#000000", "#DC143C"];

  // Shades of red in order of intensity, used for colouring nodes by time taken
  var cols_by_time = ["#000000", "#1A0500", "#330A00", "#4C0F00", "#661400", "#801A00",
                      "#991F00", "#B22400", "#CC2900", "#E62E00", "#FF3300", "#FF4719"];

  // Recursively build a list of edges and states that comprise the plan graph
  function build(node, parent, edges, states, colour_idx, max_node_time, index, count) {
    if (node["output_card"] === null || node["output_card"] === undefined) {
      return;
    }
    var id = getId(node["label"]);
    var metric_node = getNode(id)
    var predicates = metric_node && (metric_node.other['group by'] || metric_node.other['hash predicates'] || metric_node.other['predicates']) || '';
    var state = { "name": node["label"],
        "type": node["type"],
        "label": node["name"],
        "detail": node["label_detail"],
        "predicates": predicates,
        "num_instances": node["num_instances"],
        "num_active": node["num_active"],
        "max_time": ko.bindingHandlers.numberFormat.human(node["max_time_val"], 5),
        "avg_time": node["avg_time"],
        "icon": node["icon"],
        "parent": parent || node["data_stream_target"],
        "is_broadcast": node["is_broadcast"],
        "max_time_val": node["max_time_val"],
        "width": "200px" };
    states_by_name[state.name] = state;
    states.push(state);
    if (parent) {
      edges.push({ start: node["label"], end: parent, style: { label: '', labelpos: index === 0 && count > 1 ? 'l' : 'r' }, content: { value: 0, unit: 0 } });
    }
    // Add an inter-fragment edge. We use a red dashed line to show that rows are crossing
    // the fragment boundary.
    if (node["data_stream_target"]) {
      var networkTime = getMaxTotalNetworkTime(node["label"], node["data_stream_target"]);
      var text = ko.bindingHandlers.numberFormat.human(networkTime.value, networkTime.unit);
      edges.push({ "start": node["label"],
                   "end": node["data_stream_target"],
                   "content": networkTime,
                   "style": { label: '',
                              style: "stroke-dasharray: 5, 5;",
                              labelpos: index === 0 && count > 1 ? 'l' : 'r' }});
    }
    max_node_time = Math.max(node["max_time_val"], max_node_time)
    for (var i = 0; i < node["children"].length; ++i) {
      max_node_time = build(
        node["children"][i], node["label"], edges, states, colour_idx, max_node_time, i, node["children"].length);
    }
    return max_node_time;
  }

  var is_first = true;

  function select(node) {
    var key = getKey(node);
    if (!key) {
      return;
    }
    clearSelection();
    $('#' + id + " g.node:contains('" + key + "')").attr('class', 'node active');
    showDetail(node);
  }

  function clearSelection() {
    $('#' + id + " g.node").attr('class', 'node'); // addClass doesn't work in svg on our version of jQuery
  }

  function getNode(id) {
    return _impalaDagree._plan && _impalaDagree._plan.metrics && (_impalaDagree._plan.metrics.nodes[id] || _impalaDagree._plan.metrics[id]);
  }

  function getId(key) {
    var id = key.split(':')[0];
    var nid = parseInt(id, 10);
    return Number.isNaN(nid) ? id : nid;
  }

  function getKey(node) {
    var nodes = Object.keys(states_by_name);
    var key;
    var nNode = parseInt(node, 10);
    var keys = Object.keys(nodes);
    for (var i = 0; i < keys.length; i++) {
      if (getId(nodes[keys[i]]) == nNode) {
        key = nodes[keys[i]];
        break;
      }
    }
    return key;
  }

  function zoomToNode(node) {
    var key = getKey(node);
    if (!key) {
      return;
    }
    var n = $('#' + id + " g.node:contains('" + key + "')")[0];
    var t = d3.transform(d3.select(n).attr("transform")),
        x = t.translate[0],
        y = t.translate[1];

    var scale = 1;

    svg.transition().duration(1000)
        .call(zoom.translate([((x * -scale) + (svg.property("clientWidth") / 2)), ((y * -scale) + svg.property("clientHeight") / 2)])
            .scale(scale).event);
  }

  function getIcon(icon) {
    var html = '';
    if (icon && icon.svg) {
      html += '<svg class="hi"><use xlink:href="#'+ icon.svg +'"></use></svg>'
    } else if (icon && icon.font) {
      html += "<div class='fa fa-fw valign-middle " + icon.font + "'></div>";
    }
    return html;
  }

  function getMaxTotalNetworkTime(sender, receiver) {
    var sentTime = getMaxFragmentMetric(sender, 'TotalNetworkSendTime'); // AFAIK there can be only 1 sender per fragment.
    var receiveTime = getMaxValue(receiver, 'ChildTime'); // We can't use TotalNetworkReceiveTime from fragment, because there can be multiple receiver per fragment and that time gets added
    return receiveTime && sentTime ? { value: Math.min(receiveTime.value, sentTime.value), unit: sentTime.unit } : { value: 0, unit: 0 }; // We get the smallest between both, because sometime 1 of them is larger than the other (doesn't make sense for our purpose)*/
  }

  function getValueByKey(key, metric, path, minmax, start) {
    if (!path) {
      path = 'properties.hosts';
    }
    var id = getId(key);
    var node = getNode(id);
    if (!node) {
      return;
    }
    return getValue(node, metric, path, minmax, start);
  }

  function getValue(node, metric, path, minmax, start) {
    if (!path) {
      path = 'properties.hosts';
    }
    var timeline = node.timeline;
    var hosts = getProperty(node, path);
    if (!hosts) {
      return '';
    }
    if (timeline[minmax] && hosts[timeline[minmax]]) {
      return hosts[timeline[minmax]][metric];
    } else {
      return Object.keys(hosts).filter(function (key) { return key !== 'averaged'; }).reduce(function (previous, host) {
        if (Math[minmax](hosts[host][metric].value, previous.value) !== previous.value) {
          return hosts[host][metric];
        } else {
          return previous;
        }
      }, { value: start, unit: 5 });
    }
  }

  function getMaxValue(key, metric, path) {
    return getValueByKey(key, metric, path, 'max', -(Number.MAX_SAFE_INTEGER - 1));
  }

  function getMinValue(key, metric, path) {
    return getValueByKey(key, metric, path, 'min', Number.MAX_SAFE_INTEGER);
  }

  function getFragmentMetric(node, metric, path, minmax, start) {
    var fragment = getFragment(getId(node));
    if (!fragment) {
      return;
    }
    return getValue(fragment, metric, path, minmax, start)
  }

  function getMinFragmentMetric(node, metric, path) {
    if (!path) {
      path = 'properties.hosts';
    }
    return getFragmentMetric(node, metric, path, 'min', Number.MAX_SAFE_INTEGER);
  }

  function getMaxFragmentMetric(node, metric, path) {
    if (!path) {
      path = 'properties.hosts';
    }
    return getFragmentMetric(node, metric, path, 'max', -(Number.MAX_SAFE_INTEGER - 1));
  }

  // This is not exact, but shows some approximation of reality.
  function getCPUTimelineData(key) {
    var timeline = getTimelineData(key);
    if (!timeline) {
      return;
    }
    var id = getId(key);
    var localTime = getMaxValue(key, 'LocalTime');
    localTime = $.extend({}, localTime, { clazz: 'cpu' });
    var last = timeline.filter(function(time) {
      return time.name !== 'Closed';
    }); // Close time is normally wait time;
    var openFinished = last.filter(function(time) {
      return time.name === 'Open Finished';
    })[0];
    var firstBatchReturned = last.filter(function(time) {
      return time.name === 'First Batch Returned';
    })[0];
    last = last[last.length - 1];
    var time;
    if (!openFinished) {
      var end = getMetricsMax() || localTime.value;
      time = _timelineBefore(end, [localTime]);
    } else if (key.indexOf('EXCHANGE') >= 0 && firstBatchReturned) {
      var triplet = getExchangeCPUIOTimelineData(key);
      time = _timelineAfter(firstBatchReturned.value, triplet);
    } else if (key.indexOf('JOIN') >= 0) {
      var middle = (openFinished.duration - localTime.value) / 2;
      var node = getNode(key);
      var spillTime = getMaxValue(key, 'SpillTime');
      var joinTimeline;
      if (spillTime) {
        joinTimeline = [$.extend({}, spillTime, { clazz: 'io' }), $.extend({}, localTime, {value: localTime.value - spillTime.value})];
      } else {
        joinTimeline = [localTime];
      }
      time = _timelineAfter(openFinished.start_time + middle, joinTimeline);
    } else if (key.indexOf('UNION') >= 0 || (key.indexOf('AGGREGATE') >= 0 && states_by_name[key].detail.indexOf('STREAMING') >= 0)) {
      time = _timelineAfter(openFinished.value, [localTime]);
    } else if (key.indexOf('AGGREGATE') >= 0) {
      var spillTime = getMaxValue(key, 'SpillTime');
      var aggTimeline;
      if (spillTime) {
        aggTimeline = [$.extend({}, spillTime, { clazz: 'io' }), $.extend({}, localTime, {value: localTime.value - spillTime.value})];
      } else {
        aggTimeline = [localTime];
      }
      time = _timelineBefore(last.value, aggTimeline);
    } else if (key.indexOf('SCAN') >= 0) {
      var doublet = getScanCPUIOTimelineData(key);
      var doubletSum = sum(doublet, 'value');
      if (firstBatchReturned && firstBatchReturned.start_time + doubletSum < last.value) {
        time = _timelineAfter(firstBatchReturned.start_time, doublet);
      } else {
        time = _timelineBefore(last.value, doublet);
      }
    } else {
      time = _timelineBefore(last.value, [localTime]);
    }
    return time;
  }

  function _timelineBefore(end_time, timeline) {
    var timelineSum = sum(timeline, 'value');
    return _timelineAfter(end_time - timelineSum, timeline);
  }

  function _timelineAfter(start_time, timeline) {
    var total = 0;
    return timeline.map(function (event, index) {
      return $.extend({}, event, { start_time: start_time + total, duration: event.value, value: start_time + (total += event.value), name: PROFILE_I18n[event.clazz]});
    });
  }

  function getExecutionTimelineData(key) {
    var timeline = getCPUTimelineData(key)
    if (!timeline) {
      return timeline;
    }
    var initTime = getMaxFragmentMetric(key, 'TotalTime', 'children.CodeGen.hosts');
    if (!initTime) {
      return timeline;
    }
    return [$.extend({}, initTime, { start_time: 0, duration: initTime.value, name: window.I18n('CodeGen'), color: colors[2] })].concat(timeline);
  }

  function getHealthData(key, startTime) {
    var id = getId(key);
    var node = getNode(id);
    if (!node || !node.health) {
      return;
    }
    return _timelineAfter(startTime, node.health.map(function (risk) { return $.extend({}, risk, { value: risk.impact }) }));
  }

  function getFragment(id) {
    var node = getNode(id);
    return node && _impalaDagree._plan.metrics.nodes[node.fragment];
  }

  function getMetricsMax() {
    return _impalaDagree._plan && _impalaDagree._plan.metrics && _impalaDagree._plan.metrics['max'];
  }

  function getScanCPUIOTimelineData(key) {
    var cpuExchange = getMaxValue(key, 'LocalTime');
    cpuExchange.clazz = 'cpu';
    var ioTime = getMaxValue(key, 'ChildTime');
    ioTime.clazz = 'io';
    return [ioTime, cpuExchange];
  }

  function getTopNodes() {
    return Object.keys(states_by_name).map(function (key) {
      var timeline = getCPUTimelineData(key);
      var sumTime;
      if (timeline) {
        sumTime = sum(timeline, 'duration');
      } else {
        sumTime = states_by_name[key].max_time_val;
      }
      return { name: states_by_name[key].label, duration: sumTime, unit: 5, key: key, icon: states_by_name[key].icon  };
    }).sort(function (a, b) {
      return b.duration - a.duration;
    });
  }

  function getExchangeCPUIOTimelineData(key) {
    var id = getId(key);
    var node = getNode(id);
    var timeline = node.timeline;
    var cpuExchange = getMaxValue(key, 'LocalTime');
    cpuExchange = $.extend({}, cpuExchange, { clazz: 'cpu' });

    var sender = Object.keys(states_by_name).filter(function(node) {
      return states_by_name[node].parent == key;
    })[0];
    if (!sender) {
      return [{ value: 0, unit: 0 }, { value: 0, unit: 0 }, { value: 0, unit: 0 }];
    }
    var networkTime = getMaxTotalNetworkTime(sender, key);
    networkTime = $.extend({}, networkTime, { clazz: 'io' });
    var krpcTime = getMaxFragmentMetric(sender, 'LocalTime', 'children.KrpcDataStreamSender.hosts');
    krpcTime = $.extend({}, krpcTime, { clazz: 'cpu' });
    return [krpcTime, networkTime, cpuExchange];
  }

  function getTimelineData(key, name) {
    var id = getId(key);
    var node = getNode(id);
    if (!name) {
      name = 'Node Lifecycle Event Timeline';
    }
    return node && node.timeline && ((node.timeline.hosts && node.timeline.hosts[node.timeline.min]) || node.timeline)[name];
  }
  
  function getMinData(data) {
    return data && ((data.hosts && data.hosts[data.min]) || data);
  }

  function renderTimeline(timeline, max) {
    if (!timeline) {
      return '';
    }
    var end = max || timeline[timeline.length - 1].value;
    var divider = end > 33554428 ? 1000000 : 1; // values are in NS, scaling to MS as max pixel value is 33554428px ~9h in MS
    var html = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + (end / divider) + ' 10" class="timeline" preserveAspectRatio="none">';
    html += timeline.map(function(time, index) {
      var clazz = time.clazz ? 'class="' + time.clazz + '"' : '';
      var fill = time.clazz ? '' : 'style="fill:' + (time.color || colors[index % colors.length]) + '"';
      return '<rect ' + clazz + ' x="' + (time.start_time / divider) + '" width="' + (time.duration / divider)  + '" height="10" ' + fill + '></rect>';
    }).join('');
    html += '</svg>';
    return html;
  }

  function showDetailGlobal() {
    var details = d3.select('#' + id + '.query-plan .details');
    var key = getKey(id);
    details.html('<header class="metric-title">' + getIcon({ svg: 'hi-sitemap' }) + '<h4>' + window.I18n('Overview') + '</h4></div>')
    var detailsContent = details.append('div').classed('details-content', true);
    var topNodes = getTopNodes();
    if (topNodes && topNodes.length) {
      var cpuTimelineSection = detailsContent.append('div').classed('details-section', true);
      var cpuTimelineTitle = cpuTimelineSection.append('header');
      cpuTimelineTitle.append('svg').classed('hi', true).append('use').attr('xlink:href', '#hi-filter');
      var metricsMax = getMetricsMax() ? ' (' + ko.bindingHandlers.numberFormat.human(getMetricsMax(), 5) + ')' : '';
      cpuTimelineTitle.append('h5').text(window.I18n('Top Nodes') + metricsMax);
      var cpuTimelineSectionTable = cpuTimelineSection.append('table').classed('clickable ncolumn', true);
      var cpuTimelineSectionTableRows = cpuTimelineSectionTable.selectAll('tr').data(topNodes).enter().append('tr').on('click', function (node) {
        select(getId(node.key));
        zoomToNode(node.key);
      });
      cpuTimelineSectionTableRows.append('td').html(function (time) { return '' + getIcon(time.icon) + '<span class="metric-name" title="' + time.name + '">' + time.name + '</span>'; });
      cpuTimelineSectionTableRows.append('td').text(function (datum) { return ko.bindingHandlers.numberFormat.human(datum.duration, datum.unit); });
    }

    appendTimelineAndLegend(detailsContent, getTimelineData('summary', 'Query Compilation'), window.I18n('Planning'), '#hi-access-time');
    appendTimelineAndLegend(detailsContent, getTimelineData('summary', 'Query Timeline'), window.I18n('Execution' ), '#hi-access-time');

    d3.select('#' + id + '.query-plan .details .metric-title').on('click', function () {
      toggleDetails();
    });
    updateDetailsPosition();
  }

  function updateDetailsPosition(resizerX) {
    if (!d3.select('#' + id + '.query-plan').classed('open')) {
      return;
    }
    if (resizerX == null || resizerX == undefined) {
      resizerX = $('#'+id + ' .resizer').css('left').slice(0, -2);
    }
    var right = $('#'+id).width() - resizerX - 4;
    $('#'+id + ' .details').css('width', right + 'px')
    $('#'+id + ' .details table tr:nth-child(1)').css('max-width', (right - 83) + 'px');
    $('#'+id + ' .buttons').css('left', (resizerX - 4 - 32) + 'px');
  }

  function appendTimelineAndLegend(detailsContent, data, title, icon, max) {
    var timeline = renderTimeline(data, max);
    if (timeline) {
      var executionSum = sum(data, 'duration');
      var cpuTimelineSection = detailsContent.append('div').classed('details-section', true);
      var cpuTimelineTitle = cpuTimelineSection.append('header');
      cpuTimelineTitle.append('svg').classed('hi', true).append('use').attr('xlink:href', icon);
      cpuTimelineTitle.append('h5').text(title + ' (' + ko.bindingHandlers.numberFormat.human(executionSum, 5) + ')');
      cpuTimelineSection.node().appendChild($.parseXML(timeline).children[0]);

      var cpuTimelineSectionTable = cpuTimelineSection.append('table').classed('column', true);
      cpuTimelineSectionTable.append('tr').selectAll('td').data(data).enter().append('td').html(function (time, index) { return '<div class="legend-icon ' + (time.clazz ? time.clazz : '') + '" style="' + (!time.clazz && 'background-color: ' + (time.color || colors[index % colors.length])) + '"></div><span class="metric-name" title="' + time.name + (time.message ? ': ' + time.message : '') + '">' + time.name + '</span>'; });
      cpuTimelineSectionTable.append('tr').selectAll('td').data(data).enter().append('td').text(function (datum) { return ko.bindingHandlers.numberFormat.human(datum.duration, datum.unit); });
    }
  }

  function showDetail(key) {
    var data;
    var node = getNode(key);
    if (!node) {
      return;
    }
    var data = node;

    d3.select('#' + id + '.query-plan').classed('open', true);
    var details = d3.select('#' + id + '.query-plan .details');
    var key = getKey(key);
    details.html('<header class="metric-title">' + getIcon(states_by_name[key].icon) + '<h4>' + states_by_name[key].label+ '</h4></div>');
    var detailsContent = details.append('div').classed('details-content', true);

    var cpuTimelineData = getCPUTimelineData(key);
    appendTimelineAndLegend(detailsContent, getExecutionTimelineData(key), window.I18n('Execution'), '#hi-microchip', getMetricsMax());
    appendTimelineAndLegend(detailsContent, getHealthData(key, cpuTimelineData[0] && cpuTimelineData[0].start_time), window.I18n('Risks'), '#hi-heart', getMetricsMax());

    var timelineData = getTimelineData(key);
    var timeline = renderTimeline(timelineData, getMetricsMax());
    if (timeline) {
      var timelineSum = sum(timelineData, 'duration');
      var timelineSection = detailsContent.append('div').classed('details-section', true);
      var timelineTitle = timelineSection.append('header');
      timelineTitle.append('svg').classed('hi', true).append('use').attr('xlink:href', '#hi-access-time');
      timelineTitle.append('h5').text(window.I18n('Timeline') + ' (' + ko.bindingHandlers.numberFormat.human(timelineSum, 5) + ')');
      timelineSection.node().appendChild($.parseXML(timeline).children[0]);

      var timelineSectionTable = timelineSection.append('table').classed('column', true);
      timelineSectionTable.append('thead').selectAll('tr').data(['\u00A0'].concat(Object.keys(node.timeline.hosts).sort())).enter().append('tr').append('td').text(function (host, i) { return i > 0 ? 'Host ' + i : host; }).attr('title', function (host) { return host; });
      var timelineSectionTableBody = timelineSectionTable.append('tbody');
      var timelineHosts = Object.keys(node.timeline.hosts).sort().map(function (host) { return node.timeline.hosts[host]; });
      var timelineSectionTableCols = timelineSectionTableBody.selectAll('tr').data(timelineHosts);
      var timelineSectionTableCol0 = timelineSectionTableBody.selectAll('tr').data(timelineHosts.slice(0,1));
      timelineSectionTableCol0.enter().append('tr').selectAll('td').data(function (x) { return x['Node Lifecycle Event Timeline']; }).enter().append('td').html(function (time, index) { return '<div class="legend-icon" style="background-color:' + colors[index % colors.length]+' "></div><span class="metric-name" title="' + time.name + '">' + time.name + '</span>'; });
      timelineSectionTableCols.enter().append('tr').selectAll('td').data(function (x) { return x['Node Lifecycle Event Timeline']; }).enter().append('td').text(function (datum) { return ko.bindingHandlers.numberFormat.human(datum.duration, datum.unit); });
    }

    var metricsSection = detailsContent.append('div').classed('details-section', true);
    var metricsChildSections = metricsSection.selectAll('div').data(Object.keys(data.children));

    var metricsTitle = metricsSection.append('header');
    metricsTitle.append('svg').classed('hi', true).append('use').attr('xlink:href', '#hi-bar-chart');
    metricsTitle.append('h5').text(window.I18n('Metrics'));

    var metricsContent = metricsSection.append('table').classed('column metrics', true);
    var metricsHosts = Object.keys(data.properties.hosts).sort().map(function (key) { return data.properties.hosts[key]; });
    var metricsCols = metricsContent.selectAll('tr').data(metricsHosts);
    var metricsCols0 = metricsContent.selectAll('tr').data(metricsHosts.slice(0,1));
    metricsCols0.enter().append('tr').selectAll('td').data(function (host) { return Object.keys(host).sort(); }).enter().append('td').text(function (x) { return x; }).attr('title', function (x) { return x; });
    metricsCols.enter().append('tr').selectAll('td').data(function (x) { return Object.keys(x).sort().map(function (key) {return x[key]; }) }).enter().append('td').text(function (datum) { return ko.bindingHandlers.numberFormat.human(datum.value, datum.unit); });
    metricsContent.append('thead').selectAll('tr').data(['\u00A0'].concat(Object.keys(data.properties.hosts).sort())).enter().append('tr').append('td').text(function (x, i) { return i > 0 ? x === 'averaged' ? x : 'Host ' + (i - 1) : x; }).attr('title', function (x) {return x;});

    var metricsChildSectionsContent = metricsChildSections.enter().append('div');
    metricsChildSectionsContent.append('header').append('h5').text(function (key) { return key; });
    var metricsChildSectionsContentTable = metricsChildSectionsContent.append('table').classed('column metrics', true);
    var fChildrenHosts = function (key) { return Object.keys(data.children[key].hosts).sort().map(function (host) { return data.children[key].hosts[host]; }); };
    var metricsChildSectionsContentCols = metricsChildSectionsContentTable.selectAll('tr').data(function (key) { return fChildrenHosts(key); });
    var metricsChildSectionsContentCols0 = metricsChildSectionsContentTable.selectAll('tr').data(function (key) { return fChildrenHosts(key).slice(0,1); });
    metricsChildSectionsContentCols0.enter().append('tr').selectAll('td').data(function (host) { return Object.keys(host).sort(); }).enter().append('td').text(function (x) { return x; }).attr('title', function (x) { return x; });
    metricsChildSectionsContentCols.enter().append('tr').selectAll('td').data(function (x) { return Object.keys(x).sort().map(function (key) {return x[key]; }) }).enter().append('td').text(function(datum) { return ko.bindingHandlers.numberFormat.human(datum.value, datum.unit);});
    metricsChildSectionsContentTable.append('thead').selectAll('tr').data(function (key) { return ['\u00A0'].concat(Object.keys(data.children[key].hosts).sort()); }).enter().append('tr').append('td').text(function (x, i) { return i > 0 ? x === 'averaged' ? x : 'Host ' + (i - 1) : x; }).attr('title', function (x) {return x;});

    d3.select('#' + id + '.query-plan .details .metric-title').on('click', function () {
      toggleDetails();
    });

    updateDetailsPosition();
  }

  function hideDetail(id) {
    d3.select('#' + id + '.query-plan').classed('open', false);
  }

  function getProperty(object, path) {
    var keys = path.split('.');
    for (var i = 0; i < keys.length; i++) {
      if (object[keys[i]] === null || object[keys[i]] === undefined) {
        return;
      }
      object = object[keys[i]];
    }
    return object;
  }

  function sum(states, metric) {
    var sum = 0;
    for (var i = 0; i < states.length; i++) {
      sum += getProperty(states[i], metric);
    }
    return sum;
  }

  function average(states, metric) {
    var sum = 0;
    for (var i = 0; i < states.length; i++) {
      sum += getProperty(states[i], metric);
    }
    return states.length > 0 ? sum / states.length : 0;
  }

  function averageCombined(avg1, avg2, count1, count2) {
    return (avg1 * count1 + avg2 * count2) / (count1 + count2);
  }

  function toggleDetails() {
    var queryPlan = d3.select('#' + id + '.query-plan');
    queryPlan.classed('open', !queryPlan.classed('open'));
    $("#"+id + ' .details').width('200px');
    $("#"+id + ' .resizer').css({'left': 'auto'});
    $("#"+id + ' .buttons').css({'left': 'auto'});
  }

  function renderGraph() {
    var plan = _impalaDagree._plan;
    if (!plan || !plan.plan_json.plan_nodes || !plan.plan_json.plan_nodes.length) return;
    var states = [];
    var edges = [];
    var colour_idx = 0;
    var max_node_time = 0;
    plan.plan_json["plan_nodes"].forEach(function(parent) {
      max_node_time = Math.max(
        build(parent, null, edges, states, colour_idx, max_node_time, 1, 1));
      // Pick a new colour for each plan fragment
      colour_idx = (colour_idx + 1) % colours.length;
    });
    showDetailGlobal();
    states.forEach(function (state) {
      var cpuTimeline = getCPUTimelineData(state.name);
      var max_time_val = cpuTimeline && sum(cpuTimeline, 'duration') || state.max_time_val;
      var max_time = ko.bindingHandlers.numberFormat.human(max_time_val, 5);
      state.max_time_val = max_time_val;
      state.max_time = max_time;
      state.cpu_timeline = cpuTimeline;
    });
    var avgStates = average(states, 'max_time_val');
    var edgesIO = edges.filter(function (edge) {
      return edge.content.unit === 5;
    });
    var edgesNonIO = edges.filter(function (edge) {
      return edge.content.unit === 0;
    });
    var avgEdgesIO = average(edgesIO, 'content.value');
    var avgEdgesNonIO = average(edgesNonIO, 'content.value');
    var avgCombined = averageCombined(avgStates, avgEdgesIO, states.length, edgesIO.length);
    var avg = { '0': avgEdgesNonIO, '5': avgCombined};
    // Keep a map of names to states for use when processing edges.
    states.forEach(function(state) {
      // Build the label for the node from the name and the detail
      var html = "<div attr-id='" + state.name + "'>";
      html += getIcon(state.icon);
      html += "<span style='display: inline-block;'><span class='name'>" + state.label + "</span>";
      var aboveAverageClass = state.max_time_val > avgStates ? 'above-average' : '';
      html += "<span class='metric " + aboveAverageClass + "'>" + state.max_time + "</span><br/>";
      html += "<span class='detail'>" + state.detail + "</span><br/>";
      if (state.predicates) {
        html += "<span class='detail'>" + state.predicates + "</span><br/>";
      }
      html += "<span class='id'>" + state.name + "</span></span>";
      html += renderTimeline(state.cpu_timeline, getMetricsMax());
      html += "</div>";

      var style = state.style;

      g.setNode(state.name, { "label": html,
                              "labelType": "html",
                              "style": style });
    });
    edges.forEach(function(edge) {
      // Impala marks 'broadcast' as a property of the receiver, not the sender. We use
      // '(BCAST)' to denote that a node is duplicating its output to all receivers.
      /*if (states_by_name[edge.end].is_broadcast) {
        if (states_by_name[edge.end].num_instances > 1) {
          edge.style.label += " * " + states_by_name[edge.end].num_instances;
        }
      }*/
      if (edge.content.value > avg[edge.content.unit]) {
        edge.style.labelStyle = "font-weight: bold";
      }
      g.setEdge(edge.start, edge.end, edge.style);
    });

    g.nodes().forEach(function(v) {
      var node = g.node(v);
      node.rx = node.ry = 5;
    });
    d3.select('#' + id + '.query-plan .details .metric-title').on('click', function () {
      toggleDetails();
    });

    // Create the renderer
    var render = new dagreD3.render();

    // Run the renderer. This is what draws the final graph.
    render(inner, g);
    d3.selectAll('#' + id + ' g.node').on('click', function () {
      d3.event.stopPropagation();
      var name = d3.select(this).select('div > div').attr('attr-id');
      select(getId(name));
    });

    // Center the graph, but only the first time through (so as to not lose user zooms).
    if (is_first) {
      var initialScale = 1;
      _impalaDagree.init(initialScale);
      is_first = false;
    }

  }

  return _impalaDagree;
}