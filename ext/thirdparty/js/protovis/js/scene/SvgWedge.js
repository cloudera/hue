pv.SvgScene.wedge = function(scenes) {
  var e = scenes.$g.firstChild;
  for (var i = 0; i < scenes.length; i++) {
    var s = scenes[i];

    /* visible */
    if (!s.visible) continue;
    var fill = pv.color(s.fillStyle), stroke = pv.color(s.strokeStyle);
    if (!fill.opacity && !stroke.opacity) continue;

    /* points */
    var r1 = s.innerRadius, r2 = s.outerRadius, a = Math.abs(s.angle), p;
    if (a >= 2 * Math.PI) {
      if (r1) {
        p = "M0," + r2
            + "A" + r2 + "," + r2 + " 0 1,1 0," + (-r2)
            + "A" + r2 + "," + r2 + " 0 1,1 0," + r2
            + "M0," + r1
            + "A" + r1 + "," + r1 + " 0 1,1 0," + (-r1)
            + "A" + r1 + "," + r1 + " 0 1,1 0," + r1
            + "Z";
      } else {
        p = "M0," + r2
            + "A" + r2 + "," + r2 + " 0 1,1 0," + (-r2)
            + "A" + r2 + "," + r2 + " 0 1,1 0," + r2
            + "Z";
      }
    } else {
      var sa = Math.min(s.startAngle, s.endAngle),
          ea = Math.max(s.startAngle, s.endAngle),
          c1 = Math.cos(sa), c2 = Math.cos(ea),
          s1 = Math.sin(sa), s2 = Math.sin(ea);
      if (r1) {
        p = "M" + r2 * c1 + "," + r2 * s1
            + "A" + r2 + "," + r2 + " 0 "
            + ((a < Math.PI) ? "0" : "1") + ",1 "
            + r2 * c2 + "," + r2 * s2
            + "L" + r1 * c2 + "," + r1 * s2
            + "A" + r1 + "," + r1 + " 0 "
            + ((a < Math.PI) ? "0" : "1") + ",0 "
            + r1 * c1 + "," + r1 * s1 + "Z";
      } else {
        p = "M" + r2 * c1 + "," + r2 * s1
            + "A" + r2 + "," + r2 + " 0 "
            + ((a < Math.PI) ? "0" : "1") + ",1 "
            + r2 * c2 + "," + r2 * s2 + "L0,0Z";
      }
    }

    e = this.expect("path", e);
    e.setAttribute("fill-rule", "evenodd");
    e.setAttribute("cursor", s.cursor);
    e.setAttribute("transform", "translate(" + s.left + "," + s.top + ")");
    e.setAttribute("d", p);
    e.setAttribute("fill", fill.color);
    e.setAttribute("fill-opacity", fill.opacity);
    e.setAttribute("stroke", stroke.color);
    e.setAttribute("stroke-opacity", stroke.opacity);
    e.setAttribute("stroke-width", s.lineWidth);
    e = this.append(e, scenes, i);
  }
  return e;
};
