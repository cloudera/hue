pv.SvgScene.dot = function(scenes) {
  var e = scenes.$g.firstChild;
  for (var i = 0; i < scenes.length; i++) {
    var s = scenes[i];

    /* visible */
    if (!s.visible) continue;
    var fill = pv.color(s.fillStyle), stroke = pv.color(s.strokeStyle);
    if (!fill.opacity && !stroke.opacity) continue;

    /* points */
    var radius = Math.sqrt(s.size), fillPath = "", strokePath = "";
    switch (s.shape) {
      case "cross": {
        fillPath = "M" + -radius + "," + -radius
            + "L" + radius + "," + radius
            + "M" + radius + "," + -radius
            + "L" + -radius + "," + radius;
        break;
      }
      case "triangle": {
        var h = radius, w = radius * 2 / Math.sqrt(3);
        fillPath = "M0," + h
            + "L" + w +"," + -h
            + " " + -w + "," + -h
            + "Z";
        break;
      }
      case "diamond": {
        radius *= Math.sqrt(2);
        fillPath = "M0," + -radius
            + "L" + radius + ",0"
            + " 0," + radius
            + " " + -radius + ",0"
            + "Z";
        break;
      }
      case "square": {
        fillPath = "M" + -radius + "," + -radius
            + "L" + radius + "," + -radius
            + " " + radius + "," + radius
            + " " + -radius + "," + radius
            + "Z";
        break;
      }
      case "tick": {
        fillPath = "M0,0L0," + -s.size;
        break;
      }
      default: {
        function circle(r) {
          return "M0," + r
              + "A" + r + "," + r + " 0 1,1 0," + (-r)
              + "A" + r + "," + r + " 0 1,1 0," + r
              + "Z";
        }
        if (s.lineWidth / 2 > radius) strokePath = circle(s.lineWidth);
        fillPath = circle(radius);
        break;
      }
    }

    /* transform */
    var transform = "translate(" + s.left + "," + s.top + ")"
        + (s.angle ? " rotate(" + 180 * s.angle / Math.PI + ")" : "");

    /* The normal fill path. */
    e = this.expect("path", e);
    e.setAttribute("d", fillPath);
    e.setAttribute("transform", transform);
    e.setAttribute("fill", fill.color);
    e.setAttribute("fill-opacity", fill.opacity);
    e.setAttribute("cursor", s.cursor);
    if (strokePath) {
      e.setAttribute("stroke", "none");
    } else {
      e.setAttribute("stroke", stroke.color);
      e.setAttribute("stroke-opacity", stroke.opacity);
      e.setAttribute("stroke-width", s.lineWidth);
    }
    e = this.append(e, scenes, i);

    /* The special-case stroke path. */
    if (strokePath) {
      e = this.expect("path", e);
      e.setAttribute("d", strokePath);
      e.setAttribute("transform", transform);
      e.setAttribute("fill", stroke.color);
      e.setAttribute("fill-opacity", stroke.opacity);
      e.setAttribute("cursor", s.cursor);
      e = this.append(e, scenes, i);
    }
  }
  return e;
};
