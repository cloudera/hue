/**
 * Returns a new grid layout.
 *
 * @class A grid layout with regularly-sized rows and columns. <img
 * src="../grid.png" width="160" height="160" align="right"> The number of rows
 * and columns are determined from the array, which should be in row-major
 * order. For example, the 2&times;3 array:
 *
 * <pre>1 2 3
 * 4 5 6</pre>
 *
 * should be represented as:
 *
 * <pre>[[1, 2, 3], [4, 5, 6]]</pre>
 *
 * If your data is in column-major order, you can use {@link pv.transpose} to
 * transpose it.
 *
 * <p>This layout defines left, top, width, height and data properties. The data
 * property will be the associated element in the array. For example, if the
 * array is a two-dimensional array of values in the range [0,1], a simple
 * heatmap can be generated as:
 *
 * <pre>.add(pv.Bar)
 *   .extend(pv.Layout.grid(array))
 *   .fillStyle(pv.ramp("white", "black"))</pre>
 *
 * By default, the grid fills the full width and height of the parent panel.
 *
 * @param {array[]} arrays an array of arrays.
 * @returns {pv.Layout.grid} a grid layout.
 */
pv.Layout.grid = function(arrays) {
  var rows = arrays.length, cols = arrays[0].length;

  /** @private */
  function w() { return this.parent.width() / cols; }

  /** @private */
  function h() { return this.parent.height() / rows; }

  /* A dummy mark, like an anchor, which the caller extends. */
  return new pv.Mark()
      .data(pv.blend(arrays))
      .left(function() { return w.call(this) * (this.index % cols); })
      .top(function() { return h.call(this) * Math.floor(this.index / cols); })
      .width(w)
      .height(h);
};
