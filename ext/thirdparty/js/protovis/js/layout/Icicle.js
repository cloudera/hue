// TODO share code with Treemap
// TODO vertical / horizontal orientation?

/**
 * Returns a new icicle tree layout.
 *
 * @class A tree layout in the form of an icicle. <img src="../icicle.png"
 * width="160" height="160" align="right"> The first row corresponds to the root
 * of the tree; subsequent rows correspond to each tier. Rows are subdivided
 * into cells based on the size of nodes, per {@link #size}. Within a row, cells
 * are sorted by size.
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
 * To produce a default icicle layout, say:
 *
 * <pre>.add(pv.Bar)
 *   .extend(pv.Layout.icicle(tree))</pre>
 *
 * To customize the tree to highlight leaf nodes bigger than 10,000 (1E4), you
 * might say:
 *
 * <pre>.add(pv.Bar)
 *   .extend(pv.Layout.icicle(tree))
 *   .fillStyle(function(n) n.data > 1e4 ? "#ff0" : "#fff")</pre>
 *
 * The format of the <tt>tree</tt> argument is any hierarchical object whose
 * leaf nodes are numbers corresponding to their size. For an example, and
 * information on how to convert tabular data into such a tree, see
 * {@link pv.Tree}. If the leaf nodes are not numbers, a {@link #size} function
 * can be specified to override how the tree is interpreted. This size function
 * can also be used to transform the data.
 *
 * <p>By default, the icicle fills the full width and height of the parent
 * panel. An optional root key can be specified using {@link #root} for
 * convenience.
 *
 * @param tree a tree (an object) who leaf attributes have sizes.
 * @returns {pv.Layout.icicle} a tree layout.
 */
pv.Layout.icicle = function(tree) {
  var keys = [], sizeof = Number;

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
      icify(node);
      for (var i = 0; i < node.children.length; i++) {
        layout(node.children[i]);
      }
    }
  }

  /** @private */
  function icify(node) {
    var left = node.left;
    for (var i = 0; i < node.children.length; i++) {
      var child = node.children[i], width = (child.size / node.size) * node.width;
      child.left = left;
      child.top = node.top + node.height;
      child.width = width;
      child.height = node.height;
      child.depth = node.depth + 1;
      left += width;
      if (child.children) {
        icify(child);
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
    root.top = 0;
    root.left = 0;
    root.width = this.parent.width();
    root.height = this.parent.height() / depth(root);
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
   * Specifies the root key; optional. The root key is prepended to the
   * <tt>keys</tt> attribute for all generated nodes. This method is provided
   * for convenience and does not affect layout.
   *
   * @param {string} v the root key.
   * @function
   * @name pv.Layout.icicle.prototype.root
   * @returns {pv.Layout.icicle} this.
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
   * can also be used as sizing functions. These function similarly to
   * <tt>Number</tt>, except perform a root and log scale, respectively.
   *
   * @param {function} f the new sizing function.
   * @function
   * @name pv.Layout.icicle.prototype.size
   * @returns {pv.Layout.icicle} this.
   */
  mark.size = function(f) {
    sizeof = f;
    return this;
  };

  return mark;
};
