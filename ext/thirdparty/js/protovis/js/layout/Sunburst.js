// TODO share code with Treemap
// TODO inspect parent panel dimensions to set inner and outer radii

/**
 * Returns a new sunburst tree layout.
 *
 * @class A tree layout in the form of a sunburst. <img
 * src="../sunburst.png" width="160" height="160" align="right"> The
 * center circle corresponds to the root of the tree; subsequent rings
 * correspond to each tier. Rings are subdivided into wedges based on the size
 * of nodes, per {@link #size}. Within a ring, wedges are sorted by size.
 *
 * <p>The tree layout is intended to be extended (see {@link pv.Mark#extend} by
 * a {@link pv.Wedge}. The data property returns an array of nodes for use by
 * other property functions. The following node attributes are supported:
 *
 * <ul>
 * <li><tt>left</tt> - the wedge left position.
 * <li><tt>top</tt> - the wedge top position.
 * <li><tt>innerRadius</tt> - the wedge inner radius.
 * <li><tt>outerRadius</tt> - the wedge outer radius.
 * <li><tt>startAngle</tt> - the wedge start angle.
 * <li><tt>endAngle</tt> - the wedge end angle.
 * <li><tt>angle</tt> - the wedge angle.
 * <li><tt>depth</tt> - the node depth (tier; the root is 0).
 * <li><tt>keys</tt> - an array of string keys for the node.
 * <li><tt>size</tt> - the aggregate node size.
 * <li><tt>children</tt> - child nodes, if any.
 * <li><tt>data</tt> - the associated tree element, for leaf nodes.
 * </ul>
 *
 * <p>To produce a default sunburst layout, say:
 *
 * <pre>.add(pv.Wedge)
 *   .extend(pv.Layout.sunburst(tree))</pre>
 *
 * To only show nodes at a depth of two or greater, you might say:
 *
 * <pre>.add(pv.Wedge)
 *   .extend(pv.Layout.sunburst(tree))
 *   .visible(function(n) n.depth > 1)</pre>
 *
 * The format of the <tt>tree</tt> argument is a hierarchical object whose leaf
 * nodes are numbers corresponding to their size. For an example, and
 * information on how to convert tabular data into such a tree, see
 * {@link pv.Tree}. If the leaf nodes are not numbers, a {@link #size} function
 * can be specified to override how the tree is interpreted. This size function
 * can also be used to transform the data.
 *
 * <p>By default, the sunburst fills the full width and height of the parent
 * panel. An optional root key can be specified using {@link #root} for
 * convenience.
 *
 * @param tree a tree (an object) who leaf attributes have sizes.
 * @returns {pv.Layout.sunburst} a tree layout.
 */
pv.Layout.sunburst = function(tree) {
  var keys = [], sizeof = Number, w, h, r;

  /** @private */
  function accumulate(map) {
    var node = {size: 0, children: [], keys: keys.slice()};
    for (var key in map) {
      var child = map[key], size = sizeof(child);
      keys.push(key);
      if (isNaN(size)) {
        child = accumulate(child);
      } else {
        child = {size: size, data: child, keys: keys.slice()};
      }
      node.children.push(child);
      node.size += child.size;
      keys.pop();
    }
    node.children.sort(function(a, b) { return b.size - a.size; });
    return node;
  }

  /** @private */
  function scale(node, k) {
    node.size *= k;
    if (node.children) {
      for (var i = 0; i < node.children.length; i++) {
        scale(node.children[i], k);
      }
    }
  }

  /** @private */
  function depth(node, i) {
    i = i ? (i + 1) : 1;
    return node.children
        ? pv.max(node.children, function(n) { return depth(n, i); })
        : i;
  }

  /** @private */
  function layout(node) {
    if (node.children) {
      wedgify(node);
      for (var i = 0; i < node.children.length; i++) {
        layout(node.children[i]);
      }
    }
  }

  /** @private */
  function wedgify(node) {
    var startAngle = node.startAngle;
    for (var i = 0; i < node.children.length; i++) {
      var child = node.children[i], angle = (child.size / node.size) * node.angle;
      child.startAngle = startAngle;
      child.angle = angle;
      child.endAngle = startAngle + angle;
      child.depth = node.depth + 1;
      child.left = w / 2;
      child.top = h / 2;
      child.innerRadius = Math.max(0, child.depth - .5) * r;
      child.outerRadius = (child.depth + .5) * r;
      startAngle += angle;
      if (child.children) {
        wedgify(child);
      }
    }
  }

  /** @private */
  function flatten(node, array) {
    if (node.children) {
      for (var i = 0; i < node.children.length; i++) {
        flatten(node.children[i], array);
      }
    }
    array.push(node)
    return array;
  }

  /** @private */
  function data() {
    var root = accumulate(tree);
    w = this.parent.width();
    h = this.parent.height();
    r = Math.min(w, h) / 2 / (depth(root) - .5);
    root.left = w / 2;
    root.top = h / 2;
    root.startAngle = 0;
    root.angle = 2 * Math.PI;
    root.endAngle = 2 * Math.PI;
    root.innerRadius = 0;
    root.outerRadius = r;
    root.depth = 0;
    layout(root);
    return flatten(root, []).reverse();
  }

  /* A dummy mark, like an anchor, which the caller extends. */
  var mark = new pv.Mark()
      .data(data)
      .left(function(n) { return n.left; })
      .top(function(n) { return n.top; })
      .startAngle(function(n) { return n.startAngle; })
      .angle(function(n) { return n.angle; })
      .innerRadius(function(n) { return n.innerRadius; })
      .outerRadius(function(n) { return n.outerRadius; });

  /**
   * Specifies the root key; optional. The root key is prepended to the
   * <tt>keys</tt> attribute for all generated nodes. This method is provided
   * for convenience and does not affect layout.
   *
   * @param {string} v the root key.
   * @function
   * @name pv.Layout.sunburst.prototype.root
   * @returns {pv.Layout.sunburst} this.
   */
  mark.root = function(v) {
    keys = [v];
    return this;
  };

  /**
   * Specifies the sizing function. By default, the sizing function is
   * <tt>Number</tt>. The sizing function is invoked for each node in the tree
   * (passed to the constructor): the sizing function must return
   * <tt>undefined</tt> or <tt>NaN</tt> for internal nodes, and a number for
   * leaf nodes. The aggregate sizes of internal nodes will be automatically
   * computed by the layout.
   *
   * <p>For example, if the tree data structure represents a file system, with
   * files as leaf nodes, and each file has a <tt>bytes</tt> attribute, you can
   * specify a size function as:
   *
   * <pre>.size(function(d) d.bytes)</pre>
   *
   * This function will return <tt>undefined</tt> for internal nodes (since
   * these do not have a <tt>bytes</tt> attribute), and a number for leaf nodes.
   *
   * <p>Note that the built-in <tt>Math.sqrt</tt> and <tt>Math.log</tt> methods
   * can be used as sizing functions. These function similarly to
   * <tt>Number</tt>, except perform a root and log scale, respectively.
   *
   * @param {function} f the new sizing function.
   * @function
   * @name pv.Layout.sunburst.prototype.size
   * @returns {pv.Layout.sunburst} this.
   */
  mark.size = function(f) {
    sizeof = f;
    return this;
  };

  return mark;
};
