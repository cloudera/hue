pv.SvgScene.image = function(scenes) {
  var e = scenes.$g.firstChild;
  for (var i = 0; i < scenes.length; i++) {
    var s = scenes[i];

    /* visible */
    if (!s.visible) continue;

    /* fill */
    e = this.fill(e, scenes, i);

    /* image */
    e = this.expect("image", e);
    e.setAttribute("preserveAspectRatio", "none");
    e.setAttribute("x", s.left);
    e.setAttribute("y", s.top);
    e.setAttribute("width", s.width);
    e.setAttribute("height", s.height);
    e.setAttribute("cursor", s.cursor);
    e.setAttributeNS(pv.ns.xlink, "href", s.url);
    e = this.append(e, scenes, i);

    /* stroke */
    e = this.stroke(e, scenes, i);
  }
  return e;
};
