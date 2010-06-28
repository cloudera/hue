/**
 * Returns a new stack layout.
 *
 * @class A layout for stacking marks vertically or horizontally, using the
 * <i>cousin</i> instance. This layout is designed to be used for one of the
 * four positional properties in the box model, and changes behavior depending
 * on the property being evaluated:<ul>
 *
 * <li>bottom: cousin.bottom + cousin.height
 * <li>top: cousin.top + cousin.height
 * <li>left: cousin.left + cousin.width
 * <li>right: cousin.right + cousin.width
 *
 * </ul>If no cousin instance is available (for example, for first instance),
 * the specified offset is used. If no offset is specified, zero is used. For
 * example,
 *
 * <pre>new pv.Panel()
 *     .width(150).height(150)
 *   .add(pv.Panel)
 *     .data([[1, 1.2, 1.7, 1.5, 1.7],
 *            [.5, 1, .8, 1.1, 1.3],
 *            [.2, .5, .8, .9, 1]])
 *   .add(pv.Area)
 *     .data(function(d) d)
 *     .bottom(pv.Layout.stack())
 *     .height(function(d) d * 40)
 *     .left(function() this.index * 35)
 *   .root.render();</pre>
 *
 * specifies a vertically-stacked area chart.
 *
 * @returns {pv.Layout.stack} a stack property function.
 * @see pv.Mark#cousin
 */
pv.Layout.stack = function() {
  /** @private */
  var offset = function() { return 0; };

  /** @private */
  function layout() {

    /* Find the previous visible parent instance. */
    var i = this.parent.index, p, c;
    while ((i-- > 0) && !c) {
      p = this.parent.scene[i];
      if (p.visible) c = p.children[this.childIndex][this.index];
    }

    if (c) {
      switch (property) {
        case "bottom": return c.bottom + c.height;
        case "top": return c.top + c.height;
        case "left": return c.left + c.width;
        case "right": return c.right + c.width;
      }
    }

    return offset.apply(this, arguments);
  }

  /**
   * Sets the offset for this stack layout. The offset can either be specified
   * as a function or as a constant. If a function, the function is invoked in
   * the same context as a normal property function: <tt>this</tt> refers to the
   * mark, and the arguments are the full data stack. By default the offset is
   * zero.
   *
   * @function
   * @name pv.Layout.stack.prototype.offset
   * @param {function} f offset function, or constant value.
   * @returns {pv.Layout.stack} this.
   */
  layout.offset = function(f) {
      offset = (f instanceof Function) ? f : function() { return f; };
      return this;
    };

  return layout;
};
