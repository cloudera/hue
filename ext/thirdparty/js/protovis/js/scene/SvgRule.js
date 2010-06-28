pv.SvgScene.rule = function(scenes) {
  var e = scenes.$g.firstChild;
  for (var i = 0; i < scenes.length; i++) {
    var s = scenes[i];

    /* visible */
    if (!s.visible) continue;
    var stroke = pv.color(s.strokeStyle);
    if (!stroke.opacity) continue;

    e = this.expect("line", e);
    e.setAttribute("cursor", s.cursor);
    e.setAttribute("x1", s.left);
    e.setAttribute("y1", s.top);
    e.setAttribute("x2", s.left + s.width);
    e.setAttribute("y2", s.top + s.height);
    e.setAttribute("stroke", stroke.color);
    e.setAttribute("stroke-opacity", stroke.opacity);
    e.setAttribute("stroke-width", s.lineWidth);
    e = this.append(e, scenes, i);
  }
  return e;
};
