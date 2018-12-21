/* Builds and then renders a plan graph using Dagre / D3. The JSON for the current query
is retrieved by an HTTP call, and then the graph of nodes and edges is built by walking
over each plan fragment in turn. Plan fragments are connected wherever a node has a
data_stream_target attribute.
<script src="desktop/ext/js/d3.v3.js"></script>
<script src="desktop/ext/js/dagre-d3-min.js"></script>
Copied from https://github.com/apache/incubator-impala/blob/master/www/query_plan.tmpl
*/
function impalaDagre(id) {
  var d3 = window.d3v3;
  var dagreD3 = window.dagreD3;
  var g = new dagreD3.graphlib.Graph().setGraph({rankDir: "BT"});
  var svg = d3.select("#"+id + " svg");
  var inner = svg.select("g");
  var states_by_name = { };
  var _impalaDagree = {
    _metrics: {},
    init: function (initialScale) {
      clearSelection();
      zoom.translate([((svg.attr("width") || $("#"+id).width()) - g.graph().width * initialScale) / 2, 20])
      .scale(initialScale)
      .event(svg);
    },
    metrics: function(metrics) {
      _impalaDagree._metrics = metrics;
    },
    update: function(plan) {
      renderGraph(plan);
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
      hideDetail();
      clearSelection();
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
    d3.select("#"+id)
    .append('div')
      .classed('details', true);
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
  function build(node, parent, edges, states, colour_idx, max_node_time) {
    if (node["output_card"] === null || node["output_card"] === undefined) {
      return;
    }
    states.push({ "name": node["label"],
                  "type": node["type"],
                  "label": node["name"],
                  "detail": node["label_detail"],
                  "num_instances": node["num_instances"],
                  "num_active": node["num_active"],
                  "max_time": node["max_time"],
                  "avg_time": node["avg_time"],
                  "icon": node["icon"],
                  "is_broadcast": node["is_broadcast"],
                  "max_time_val": node["max_time_val"]});
    if (parent) {
      var label_val = "" + node["output_card"].toLocaleString();
      edges.push({ start: node["label"], end: parent,
                   style: { label: label_val }});
    }
    // Add an inter-fragment edge. We use a red dashed line to show that rows are crossing
    // the fragment boundary.
    if (node["data_stream_target"]) {
      edges.push({ "start": node["label"],
                   "end": node["data_stream_target"],
                   "style": { label: "" + node["output_card"].toLocaleString(),
                              style: "stroke-dasharray: 5, 5;"}});
    }
    max_node_time = Math.max(node["max_time_val"], max_node_time)
    for (var i = 0; i < node["children"].length; ++i) {
      max_node_time = build(
        node["children"][i], node["label"], edges, states, colour_idx, max_node_time);
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
    $("g.node:contains('" + key + "')").attr('class', 'node active');
    showDetail(node);
  }

  function clearSelection() {
    $("g.node").attr('class', 'node'); // addClass doesn't work in svg on our version of jQuery
  }

  function getKey(node) {
    var nodes = g.nodes();
    var key;
    var nNode = parseInt(node, 10);
    var keys = Object.keys(nodes);
    for (var i = 0; i < keys.length; i++) {
      if (parseInt(nodes[keys[i]].split(':')[0], 10) == nNode) {
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
    var n = $("g.node:contains('" + key + "')")[0];
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

  function showDetail(id) {
    var data;
    if (_impalaDagree._metrics[id] && _impalaDagree._metrics[id]['averaged']) {
      data = _impalaDagree._metrics[id]['averaged'];
    } else if (_impalaDagree._metrics[id]) {
      data = _impalaDagree._metrics[id][Object.keys(_impalaDagree._metrics[id])[0]];
    }
    d3.select('.query-plan').classed('open', true);
    var title = d3.select('.query-plan .details')
    .selectAll('.metric-title').data([0]);
    title.enter().append('div').classed('metric-title', true);
    var key = getKey(id);
    title.html(getIcon(states_by_name[key].icon) + '<span>' + states_by_name[key].label+ '</span>');

    var metricTitle = d3.select('.query-plan .details')
    .selectAll('.metrics').data([0]);
    metricTitle.enter().append('div').classed('metrics', true);

    var metrics = d3.select('.query-plan .details .metrics').selectAll('div')
    .data(Object.keys(data).sort().map(function (key) { return data[key]; }));
    metrics.exit().remove();
    metrics.enter().append('div');
    metrics.html(function (datum) { return '<div class="metric-name">' + datum.name + '</div> : <div class="metric-value">' + ko.bindingHandlers.numberFormat.human(datum.value, datum.unit) + '</div>'; });
  }

  function hideDetail(id) {
    d3.select('.query-plan').classed('open', false);
  }

  function renderGraph(plan) {
    if (!plan || !plan.plan_nodes || !plan.plan_nodes.length) return;
    var states = [];
    var edges = [];
    var colour_idx = 0;

    var max_node_time = 0;
    plan["plan_nodes"].forEach(function(parent) {
      max_node_time = Math.max(
        build(parent, null, edges, states, colour_idx, max_node_time));
      // Pick a new colour for each plan fragment
      colour_idx = (colour_idx + 1) % colours.length;
    });

    // Keep a map of names to states for use when processing edges.
    states.forEach(function(state) {
      // Build the label for the node from the name and the detail
      var html = "<div onclick=\"event.stopPropagation(); huePubSub.publish('impala.node.select', " + parseInt(state.name.split(':')[0], 10) + ");\">"; // TODO: Remove Hue dependency
      html += getIcon(state.icon)
      html += "<span class='name'>" + state.label + "</span><br/>";
      html += "<span class='metric'>" + state.max_time + "</span>";
      html += "<span class='detail'>" + state.detail + "</span><br/>";
      html += "<span class='metric'>" + state.max_time + "</span>"
      html += "<span class='id'>" + state.name + "</span>";
      html += "</div>";

      var style = state.style;

      // If colouring nodes by total time taken, choose a shade in the cols_by_time list
      // with idx proportional to the max time of the node divided by the max time over all
      // nodes.
      /*if (document.getElementById("colour_scheme").checked) {
        var idx = (cols_by_time.length - 1) * (state.max_time_val / (1.0 * max_node_time));
        style = "fill: " + cols_by_time[Math.floor(idx)];
      }*/
      g.setNode(state.name, { "label": html,
                              "labelType": "html",
                              "style": style });
      states_by_name[state.name] = state;
    });

    edges.forEach(function(edge) {
      // Impala marks 'broadcast' as a property of the receiver, not the sender. We use
      // '(BCAST)' to denote that a node is duplicating its output to all receivers.
      if (states_by_name[edge.end].is_broadcast) {
        edge.style.label += " * " + states_by_name[edge.end].num_instances;
      }
      g.setEdge(edge.start, edge.end, edge.style);
    });

    g.nodes().forEach(function(v) {
      var node = g.node(v);
      node.rx = node.ry = 5;
    });

    // Create the renderer
    var render = new dagreD3.render();

    // Run the renderer. This is what draws the final graph.
    render(inner, g);

    // Center the graph, but only the first time through (so as to not lose user zooms).
    if (is_first) {
      var initialScale = 1;
      _impalaDagree.init(initialScale);
      svg.attr('height', Math.min(g.graph().height * initialScale + 40, 600));
      is_first = false;
    }

  }

  return _impalaDagree;
}