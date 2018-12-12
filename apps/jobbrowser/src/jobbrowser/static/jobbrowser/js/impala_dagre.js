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
  var _impalaDagree = {
    update: function(plan) {
      renderGraph(plan);
      _impalaDagree._width = $(svg[0]).width();
    },
    height: function(value) {
      var scale = _impalaDagree.scale || 1;
      var height = value || 600;
      _impalaDagree._height = height;
      svg.attr('height', Math.min(g.graph().height * scale + 40, height) || height);
    },
    action: function(type) {
      if (type == 'plus') {
        zoom.scale(zoom.scale() + 0.25);
        inner.attr("transform", "translate(" + zoom.translate() + ")" +
            "scale(" + zoom.scale() + ")");
      } else if (type == 'minus') {
        zoom.scale(zoom.scale() - 0.25);
        inner.attr("transform", "translate(" + zoom.translate() + ")" +
            "scale(" + zoom.scale() + ")");
      }
    },
    moveTo: function(id) {
      zoomToNode(id);
    },
    select: function(id) {
      select(id);
    },
  };
  createActions();

  function createActions () {
    d3.select("#"+id)
      .style('position', 'relative')
    .append('div')
      .style('position', 'absolute')
      .style('right', '5px')
      .style('bottom', '5px')
      .classed('button', true)
    .selectAll('button').data([{ type: 'plus', icon: 'fa-plus' }, { type: 'minus', icon: 'fa-minus' }])
    .enter()
    .append(function (data) {
       var button = $("<div class='fa fa-fw valign-middle " + data.icon + "'></div>")[0];
       $(button).on('click', function () {
         _impalaDagree.action(data.type);
       });
       return button;
    });
  }

  // Set up zoom support
  var zoom = d3.behavior.zoom().on("zoom", function() {
    var e = d3.event,
        scale = Math.min(Math.max(e.scale, Math.min(_impalaDagree._width / g.graph().width, _impalaDagree._height / g.graph().height)), 2),
        tx = Math.min(40, Math.max(e.translate[0], _impalaDagree._width - 40 - g.graph().width * scale)),
        ty = Math.min(40, Math.max(e.translate[1], _impalaDagree._height - 40 - g.graph().height * scale));
    _impalaDagree.scale = scale;
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
    if (!node["output_card"]) return;
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
    $("g.node").attr('class', 'node') // addClass doesn't work in svg on our version of jQuery
    $("g.node:contains('" + key + "')").attr('class', 'node active');
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
    var states_by_name = { };
    states.forEach(function(state) {
      // Build the label for the node from the name and the detail
      var html = "";
      if (state.icon && state.icon.svg) {
        html += '<svg class="hi"><use xlink:href="#'+ state.icon.svg +'"></use></svg>'
        //html += "<img src=\"" + icon.svg + "\"></img>";
      } else if (state.icon && state.icon.font){
        html += "<span class='fa fa-fw valign-middle " + state.icon.font + "'></span>";
      }
      html += "<span class='name'>" + state.label + "</span><br/>";
      html += "<span class='metric'>" + state.max_time + "</span>";
      html += "<span class='detail'>" + state.detail + "</span><br/>";
      html += "<span class='metric'>" + state.max_time + "</span>"
      html += "<span class='id'>" + state.name + "</span>";;

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
      _impalaDagree.scale = initialScale;
      zoom.translate([((svg.attr("width") || $("#"+id).width()) - g.graph().width * initialScale) / 2, 20])
        .scale(initialScale)
        .event(svg);
      svg.attr('height', Math.min(g.graph().height * initialScale + 40, 600));
      is_first = false;
    }

  }

  return _impalaDagree;
}