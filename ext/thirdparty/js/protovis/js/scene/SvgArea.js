// TODO strokeStyle for areaSegment?

pv.SvgScene.area = function(scenes) {
  var e = scenes.$g.firstChild;
  if (!scenes.length) return e;
  var s = scenes[0];

  /* segmented */
  if (s.segmented) return this.areaSegment(scenes);

  /* visible */
  if (!s.visible) return e;
  var fill = pv.color(s.fillStyle), stroke = pv.color(s.strokeStyle);
  if (!fill.opacity && !stroke.opacity) return e;

  /* points */
  var p1 = "", p2 = "";
  for (var i = 0, j = scenes.length - 1; j >= 0; i++, j--) {
    var si = scenes[i], sj = scenes[j];
    p1 += si.left + "," + si.top + " ";
    p2 += (sj.left + sj.width) + "," + (sj.top + sj.height) + " ";

    /* interpolate (assume linear by default) */
    if (i < scenes.length - 1) {
      var sk = scenes[i + 1], sl = scenes[j - 1];
      switch (s.interpolate) {
        case "step-before": {
          p1 += si.left + "," + sk.top + " ";
          p2 += (sl.left + sl.width) + "," + (sj.top + sj.height) + " ";
          break;
        }
        case "step-after": {
          p1 += sk.left + "," + si.top + " ";
          p2 += (sj.left + sj.width) + "," + (sl.top + sl.height) + " ";
          break;
        }
      }
    }
  }

  e = this.expect("polygon", e);
  e.setAttribute("cursor", s.cursor);
  e.setAttribute("points", p1 + p2);
  var fill = pv.color(s.fillStyle);
  e.setAttribute("fill", fill.color);
  e.setAttribute("fill-opacity", fill.opacity);
  var stroke = pv.color(s.strokeStyle);
  e.setAttribute("stroke", stroke.color);
  e.setAttribute("stroke-opacity", stroke.opacity);
  e.setAttribute("stroke-width", s.lineWidth);
  return this.append(e, scenes, 0);
};

pv.SvgScene.areaSegment = function(scenes) {
  var e = scenes.$g.firstChild;
  for (var i = 0, n = scenes.length - 1; i < n; i++) {
    var s1 = scenes[i], s2 = scenes[i + 1];

    /* visible */
    if (!s1.visible || !s2.visible) continue;
    var fill = pv.color(s1.fillStyle), stroke = pv.color(s1.strokeStyle);
    if (!fill.opacity && !stroke.opacity) continue;

    /* points */
    var p = s1.left + "," + s1.top + " "
        + s2.left + "," + s2.top + " "
        + (s2.left + s2.width) + "," + (s2.top + s2.height) + " "
        + (s1.left + s1.width) + "," + (s1.top + s1.height);

    e = this.expect("polygon", e);
    e.setAttribute("cursor", s1.cursor);
    e.setAttribute("points", p);
    e.setAttribute("fill", fill.color);
    e.setAttribute("fill-opacity", fill.opacity);
    e.setAttribute("stroke", stroke.color);
    e.setAttribute("stroke-opacity", stroke.opacity);
    e.setAttribute("stroke-width", s1.lineWidth);
    e = this.append(e, scenes, i);
  }
  return e;
};
