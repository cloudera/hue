pv.SvgScene.label = function(scenes) {
  var e = scenes.$g.firstChild;
  for (var i = 0; i < scenes.length; i++) {
    var s = scenes[i];

    /* visible */
    if (!s.visible) continue;
    var fill = pv.color(s.textStyle);
    if (!fill.opacity) continue;

    /* text-baseline, text-align */
    var x = 0, y = 0, dy = 0, anchor = "start";
    switch (s.textBaseline) {
      case "middle": dy = ".35em"; break;
      case "top": dy = ".71em"; y = s.textMargin; break;
      case "bottom": y = "-" + s.textMargin; break;
    }
    switch (s.textAlign) {
      case "right": anchor = "end"; x = "-" + s.textMargin; break;
      case "center": anchor = "middle"; break;
      case "left": x = s.textMargin; break;
    }

    e = this.expect("text", e);
    e.setAttribute("pointer-events", "none");
    e.setAttribute("x", x);
    e.setAttribute("y", y);
    e.setAttribute("dy", dy);
    e.setAttribute("text-anchor", anchor);
    e.setAttribute("transform",
        "translate(" + s.left + "," + s.top + ")"
        + (s.textAngle ? " rotate(" + 180 * s.textAngle / Math.PI + ")" : ""));
    e.setAttribute("fill", fill.color);
    e.setAttribute("fill-opacity", fill.opacity);
    e.style.font = s.font;
    e.style.textShadow = s.textShadow;
    if (e.firstChild) e.firstChild.nodeValue = s.text;
    else e.appendChild(document.createTextNode(s.text));
    e = this.append(e, scenes, i);
  }
  return e;
};
