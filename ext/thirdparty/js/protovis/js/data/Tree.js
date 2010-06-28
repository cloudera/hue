/**
 * Returns a {@link pv.Tree} operator for the specified array. This is a
 * convenience factory method, equivalent to <tt>new pv.Tree(array)</tt>.
 *
 * @see pv.Tree
 * @param {array} array an array from which to construct a tree.
 * @returns {pv.Tree} a tree operator for the specified array.
 */
pv.tree = function(array) {
  return new pv.Tree(array);
};

/**
 * Constructs a tree operator for the specified array. This constructor should
 * not be invoked directly; use {@link pv.tree} instead.
 *
 * @class Represents a tree operator for the specified array. The tree operator
 * allows a hierarchical map to be constructed from an array; it is similar to
 * the {@link pv.Nest} operator, except the hierarchy is derived dynamically
 * from the array elements.
 *
 * <p>For example, given an array of size information for ActionScript classes:
 *
 * <pre>{ name: "flare.flex.FlareVis", size: 4116 },
 * { name: "flare.physics.DragForce", size: 1082 },
 * { name: "flare.physics.GravityForce", size: 1336 }, ...</pre>
 *
 * To facilitate visualization, it may be useful to nest the elements by their
 * package hierarchy:
 *
 * <pre>var tree = pv.tree(classes)
 *     .keys(function(d) d.name.split("."))
 *     .map();</pre>
 *
 * The resulting tree is:
 *
 * <pre>{ flare: {
 *     flex: {
 *       FlareVis: {
 *         name: "flare.flex.FlareVis",
 *         size: 4116 } },
 *     physics: {
 *       DragForce: {
 *         name: "flare.physics.DragForce",
 *         size: 1082 },
 *       GravityForce: {
 *         name: "flare.physics.GravityForce",
 *         size: 1336 } },
 *     ... } }</pre>
 *
 * By specifying a value function,
 *
 * <pre>var tree = pv.tree(classes)
 *     .keys(function(d) d.name.split("."))
 *     .value(function(d) d.size)
 *     .map();</pre>
 *
 * we can further eliminate redundant data:
 *
 * <pre>{ flare: {
 *     flex: {
 *       FlareVis: 4116 },
 *     physics: {
 *       DragForce: 1082,
 *       GravityForce: 1336 },
 *   ... } }</pre>
 *
 * For visualizations with large data sets, performance improvements may be seen
 * by storing the data in a tree format, and then flattening it into an array at
 * runtime with {@link pv.Flatten}.
 *
 * @param {array} array an array from which to construct a tree.
 */
pv.Tree = function(array) {
  this.array = array;
};

/**
 * Assigns a <i>keys</i> function to this operator; required. The keys function
 * returns an array of <tt>string</tt>s for each element in the associated
 * array; these keys determine how the elements are nested in the tree. The
 * returned keys should be unique for each element in the array; otherwise, the
 * behavior of this operator is undefined.
 *
 * @param {function} k the keys function.
 * @returns {pv.Tree} this.
 */
pv.Tree.prototype.keys = function(k) {
  this.k = k;
  return this;
};

/**
 * Assigns a <i>value</i> function to this operator; optional. The value
 * function specifies an optional transformation of the element in the array
 * before it is inserted into the map. If no value function is specified, it is
 * equivalent to using the identity function.
 *
 * @param {function} k the value function.
 * @returns {pv.Tree} this.
 */
pv.Tree.prototype.value = function(v) {
  this.v = v;
  return this;
};

/**
 * Returns a hierarchical map of values. The hierarchy is determined by the keys
 * function; the values in the map are determined by the value function.
 *
 * @returns a hierarchical map of values.
 */
pv.Tree.prototype.map = function() {
  var map = {}, o = {};
  for (var i = 0; i < this.array.length; i++) {
    o.index = i;
    var value = this.array[i], keys = this.k.call(o, value), node = map;
    for (var j = 0; j < keys.length - 1; j++) {
      node = node[keys[j]] || (node[keys[j]] = {});
    }
    node[keys[j]] = this.v ? this.v.call(o, value) : value;
  }
  return map;
};
