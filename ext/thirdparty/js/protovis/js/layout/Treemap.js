// TODO add `by` function for determining size (and children?)

/**
 * Returns a new treemap tree layout.
 *
 * @class A tree layout in the form of an treemap. <img
 * src="../treemap.png" width="160" height="160" align="right"> Treemaps
 * are a form of space-filling layout that represents nodes as boxes, with child
 * nodes placed within parent boxes. The size of each box is proportional to the
 * size of the node in the tree.
 *
 * <p>This particular algorithm is taken from Bruls, D.M., C. Huizing, and
 * J.J. van Wijk, <a href="http://www.win.tue.nl/~vanwijk/stm.pdf">"Squarified
 * Treemaps"</a> in <i>Data Visualization 2000, Proceedings of the Joint
 * Eurographics and IEEE TCVG Sumposium on Visualization</i>, 2000,
 * pp. 33-42.
 *
 * <p>This tree layout is intended to be extended (see {@link pv.Mark#extend})
 * by a {@link pv.Bar}. The data property returns an array of nodes for use by
 * other property functions. The following node attributes are supported:
 *
 * <ul>
 * <li><tt>left</tt> - the cell left position.
 * <li><tt>top</tt> - the cell top position.
 * <li><tt>width</tt> - the cell width.
 * <li><tt>height</tt> - the cell height.
 * <li><tt>depth</tt> - the node depth (tier; the root is 0).
 * <li><tt>keys</tt> - an array of string keys for the node.
 * <li><tt>size</tt> - the aggregate node size.
 * <li><tt>children</tt> - child nodes, if any.
 * <li><tt>data</tt> - the associated tree element, for leaf nodes.
 * </ul>
 *
 * To produce a default treemap layout, say:
 *
 * <pre>.add(pv.Bar)
 *   .extend(pv.Layout.treemap(tree))</pre>
 *
 * To display internal nodes, and color by depth, say:
 *
 * <pre>.add(pv.Bar)
 *   .extend(pv.Layout.treemap(tree).inset(10))
 *   .fillStyle(pv.Colors.category19().by(function(n) n.depth))</pre>
 *
 * The format of the <tt>tree</tt> argument is a hierarchical object whose leaf
 * nodes are numbers corresponding to their size. For an example, and
 * information on how to convert tabular data into such a tree, see
 * {@link pv.Tree}. If the leaf nodes are not numbers, a {@link #size} function
 * can be specified to override how the tree is interpreted. This size function
 * can also be used to transform the data.
 *
 * <p>By default, the treemap fills the full width and height of the parent
 * panel, and only leaf nodes are rendered. If an {@link #inset} is specified,
 * internal nodes will be rendered, each inset from their parent by the
 * specified margins. Rounding can be enabled using {@link #round}. Finally, an
 * optional root key can be specified using {@link #root} for convenience.
 *
 * @param tree a tree (an object) who leaf attributes have sizes.
 * @returns {pv.Layout.treemap} a tree layout.
 */
pv.Layout.treemap = function(tree) {
  var keys = [], round, inset, sizeof = Number;

  /** @private */
  function rnd(i) {
    return round ? Math.round(i) : i;
  }

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
    node.children.sort(function(a, b) { return a.size - b.size; });
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
  function ratio(row, l) {
    var rmax = -Infinity, rmin = Infinity, s = 0;
    for (var i = 0; i < row.length; i++) {
      var r = row[i].size;
      if (r < rmin) rmin = r;
      if (r > rmax) rmax = r;
      s += r;
    }
    s = s * s;
    l = l * l;
    return Math.max(l * rmax / s, s / (l * rmin));
  }

  /** @private */
  function squarify(node) {
    var row = [], mink = Infinity;
    var x = node.left + (inset ? inset.left : 0),
        y = node.top + (inset ? inset.top : 0),
        w = node.width - (inset ? inset.left + inset.right : 0),
        h = node.height - (inset ? inset.top + inset.bottom : 0),
        l = Math.min(w, h);

    scale(node, w * h / node.size);

    function position(row) {
      var s = pv.sum(row, function(node) { return node.size; }),
          hh = (l == 0) ? 0 : rnd(s / l);

      for (var i = 0, d = 0; i < row.length; i++) {
        var n = row[i], nw = rnd(n.size / hh);
        if (w == l) {
          n.left = x + d;
          n.top = y;
          n.width = nw;
          n.height = hh;
        } else {
          n.left = x;
          n.top = y + d;
          n.width = hh;
          n.height = nw;
        }
        d += nw;
      }

      if (w == l) {
        if (n) n.width += w - d; // correct rounding error
        y += hh;
        h -= hh;
      } else {
        if (n) n.height += h - d; // correct rounding error
        x += hh;
        w -= hh;
      }
      l = Math.min(w, h);
    }

    var children = node.children.slice(); // copy
    while (children.length > 0) {
      var child = children[children.length - 1];
      if (child.size <= 0) {
        children.pop();
        continue;
      }
      row.push(child);

      var k = ratio(row, l);
      if (k <= mink) {
        children.pop();
        mink = k;
      } else {
        row.pop();
        position(row);
        row.length = 0;
        mink = Infinity;
      }
    }

    if (row.length > 0) {
      position(row);
    }

    /* correct rounding error */
    if (w == l) {
      for (var i = 0; i < row.length; i++) {
        row[i].width += w;
      }
    } else {
      for (var i = 0; i < row.length; i++) {
        row[i].height += h;
      }
    }
  }

  /** @private */
  function layout(node) {
    if (node.children) {
      squarify(node);
      for (var i = 0; i < node.children.length; i++) {
        var child = node.children[i];
        child.depth = node.depth + 1;
        layout(child);
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
    if (inset || !node.children) {
      array.push(node)
    }
    return array;
  }

  /** @private */
  function data() {
    var root = accumulate(tree);
    root.left = 0;
    root.top = 0;
    root.width = this.parent.width();
    root.height = this.parent.height();
    root.depth = 0;
    layout(root);
    return flatten(root, []).reverse();
  }

  /* A dummy mark, like an anchor, which the caller extends. */
  var mark = new pv.Mark()
      .data(data)
      .left(function(n) { return n.left; })
      .top(function(n) { return n.top; })
      .width(function(n) { return n.width; })
      .height(function(n) { return n.height; });

  /**
   * Enables or disables rounding. When rounding is enabled, the left, top,
   * width and height properties will be rounded to integer pixel values. The
   * rounding algorithm uses error accumulation to ensure an exact fit.
   *
   * @param {boolean} v whether rounding should be enabled.
   * @function
   * @name pv.Layout.treemap.prototype.round
   * @returns {pv.Layout.treemap} this.
   */
  mark.round = function(v) {
    round = v;
    return this;
  };

  /**
   * Specifies the margins to inset child nodes from their parents; as a side
   * effect, this also enables the display of internal nodes, which are hidden
   * by default. If only a single argument is specified, this value is used to
   * inset all four sides.
   *
   * @param {number} top the top margin.
   * @param {number} [right] the right margin.
   * @param {number} [bottom] the bottom margin.
   * @param {number} [left] the left margin.
   * @function
   * @name pv.Layout.treemap.prototype.inset
   * @returns {pv.Layout.treemap} this.
   */
  mark.inset = function(top, right, bottom, left) {
    if (arguments.length == 1) right = bottom = left = top;
    inset = {top:top, right:right, bottom:bottom, left:left};
    return this;
  };

  /**
   * Specifies the root key; optional. The root key is prepended to the
   * <tt>keys</tt> attribute for all generated nodes. This method is provided
   * for convenience and does not affect layout.
   *
   * @param {string} v the root key.
   * @function
   * @name pv.Layout.treemap.prototype.root
   * @returns {pv.Layout.treemap} this.
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
   * @name pv.Layout.treemap.prototype.size
   * @returns {pv.Layout.treemap} this.
   */
  mark.size = function(f) {
    sizeof = f;
    return this;
  };

  return mark;
};
