/**
 * Returns a log scale for the specified domain. The arguments to this
 * constructor are optional, and equivalent to calling {@link #domain}.
 *
 * @class Represents a log scale. <style
 * type="text/css">sub{line-height:0}</style> <img src="../log.png"
 * width="190" height="175" align="right"> Most commonly, a log scale represents
 * a 1-dimensional log transformation from a numeric domain of input data
 * [<i>d<sub>0</sub></i>, <i>d<sub>1</sub></i>] to a numeric range of pixels
 * [<i>r<sub>0</sub></i>, <i>r<sub>1</sub></i>]. The equation for such a scale
 * is:
 *
 * <blockquote><i>f(x) = (log(x) - log(d<sub>0</sub>)) / (log(d<sub>1</sub>) -
 * log(d<sub>0</sub>)) * (r<sub>1</sub> - r<sub>0</sub>) +
 * r<sub>0</sub></i></blockquote>
 *
 * where <i>log(x)</i> represents the zero-symmetric logarthim of <i>x</i> using
 * the scale's associated base (default: 10, see {@link pv.logSymmetric}). For
 * example, a log scale from the domain [1, 100] to range [0, 640]:
 *
 * <blockquote><i>f(x) = (log(x) - log(1)) / (log(100) - log(1)) * (640 - 0) + 0</i><br>
 * <i>f(x) = log(x) / 2 * 640</i><br>
 * <i>f(x) = log(x) * 320</i><br>
 * </blockquote>
 *
 * Thus, saying
 *
 * <pre>.height(function(d) Math.log(d) * 138.974)</pre>
 *
 * is equivalent to
 *
 * <pre>.height(pv.Scale.log(1, 100).range(0, 640))</pre>
 *
 * As you can see, scales do not always make code smaller, but they should make
 * code more explicit and easier to maintain. In addition to readability, scales
 * offer several useful features:
 *
 * <p>1. The range can be expressed in colors, rather than pixels. Changing the
 * example above to
 *
 * <pre>.fillStyle(pv.Scale.log(1, 100).range("red", "green"))</pre>
 *
 * will cause it to fill the marks "red" on an input value of 1, "green" on an
 * input value of 100, and some color in-between for intermediate values.
 *
 * <p>2. The domain and range can be subdivided for a "poly-log"
 * transformation. For example, you may want a diverging color scale that is
 * increasingly red for small values, and increasingly green for large values:
 *
 * <pre>.fillStyle(pv.Scale.log(1, 10, 100).range("red", "white", "green"))</pre>
 *
 * The domain can be specified as a series of <i>n</i> monotonically-increasing
 * values; the range must also be specified as <i>n</i> values, resulting in
 * <i>n - 1</i> contiguous log scales.
 *
 * <p>3. Log scales can be inverted for interaction. The {@link #invert} method
 * takes a value in the output range, and returns the corresponding value in the
 * input domain. This is frequently used to convert the mouse location (see
 * {@link pv.Mark#mouse}) to a value in the input domain. Note that inversion is
 * only supported for numeric ranges, and not colors.
 *
 * <p>4. A scale can be queried for reasonable "tick" values. The {@link #ticks}
 * method provides a convenient way to get a series of evenly-spaced rounded
 * values in the input domain. Frequently these are used in conjunction with
 * {@link pv.Rule} to display tick marks or grid lines.
 *
 * <p>5. A scale can be "niced" to extend the domain to suitable rounded
 * numbers. If the minimum and maximum of the domain are messy because they are
 * derived from data, you can use {@link #nice} to round these values down and
 * up to even numbers.
 *
 * @param {number...} domain... domain values.
 * @returns {pv.Scale.log} a log scale.
 */
pv.Scale.log = function() {
  var d = [1, 10], l = [0, 1], b = 10, r = [0, 1], i = [pv.identity];

  /** @private */
  function scale(x) {
    var j = pv.search(d, x);
    if (j < 0) j = -j - 2;
    j = Math.max(0, Math.min(i.length - 1, j));
    return i[j]((log(x) - l[j]) / (l[j + 1] - l[j]));
  }

  /** @private */
  function log(x) {
    return pv.logSymmetric(x, b);
  }

  /**
   * Sets or gets the input domain. This method can be invoked several ways:
   *
   * <p>1. <tt>domain(min, ..., max)</tt>
   *
   * <p>Specifying the domain as a series of numbers is the most explicit and
   * recommended approach. Most commonly, two numbers are specified: the minimum
   * and maximum value. However, for a diverging scale, or other subdivided
   * poly-log scales, multiple values can be specified. Values can be derived
   * from data using {@link pv.min} and {@link pv.max}. For example:
   *
   * <pre>.domain(1, pv.max(array))</pre>
   *
   * An alternative method for deriving minimum and maximum values from data
   * follows.
   *
   * <p>2. <tt>domain(array, minf, maxf)</tt>
   *
   * <p>When both the minimum and maximum value are derived from data, the
   * arguments to the <tt>domain</tt> method can be specified as the array of
   * data, followed by zero, one or two accessor functions. For example, if the
   * array of data is just an array of numbers:
   *
   * <pre>.domain(array)</pre>
   *
   * On the other hand, if the array elements are objects representing stock
   * values per day, and the domain should consider the stock's daily low and
   * daily high:
   *
   * <pre>.domain(array, function(d) d.low, function(d) d.high)</pre>
   *
   * The first method of setting the domain is preferred because it is more
   * explicit; setting the domain using this second method should be used only
   * if brevity is required.
   *
   * <p>3. <tt>domain()</tt>
   *
   * <p>Invoking the <tt>domain</tt> method with no arguments returns the
   * current domain as an array of numbers.
   *
   * @function
   * @name pv.Scale.log.prototype.domain
   * @param {number...} domain... domain values.
   * @returns {pv.Scale.log} <tt>this</tt>, or the current domain.
   */
  scale.domain = function(array, min, max) {
    if (arguments.length) {
      if (array instanceof Array) {
        if (arguments.length < 2) min = pv.identity;
        if (arguments.length < 3) max = min;
        d = [pv.min(array, min), pv.max(array, max)];
      } else {
        d = Array.prototype.slice.call(arguments);
      }
      l = d.map(log);
      return this;
    }
    return d;
  };

  /**
   * @function
   * @name pv.Scale.log.prototype.range
   * @param {...} range... range values.
   * @returns {pv.Scale.log} <tt>this</tt>.
   */
  scale.range = function() {
    if (arguments.length) {
      r = Array.prototype.slice.call(arguments);
      i = [];
      for (var j = 0; j < r.length - 1; j++) {
        i.push(pv.Scale.interpolator(r[j], r[j + 1]));
      }
      return this;
    }
    return r;
  };

  /**
   * Sets or gets the output range. This method can be invoked several ways:
   *
   * <p>1. <tt>range(min, ..., max)</tt>
   *
   * <p>The range may be specified as a series of numbers or colors. Most
   * commonly, two numbers are specified: the minimum and maximum pixel values.
   * For a color scale, values may be specified as {@link pv.Color}s or
   * equivalent strings. For a diverging scale, or other subdivided poly-log
   * scales, multiple values can be specified. For example:
   *
   * <pre>.range("red", "white", "green")</pre>
   *
   * <p>Currently, only numbers and colors are supported as range values. The
   * number of range values must exactly match the number of domain values, or
   * the behavior of the scale is undefined.
   *
   * <p>2. <tt>range()</tt>
   *
   * <p>Invoking the <tt>range</tt> method with no arguments returns the current
   * range as an array of numbers or colors.
   *
   * @function
   * @name pv.Scale.log.prototype.invert
   * @param {...} range... range values.
   * @returns {pv.Scale.log} <tt>this</tt>, or the current range.
   */
  scale.invert = function(y) {
    var j = pv.search(r, y);
    if (j < 0) j = -j - 2;
    j = Math.max(0, Math.min(i.length - 1, j));
    var t = l[j] + (y - r[j]) / (r[j + 1] - r[j]) * (l[j + 1] - l[j]);
    return (d[j] < 0) ? -Math.pow(b, -t) : Math.pow(b, t);
  };

  /**
   * Returns an array of evenly-spaced, suitably-rounded values in the input
   * domain. These values are frequently used in conjunction with {@link
   * pv.Rule} to display tick marks or grid lines.
   *
   * @function
   * @name pv.Scale.log.prototype.ticks
   * @returns {number[]} an array input domain values to use as ticks.
   */
  scale.ticks = function() {
    // TODO: support multiple domains
    var start = Math.floor(l[0]),
        end = Math.ceil(l[1]),
        ticks = [];
    for (var i = start; i < end; i++) {
      var x = Math.pow(b, i);
      if (d[0] < 0) x = -x;
      for (var j = 1; j < b; j++) {
        ticks.push(x * j);
      }
    }
    ticks.push(Math.pow(b, end));
    if (ticks[0] < d[0]) ticks.shift();
    if (ticks[ticks.length - 1] > d[1]) ticks.pop();
    return ticks;
  };

  /**
   * Formats the specified tick value using the appropriate precision, assuming
   * base 10.
   *
   * @function
   * @name pv.Scale.log.prototype.tickFormat
   * @param {number} t a tick value.
   * @return {string} a formatted tick value.
   */
  scale.tickFormat = function(t) {
    return t.toPrecision(1);
  };

  /**
   * "Nices" this scale, extending the bounds of the input domain to
   * evenly-rounded values. This method uses {@link pv.logFloor} and {@link
   * pv.logCeil}. Nicing is useful if the domain is computed dynamically from
   * data, and may be irregular. For example, given a domain of
   * [0.20147987687960267, 0.996679553296417], a call to <tt>nice()</tt> might
   * extend the domain to [0.1, 1].
   *
   * <p>This method must be invoked each time after setting the domain (and
   * base).
   *
   * @function
   * @name pv.Scale.log.prototype.nice
   * @returns {pv.Scale.log} <tt>this</tt>.
   */
  scale.nice = function() {
    // TODO: support multiple domains
    d = [pv.logFloor(d[0], b), pv.logCeil(d[1], b)];
    l = d.map(log);
    return this;
  };

  /**
   * Sets or gets the logarithm base. Defaults to 10.
   *
   * @function
   * @name pv.Scale.log.prototype.base
   * @param {number} [v] the new base.
   * @returns {pv.Scale.log} <tt>this</tt>, or the current base.
   */
  scale.base = function(v) {
    if (arguments.length) {
      b = v;
      l = d.map(log);
      return this;
    }
    return b;
  };

  /**
   * Returns a view of this scale by the specified accessor function <tt>f</tt>.
   * Given a scale <tt>y</tt>, <tt>y.by(function(d) d.foo)</tt> is equivalent to
   * <tt>function(d) y(d.foo)</tt>.
   *
   * <p>This method is provided for convenience, such that scales can be
   * succinctly defined inline. For example, given an array of data elements
   * that have a <tt>score</tt> attribute with the domain [0, 1], the height
   * property could be specified as:
   *
   * <pre>.height(pv.Scale.log().range(0, 480).by(function(d) d.score))</pre>
   *
   * This is equivalent to:
   *
   * <pre>.height(function(d) d.score * 480)</pre>
   *
   * This method should be used judiciously; it is typically more clear to
   * invoke the scale directly, passing in the value to be scaled.
   *
   * @function
   * @name pv.Scale.log.prototype.by
   * @param {function} f an accessor function.
   * @returns {pv.Scale.log} a view of this scale by the specified accessor
   * function.
   */
  scale.by = function(f) {
    function by() { return scale(f.apply(this, arguments)); }
    for (var method in scale) by[method] = scale[method];
    return by;
  };

  scale.domain.apply(scale, arguments);
  return scale;
};
