var guid = 0;

pv.SvgScene.panel = function(scenes) {
  var g = scenes.$g, e = g && g.firstChild;
  for (var i = 0; i < scenes.length; i++) {
    var s = scenes[i];

    /* visible */
    if (!s.visible) continue;

    /* svg */
    if (!scenes.parent) {
      s.canvas.style.display = "inline-block";
      g = s.canvas.firstChild;
      if (!g) {
        g = s.canvas.appendChild(this.create("svg"));
        g.onclick
            = g.onmousedown
            = g.onmouseup
            = g.onmousemove
            = g.onmouseout
            = g.onmouseover
            = pv.SvgScene.dispatch;
      }
      scenes.$g = g;
      g.setAttribute("width", s.width + s.left + s.right);
      g.setAttribute("height", s.height + s.top + s.bottom);
      if (typeof e == "undefined") e = g.firstChild;
    }

    /* clip (nest children) */
    if (s.overflow == "hidden") {
      var c = this.expect("g", e), id = (guid++).toString(36);
      c.setAttribute("clip-path", "url(#" + id + ")");
      if (!c.parentNode) g.appendChild(c);
      scenes.$g = g = c;
      e = c.firstChild;

      e = this.expect("clipPath", e);
      e.setAttribute("id", id);
      var r = e.firstChild ||  e.appendChild(this.create("rect"));
      r.setAttribute("x", s.left);
      r.setAttribute("y", s.top);
      r.setAttribute("width", s.width);
      r.setAttribute("height", s.height);
      if (!e.parentNode) g.appendChild(e);
      e = e.nextSibling;
    }

    /* fill */
    e = this.fill(e, scenes, i);

    /* children */
    for (var j = 0; j < s.children.length; j++) {
      s.children[j].$g = e = this.expect("g", e);
      e.setAttribute("transform", "translate(" + s.left + "," + s.top + ")");
      this.updateAll(s.children[j]);
      if (!e.parentNode) g.appendChild(e);
      e = e.nextSibling;
    }

    /* stroke */
    e = this.stroke(e, scenes, i);

    /* clip (restore group) */
    if (s.overflow == "hidden") {
      scenes.$g = g = c.parentNode;
      e = c.nextSibling;
    }
  }
  return e;
};

pv.SvgScene.fill = function(e, scenes, i) {
  var s = scenes[i], fill = pv.color(s.fillStyle);
  if (fill.opacity) {
    e = this.expect("rect", e);
    e.setAttribute("x", s.left);
    e.setAttribute("y", s.top);
    e.setAttribute("width", s.width);
    e.setAttribute("height", s.height);
    e.setAttribute("cursor", s.cursor);
    e.setAttribute("fill", fill.color);
    e.setAttribute("fill-opacity", fill.opacity);
    e = this.append(e, scenes, i);
  }
  return e;
};

pv.SvgScene.stroke = function(e, scenes, i) {
  var s = scenes[i], stroke = pv.color(s.strokeStyle);
  if (stroke.opacity) {
    e = this.expect("rect", e);
    e.setAttribute("x", s.left);
    e.setAttribute("y", s.top);
    e.setAttribute("width", Math.max(1E-10, s.width));
    e.setAttribute("height", Math.max(1E-10, s.height));
    e.setAttribute("cursor", s.cursor);
    e.setAttribute("fill", "none");
    e.setAttribute("stroke", stroke.color);
    e.setAttribute("stroke-opacity", stroke.opacity);
    e.setAttribute("stroke-width", s.lineWidth);
    e = this.append(e, scenes, i);
  }
  return e;
};
