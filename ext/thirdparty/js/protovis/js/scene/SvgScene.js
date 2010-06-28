// TODO don't populate default attributes?

/**
 * @private
 * @namespace
 */
pv.Scene = pv.SvgScene = {};

/**
 * Updates the display for the specified array of scene nodes.
 *
 * @param scenes {array} an array of scene nodes.
 */
pv.SvgScene.updateAll = function(scenes) {
  if (!scenes.length) return;
  if ((scenes[0].reverse)
      && (scenes.type != "line")
      && (scenes.type != "area")) {
    var reversed = pv.extend(scenes);
    for (var i = 0, j = scenes.length - 1; j >= 0; i++, j--) {
      reversed[i] = scenes[j];
    }
    scenes = reversed;
  }
  this.removeSiblings(this[scenes.type](scenes));
};

/**
 * Creates a new SVG element of the specified type.
 *
 * @param type {string} an SVG element type, such as "rect".
 * @return a new SVG element.
 */
pv.SvgScene.create = function(type) {
  return document.createElementNS(pv.ns.svg, type);
};

/**
 * Expects the element <i>e</i> to be the specified type. If the element does
 * not exist, a new one is created. If the element does exist but is the wrong
 * type, it is replaced with the specified element.
 *
 * @param type {string} an SVG element type, such as "rect".
 * @return a new SVG element.
 */
pv.SvgScene.expect = function(type, e) {
  if (!e) return this.create(type);
  if (e.tagName == "a") e = e.firstChild;
  if (e.tagName == type) return e;
  var n = this.create(type);
  e.parentNode.replaceChild(n, e);
  return n;
};

/** TODO */
pv.SvgScene.append = function(e, scenes, index) {
  e.$scene = {scenes:scenes, index:index};
  e = this.title(e, scenes[index]);
  if (!e.parentNode) scenes.$g.appendChild(e);
  return e.nextSibling;
};

/**
 * Applies a title tooltip to the specified element <tt>e</tt>, using the
 * <tt>title</tt> property of the specified scene node <tt>s</tt>. Note that
 * this implementation does not create an SVG <tt>title</tt> element as a child
 * of <tt>e</tt>; although this is the recommended standard, it is only
 * supported in Opera. Instead, an anchor element is created around the element
 * <tt>e</tt>, and the <tt>xlink:title</tt> attribute is set accordingly.
 *
 * @param e an SVG element.
 * @param s a scene node.
 */
pv.SvgScene.title = function(e, s) {
  var a = e.parentNode, t = String(s.title);
  if (a && (a.tagName != "a")) a = null;
  if (t) {
    if (!a) {
      a = this.create("a");
      if (e.parentNode) e.parentNode.replaceChild(a, e);
      a.appendChild(e);
    }
    a.setAttributeNS(pv.ns.xlink, "title", t);
    return a;
  }
  if (a) a.parentNode.replaceChild(e, a);
  return e;
};

/** TODO */
pv.SvgScene.dispatch = function(e) {
  var t = e.target.$scene;
  if (t) {
    t.scenes.mark.dispatch(e.type, t.scenes, t.index);
    e.preventDefault();
  }
};

/** TODO */
pv.SvgScene.removeSiblings = function(e) {
  while (e) {
    var n = e.nextSibling;
    e.parentNode.removeChild(e);
    e = n;
  }
};
