/**
 * Returns a {@link pv.Nest} operator for the specified array. This is a
 * convenience factory method, equivalent to <tt>new pv.Nest(array)</tt>.
 *
 * @see pv.Nest
 * @param {array} array an array of elements to nest.
 * @returns {pv.Nest} a nest operator for the specified array.
 */
pv.nest = function(array) {
  return new pv.Nest(array);
};

/**
 * Constructs a nest operator for the specified array. This constructor should
 * not be invoked directly; use {@link pv.nest} instead.
 *
 * @class Represents a {@link Nest} operator for the specified array. Nesting
 * allows elements in an array to be grouped into a hierarchical tree
 * structure. The levels in the tree are specified by <i>key</i> functions. The
 * leaf nodes of the tree can be sorted by value, while the internal nodes can
 * be sorted by key. Finally, the tree can be returned either has a
 * multidimensional array via {@link #entries}, or as a hierarchical map via
 * {@link #map}. The {@link #rollup} routine similarly returns a map, collapsing
 * the elements in each leaf node using a summary function.
 *
 * <p>For example, consider the following tabular data structure of Barley
 * yields, from various sites in Minnesota during 1931-2:
 *
 * <pre>{ yield: 27.00, variety: "Manchuria", year: 1931, site: "University Farm" },
 * { yield: 48.87, variety: "Manchuria", year: 1931, site: "Waseca" },
 * { yield: 27.43, variety: "Manchuria", year: 1931, site: "Morris" }, ...</pre>
 *
 * To facilitate visualization, it may be useful to nest the elements first by
 * year, and then by variety, as follows:
 *
 * <pre>var nest = pv.nest(yields)
 *     .key(function(d) d.year)
 *     .key(function(d) d.variety)
 *     .entries();</pre>
 *
 * This returns a nested array. Each element of the outer array is a key-values
 * pair, listing the values for each distinct key:
 *
 * <pre>{ key: 1931, values: [
 *   { key: "Manchuria", values: [
 *       { yield: 27.00, variety: "Manchuria", year: 1931, site: "University Farm" },
 *       { yield: 48.87, variety: "Manchuria", year: 1931, site: "Waseca" },
 *       { yield: 27.43, variety: "Manchuria", year: 1931, site: "Morris" },
 *       ...
 *     ] },
 *   { key: "Glabron", values: [
 *       { yield: 43.07, variety: "Glabron", year: 1931, site: "University Farm" },
 *       { yield: 55.20, variety: "Glabron", year: 1931, site: "Waseca" },
 *       ...
 *     ] },
 *   ] },
 * { key: 1932, values: ... }</pre>
 *
 * Further details, including sorting and rollup, is provided below on the
 * corresponding methods.
 *
 * @param {array} array an array of elements to nest.
 */
pv.Nest = function(array) {
  this.array = array;
  this.keys = [];
};

/**
 * Nests using the specified key function. Multiple keys may be added to the
 * nest; the array elements will be nested in the order keys are specified.
 *
 * @param {function} key a key function; must return a string or suitable map
 * key.
 * @return {pv.Nest} this.
 */
pv.Nest.prototype.key = function(key) {
  this.keys.push(key);
  return this;
};

/**
 * Sorts the previously-added keys. The natural sort order is used by default
 * (see {@link pv.naturalOrder}); if an alternative order is desired,
 * <tt>order</tt> should be a comparator function. If this method is not called
 * (i.e., keys are <i>unsorted</i>), keys will appear in the order they appear
 * in the underlying elements array. For example,
 *
 * <pre>pv.nest(yields)
 *     .key(function(d) d.year)
 *     .key(function(d) d.variety)
 *     .sortKeys()
 *     .entries()</pre>
 *
 * groups yield data by year, then variety, and sorts the variety groups
 * lexicographically (since the variety attribute is a string).
 *
 * <p>Key sort order is only used in conjunction with {@link #entries}, which
 * returns an array of key-values pairs. If the nest is used to construct a
 * {@link #map} instead, keys are unsorted.
 *
 * @param {function} [order] an optional comparator function.
 * @returns {pv.Nest} this.
 */
pv.Nest.prototype.sortKeys = function(order) {
  this.keys[this.keys.length - 1].order = order || pv.naturalOrder;
  return this;
};

/**
 * Sorts the leaf values. The natural sort order is used by default (see
 * {@link pv.naturalOrder}); if an alternative order is desired, <tt>order</tt>
 * should be a comparator function. If this method is not called (i.e., values
 * are <i>unsorted</i>), values will appear in the order they appear in the
 * underlying elements array. For example,
 *
 * <pre>pv.nest(yields)
 *     .key(function(d) d.year)
 *     .key(function(d) d.variety)
 *     .sortValues(function(a, b) a.yield - b.yield)
 *     .entries()</pre>
 *
 * groups yield data by year, then variety, and sorts the values for each
 * variety group by yield.
 *
 * <p>Value sort order, unlike keys, applies to both {@link #entries} and
 * {@link #map}. It has no effect on {@link #rollup}.
 *
 * @param {function} [order] an optional comparator function.
 * @return {pv.Nest} this.
 */
pv.Nest.prototype.sortValues = function(order) {
  this.order = order || pv.naturalOrder;
  return this;
};

/**
 * Returns a hierarchical map of values. Each key adds one level to the
 * hierarchy. With only a single key, the returned map will have a key for each
 * distinct value of the key function; the correspond value with be an array of
 * elements with that key value. If a second key is added, this will be a nested
 * map. For example:
 *
 * <pre>pv.nest(yields)
 *     .key(function(d) d.variety)
 *     .key(function(d) d.site)
 *     .map()</pre>
 *
 * returns a map <tt>m</tt> such that <tt>m[variety][site]</tt> is an array, a subset of
 * <tt>yields</tt>, with each element having the given variety and site.
 *
 * @returns a hierarchical map of values.
 */
pv.Nest.prototype.map = function() {
  var map = {}, values = [];

  /* Build the map. */
  for (var i, j = 0; j < this.array.length; j++) {
    var x = this.array[j];
    var m = map;
    for (i = 0; i < this.keys.length - 1; i++) {
      var k = this.keys[i](x);
      if (!m[k]) m[k] = {};
      m = m[k];
    }
    k = this.keys[i](x);
    if (!m[k]) {
      var a = [];
      values.push(a);
      m[k] = a;
    }
    m[k].push(x);
  }

  /* Sort each leaf array. */
  if (this.order) {
    for (var i = 0; i < values.length; i++) {
      values[i].sort(this.order);
    }
  }

  return map;
};

/**
 * Returns a hierarchical nested array. This method is similar to
 * {@link pv.entries}, but works recursively on the entire hierarchy. Rather
 * than returning a map like {@link #map}, this method returns a nested
 * array. Each element of the array has a <tt>key</tt> and <tt>values</tt>
 * field. For leaf nodes, the <tt>values</tt> array will be a subset of the
 * underlying elements array; for non-leaf nodes, the <tt>values</tt> array will
 * contain more key-values pairs.
 *
 * <p>For an example usage, see the {@link Nest} constructor.
 *
 * @returns a hierarchical nested array.
 */
pv.Nest.prototype.entries = function() {

  /** Recursively extracts the entries for the given map. */
  function entries(map) {
    var array = [];
    for (var k in map) {
      var v = map[k];
      array.push({ key: k, values: (v instanceof Array) ? v : entries(v) });
    };
    return array;
  }

  /** Recursively sorts the values for the given key-values array. */
  function sort(array, i) {
    var o = this.keys[i].order;
    if (o) array.sort(function(a, b) { return o(a.key, b.key); });
    if (++i < this.keys.length) {
      for (var j = 0; j < array.length; j++) {
        sort.call(this, array[j].values, i);
      }
    }
    return array;
  }

  return sort.call(this, entries(this.map()), 0);
};

/**
 * Returns a rollup map. The behavior of this method is the same as
 * {@link #map}, except that the leaf values are replaced with the return value
 * of the specified rollup function <tt>f</tt>. For example,
 *
 * <pre>pv.nest(yields)
 *      .key(function(d) d.site)
 *      .rollup(function(v) pv.median(v, function(d) d.yield))</pre>
 *
 * first groups yield data by site, and then returns a map from site to median
 * yield for the given site.
 *
 * @see #map
 * @param {function} f a rollup function.
 * @returns a hierarchical map, with the leaf values computed by <tt>f</tt>.
 */
pv.Nest.prototype.rollup = function(f) {

  /** Recursively descends to the leaf nodes (arrays) and does rollup. */
  function rollup(map) {
    for (var key in map) {
      var value = map[key];
      if (value instanceof Array) {
        map[key] = f(value);
      } else {
        rollup(value);
      }
    }
    return map;
  }

  return rollup(this.map());
};
