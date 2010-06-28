/**
 * The top-level Protovis namespace. All public methods and fields should be
 * registered on this object. Note that core Protovis source is surrounded by an
 * anonymous function, so any other declared globals will not be visible outside
 * of core methods. This also allows multiple versions of Protovis to coexist,
 * since each version will see their own <tt>pv</tt> namespace.
 *
 * @namespace The top-level Protovis namespace, <tt>pv</tt>.
 */
var pv = {};

/**
 * @private Returns a prototype object suitable for extending the given class
 * <tt>f</tt>. Rather than constructing a new instance of <tt>f</tt> to serve as
 * the prototype (which unnecessarily runs the constructor on the created
 * prototype object, potentially polluting it), an anonymous function is
 * generated internally that shares the same prototype:
 *
 * <pre>function g() {}
 * g.prototype = f.prototype;
 * return new g();</pre>
 *
 * For more details, see Douglas Crockford's essay on prototypal inheritance.
 *
 * @param {function} f a constructor.
 * @returns a suitable prototype object.
 * @see Douglas Crockford's essay on <a
 * href="http://javascript.crockford.com/prototypal.html">prototypal
 * inheritance</a>.
 */
pv.extend = function(f) {
  function g() {}
  g.prototype = f.prototype || f;
  return new g();
};

try {
  eval("pv.parse = function(x) x;"); // native support
} catch (e) {

/**
 * @private Parses a Protovis specification, which may use JavaScript 1.8
 * function expresses, replacing those function expressions with proper
 * functions such that the code can be run by a JavaScript 1.6 interpreter. This
 * hack only supports function expressions (using clumsy regular expressions, no
 * less), and not other JavaScript 1.8 features such as let expressions.
 *
 * @param {string} s a Protovis specification (i.e., a string of JavaScript 1.8
 * source code).
 * @returns {string} a conformant JavaScript 1.6 source code.
 */
  pv.parse = function(js) { // hacky regex support
    var re = new RegExp("function(\\s+\\w+)?\\([^)]*\\)\\s*", "mg"), m, d, i = 0, s = "";
    while (m = re.exec(js)) {
      var j = m.index + m[0].length;
      if (js.charAt(j--) != '{') {
        s += js.substring(i, j) + "{return ";
        i = j;
        for (var p = 0; p >= 0 && j < js.length; j++) {
          var c = js.charAt(j);
          switch (c) {
            case '"': case '\'': {
              while (++j < js.length && (d = js.charAt(j)) != c) {
                if (d == '\\') j++;
              }
              break;
            }
            case '[': case '(': p++; break;
            case ']': case ')': p--; break;
            case ';':
            case ',': if (p == 0) p--; break;
          }
        }
        s += pv.parse(js.substring(i, --j)) + ";}";
        i = j;
      }
      re.lastIndex = j;
    }
    s += js.substring(i);
    return s;
  };
}

/**
 * Returns the passed-in argument, <tt>x</tt>; the identity function. This method
 * is provided for convenience since it is used as the default behavior for a
 * number of property functions.
 *
 * @param x a value.
 * @returns the value <tt>x</tt>.
 */
pv.identity = function(x) { return x; };

/**
 * Returns <tt>this.index</tt>. This method is provided for convenience for use
 * with scales. For example, to color bars by their index, say:
 *
 * <pre>.fillStyle(pv.Colors.category10().by(pv.index))</pre>
 *
 * This method is equivalent to <tt>function() this.index</tt>, but more
 * succinct. Note that the <tt>index</tt> property is also supported for
 * accessor functions with {@link pv.max}, {@link pv.min} and other array
 * utility methods.
 *
 * @see pv.Scale
 * @see pv.Mark#index
 */
pv.index = function() { return this.index; };

/**
 * Returns <tt>this.childIndex</tt>. This method is provided for convenience for
 * use with scales. For example, to color bars by their child index, say:
 *
 * <pre>.fillStyle(pv.Colors.category10().by(pv.child))</pre>
 *
 * This method is equivalent to <tt>function() this.childIndex</tt>, but more
 * succinct.
 *
 * @see pv.Scale
 * @see pv.Mark#childIndex
 */
pv.child = function() { return this.childIndex; };

/**
 * Returns <tt>this.parent.index</tt>. This method is provided for convenience
 * for use with scales. This method is provided for convenience for use with
 * scales. For example, to color bars by their parent index, say:
 *
 * <pre>.fillStyle(pv.Colors.category10().by(pv.parent))</pre>
 *
 * Tthis method is equivalent to <tt>function() this.parent.index</tt>, but more
 * succinct.
 *
 * @see pv.Scale
 * @see pv.Mark#index
 */
pv.parent = function() { return this.parent.index; };

/**
 * Returns an array of numbers, starting at <tt>start</tt>, incrementing by
 * <tt>step</tt>, until <tt>stop</tt> is reached. The stop value is exclusive. If
 * only a single argument is specified, this value is interpeted as the
 * <i>stop</i> value, with the <i>start</i> value as zero. If only two arguments
 * are specified, the step value is implied to be one.
 *
 * <p>The method is modeled after the built-in <tt>range</tt> method from
 * Python. See the Python documentation for more details.
 *
 * @see <a href="http://docs.python.org/library/functions.html#range">Python range</a>
 * @param {number} [start] the start value.
 * @param {number} stop the stop value.
 * @param {number} [step] the step value.
 * @returns {number[]} an array of numbers.
 */
pv.range = function(start, stop, step) {
  if (arguments.length == 1) {
    stop = start;
    start = 0;
  }
  if (step == undefined) step = 1;
  else if (!step) throw new Error("step must be non-zero");
  var array = [], i = 0, j;
  if (step < 0) {
    while ((j = start + step * i++) > stop) {
      array.push(j);
    }
  } else {
    while ((j = start + step * i++) < stop) {
      array.push(j);
    }
  }
  return array;
};

/**
 * Returns a random number in the range [<tt>min</tt>, <tt>max</tt>) that is a
 * multiple of <tt>step</tt>. More specifically, the returned number is of the
 * form <tt>min</tt> + <i>n</i> * <tt>step</tt>, where <i>n</i> is a nonnegative
 * integer. If <tt>step</tt> is not specified, it defaults to 1, returning a
 * random integer if <tt>min</tt> is also an integer.
 *
 * @param min {number} minimum value.
 * @param [max] {number} maximum value.
 * @param [step] {numbeR} step value.
 */
pv.random = function(min, max, step) {
  if (arguments.length == 1) {
    max = min;
    min = 0;
  }
  if (step == undefined) {
    step = 1;
  }
  return step
      ? (Math.floor(Math.random() * (max - min) / step) * step + min)
      : (Math.random() * (max - min) + min);
};

/**
 * Concatenates the specified array with itself <i>n</i> times. For example,
 * <tt>pv.repeat([1, 2])</tt> returns [1, 2, 1, 2].
 *
 * @param {array} a an array.
 * @param {number} [n] the number of times to repeat; defaults to two.
 * @returns {array} an array that repeats the specified array.
 */
pv.repeat = function(array, n) {
  if (arguments.length == 1) n = 2;
  return pv.blend(pv.range(n).map(function() { return array; }));
};

/**
 * Given two arrays <tt>a</tt> and <tt>b</tt>, <style
 * type="text/css">sub{line-height:0}</style> returns an array of all possible
 * pairs of elements [a<sub>i</sub>, b<sub>j</sub>]. The outer loop is on array
 * <i>a</i>, while the inner loop is on <i>b</i>, such that the order of
 * returned elements is [a<sub>0</sub>, b<sub>0</sub>], [a<sub>0</sub>,
 * b<sub>1</sub>], ... [a<sub>0</sub>, b<sub>m</sub>], [a<sub>1</sub>,
 * b<sub>0</sub>], [a<sub>1</sub>, b<sub>1</sub>], ... [a<sub>1</sub>,
 * b<sub>m</sub>], ... [a<sub>n</sub>, b<sub>m</sub>]. If either array is empty,
 * an empty array is returned.
 *
 * @param {array} a an array.
 * @param {array} b an array.
 * @returns {array} an array of pairs of elements in <tt>a</tt> and <tt>b</tt>.
 */
pv.cross = function(a, b) {
  var array = [];
  for (var i = 0, n = a.length, m = b.length; i < n; i++) {
    for (var j = 0, x = a[i]; j < m; j++) {
      array.push([x, b[j]]);
    }
  }
  return array;
};

/**
 * Given the specified array of arrays, concatenates the arrays into a single
 * array. If the individual arrays are explicitly known, an alternative to blend
 * is to use JavaScript's <tt>concat</tt> method directly. These two equivalent
 * expressions:<ul>
 *
 * <li><tt>pv.blend([[1, 2, 3], ["a", "b", "c"]])</tt>
 * <li><tt>[1, 2, 3].concat(["a", "b", "c"])</tt>
 *
 * </ul>return [1, 2, 3, "a", "b", "c"].
 *
 * @param {array[]} arrays an array of arrays.
 * @returns {array} an array containing all the elements of each array in
 * <tt>arrays</tt>.
 */
pv.blend = function(arrays) {
  return Array.prototype.concat.apply([], arrays);
};

/**
 * Given the specified array of arrays, <style
 * type="text/css">sub{line-height:0}</style> transposes each element
 * array<sub>ij</sub> with array<sub>ji</sub>. If the array has dimensions
 * <i>n</i>&times;<i>m</i>, it will have dimensions <i>m</i>&times;<i>n</i>
 * after this method returns. This method transposes the elements of the array
 * in place, mutating the array, and returning a reference to the array.
 *
 * @param {array[]} arrays an array of arrays.
 * @returns {array[]} the passed-in array, after transposing the elements.
 */
pv.transpose = function(arrays) {
  var n = arrays.length, m = pv.max(arrays, function(d) { return d.length; });

  if (m > n) {
    arrays.length = m;
    for (var i = n; i < m; i++) {
      arrays[i] = new Array(n);
    }
    for (var i = 0; i < n; i++) {
      for (var j = i + 1; j < m; j++) {
        var t = arrays[i][j];
        arrays[i][j] = arrays[j][i];
        arrays[j][i] = t;
      }
    }
  } else {
    for (var i = 0; i < m; i++) {
      arrays[i].length = n;
    }
    for (var i = 0; i < n; i++) {
      for (var j = 0; j < i; j++) {
        var t = arrays[i][j];
        arrays[i][j] = arrays[j][i];
        arrays[j][i] = t;
      }
    }
  }

  arrays.length = m;
  for (var i = 0; i < m; i++) {
    arrays[i].length = n;
  }

  return arrays;
};

/**
 * Returns all of the property names (keys) of the specified object (a map). The
 * order of the returned array is not defined.
 *
 * @param map an object.
 * @returns {string[]} an array of strings corresponding to the keys.
 * @see #entries
 */
pv.keys = function(map) {
  var array = [];
  for (var key in map) {
    array.push(key);
  }
  return array;
};

/**
 * Returns all of the entries (key-value pairs) of the specified object (a
 * map). The order of the returned array is not defined. Each key-value pair is
 * represented as an object with <tt>key</tt> and <tt>value</tt> attributes,
 * e.g., <tt>{key: "foo", value: 42}</tt>.
 *
 * @param map an object.
 * @returns {array} an array of key-value pairs corresponding to the keys.
 */
pv.entries = function(map) {
  var array = [];
  for (var key in map) {
    array.push({ key: key, value: map[key] });
  }
  return array;
};

/**
 * Returns all of the values (attribute values) of the specified object (a
 * map). The order of the returned array is not defined.
 *
 * @param map an object.
 * @returns {array} an array of objects corresponding to the values.
 * @see #entries
 */
pv.values = function(map) {
  var array = [];
  for (var key in map) {
    array.push(map[key]);
  }
  return array;
};

/**
 * @private A private variant of Array.prototype.map that supports the index
 * property.
 */
function map(array, f) {
  var o = {};
  return f
      ? array.map(function(d, i) { o.index = i; return f.call(o, d); })
      : array.slice();
};

/**
 * Returns a normalized copy of the specified array, such that the sum of the
 * returned elements sum to one. If the specified array is not an array of
 * numbers, an optional accessor function <tt>f</tt> can be specified to map the
 * elements to numbers. For example, if <tt>array</tt> is an array of objects,
 * and each object has a numeric property "foo", the expression
 *
 * <pre>pv.normalize(array, function(d) d.foo)</pre>
 *
 * returns a normalized array on the "foo" property. If an accessor function is
 * not specified, the identity function is used. Accessor functions can refer to
 * <tt>this.index</tt>.
 *
 * @param {array} array an array of objects, or numbers.
 * @param {function} [f] an optional accessor function.
 * @returns {number[]} an array of numbers that sums to one.
 */
pv.normalize = function(array, f) {
  var norm = map(array, f), sum = pv.sum(norm);
  for (var i = 0; i < norm.length; i++) norm[i] /= sum;
  return norm;
};

/**
 * Returns the sum of the specified array. If the specified array is not an
 * array of numbers, an optional accessor function <tt>f</tt> can be specified
 * to map the elements to numbers. See {@link #normalize} for an example.
 * Accessor functions can refer to <tt>this.index</tt>.
 *
 * @param {array} array an array of objects, or numbers.
 * @param {function} [f] an optional accessor function.
 * @returns {number} the sum of the specified array.
 */
pv.sum = function(array, f) {
  var o = {};
  return array.reduce(f
      ? function(p, d, i) { o.index = i; return p + f.call(o, d); }
      : function(p, d) { return p + d; }, 0);
};

/**
 * Returns the maximum value of the specified array. If the specified array is
 * not an array of numbers, an optional accessor function <tt>f</tt> can be
 * specified to map the elements to numbers. See {@link #normalize} for an
 * example. Accessor functions can refer to <tt>this.index</tt>.
 *
 * @param {array} array an array of objects, or numbers.
 * @param {function} [f] an optional accessor function.
 * @returns {number} the maximum value of the specified array.
 */
pv.max = function(array, f) {
  if (f == pv.index) return array.length - 1;
  return Math.max.apply(null, f ? map(array, f) : array);
};

/**
 * Returns the index of the maximum value of the specified array. If the
 * specified array is not an array of numbers, an optional accessor function
 * <tt>f</tt> can be specified to map the elements to numbers. See
 * {@link #normalize} for an example. Accessor functions can refer to
 * <tt>this.index</tt>.
 *
 * @param {array} array an array of objects, or numbers.
 * @param {function} [f] an optional accessor function.
 * @returns {number} the index of the maximum value of the specified array.
 */
pv.max.index = function(array, f) {
  if (f == pv.index) return array.length - 1;
  if (!f) f = pv.identity;
  var maxi = -1, maxx = -Infinity, o = {};
  for (var i = 0; i < array.length; i++) {
    o.index = i;
    var x = f.call(o, array[i]);
    if (x > maxx) {
      maxx = x;
      maxi = i;
    }
  }
  return maxi;
}

/**
 * Returns the minimum value of the specified array of numbers. If the specified
 * array is not an array of numbers, an optional accessor function <tt>f</tt>
 * can be specified to map the elements to numbers. See {@link #normalize} for
 * an example. Accessor functions can refer to <tt>this.index</tt>.
 *
 * @param {array} array an array of objects, or numbers.
 * @param {function} [f] an optional accessor function.
 * @returns {number} the minimum value of the specified array.
 */
pv.min = function(array, f) {
  if (f == pv.index) return 0;
  return Math.min.apply(null, f ? map(array, f) : array);
};

/**
 * Returns the index of the minimum value of the specified array. If the
 * specified array is not an array of numbers, an optional accessor function
 * <tt>f</tt> can be specified to map the elements to numbers. See
 * {@link #normalize} for an example. Accessor functions can refer to
 * <tt>this.index</tt>.
 *
 * @param {array} array an array of objects, or numbers.
 * @param {function} [f] an optional accessor function.
 * @returns {number} the index of the minimum value of the specified array.
 */
pv.min.index = function(array, f) {
  if (f == pv.index) return 0;
  if (!f) f = pv.identity;
  var mini = -1, minx = Infinity, o = {};
  for (var i = 0; i < array.length; i++) {
    o.index = i;
    var x = f.call(o, array[i]);
    if (x < minx) {
      minx = x;
      mini = i;
    }
  }
  return mini;
}

/**
 * Returns the arithmetic mean, or average, of the specified array. If the
 * specified array is not an array of numbers, an optional accessor function
 * <tt>f</tt> can be specified to map the elements to numbers. See
 * {@link #normalize} for an example. Accessor functions can refer to
 * <tt>this.index</tt>.
 *
 * @param {array} array an array of objects, or numbers.
 * @param {function} [f] an optional accessor function.
 * @returns {number} the mean of the specified array.
 */
pv.mean = function(array, f) {
  return pv.sum(array, f) / array.length;
};

/**
 * Returns the median of the specified array. If the specified array is not an
 * array of numbers, an optional accessor function <tt>f</tt> can be specified
 * to map the elements to numbers. See {@link #normalize} for an example.
 * Accessor functions can refer to <tt>this.index</tt>.
 *
 * @param {array} array an array of objects, or numbers.
 * @param {function} [f] an optional accessor function.
 * @returns {number} the median of the specified array.
 */
pv.median = function(array, f) {
  if (f == pv.index) return (array.length - 1) / 2;
  array = map(array, f).sort(pv.naturalOrder);
  if (array.length % 2) return array[Math.floor(array.length / 2)];
  var i = array.length / 2;
  return (array[i - 1] + array[i]) / 2;
};

/**
 * Returns a map constructed from the specified <tt>keys</tt>, using the
 * function <tt>f</tt> to compute the value for each key. The single argument to
 * the value function is the key. The callback is invoked only for indexes of
 * the array which have assigned values; it is not invoked for indexes which
 * have been deleted or which have never been assigned values.
 *
 * <p>For example, this expression creates a map from strings to string length:
 *
 * <pre>pv.dict(["one", "three", "seventeen"], function(s) s.length)</pre>
 *
 * The returned value is <tt>{one: 3, three: 5, seventeen: 9}</tt>. Accessor
 * functions can refer to <tt>this.index</tt>.
 *
 * @param {array} keys an array.
 * @param {function} f a value function.
 * @returns a map from keys to values.
 */
pv.dict = function(keys, f) {
  var m = {}, o = {};
  for (var i = 0; i < keys.length; i++) {
    if (i in keys) {
      var k = keys[i];
      o.index = i;
      m[k] = f.call(o, k);
    }
  }
  return m;
};

/**
 * Returns a permutation of the specified array, using the specified array of
 * indexes. The returned array contains the corresponding element in
 * <tt>array</tt> for each index in <tt>indexes</tt>, in order. For example,
 *
 * <pre>pv.permute(["a", "b", "c"], [1, 2, 0])</pre>
 *
 * returns <tt>["b", "c", "a"]</tt>. It is acceptable for the array of indexes
 * to be a different length from the array of elements, and for indexes to be
 * duplicated or omitted. The optional accessor function <tt>f</tt> can be used
 * to perform a simultaneous mapping of the array elements. Accessor functions
 * can refer to <tt>this.index</tt>.
 *
 * @param {array} array an array.
 * @param {number[]} indexes an array of indexes into <tt>array</tt>.
 * @param {function} [f] an optional accessor function.
 * @returns {array} an array of elements from <tt>array</tt>; a permutation.
 */
pv.permute = function(array, indexes, f) {
  if (!f) f = pv.identity;
  var p = new Array(indexes.length), o = {};
  indexes.forEach(function(j, i) { o.index = j; p[i] = f.call(o, array[j]); });
  return p;
};

/**
 * Returns a map from key to index for the specified <tt>keys</tt> array. For
 * example,
 *
 * <pre>pv.numerate(["a", "b", "c"])</pre>
 *
 * returns <tt>{a: 0, b: 1, c: 2}</tt>. Note that since JavaScript maps only
 * support string keys, <tt>keys</tt> must contain strings, or other values that
 * naturally map to distinct string values. Alternatively, an optional accessor
 * function <tt>f</tt> can be specified to compute the string key for the given
 * element. Accessor functions can refer to <tt>this.index</tt>.
 *
 * @param {array} keys an array, usually of string keys.
 * @param {function} [f] an optional key function.
 * @returns a map from key to index.
 */
pv.numerate = function(keys, f) {
  if (!f) f = pv.identity;
  var map = {}, o = {};
  keys.forEach(function(x, i) { o.index = i; map[f.call(o, x)] = i; });
  return map;
};

/**
 * The comparator function for natural order. This can be used in conjunction with
 * the built-in array <tt>sort</tt> method to sort elements by their natural
 * order, ascending. Note that if no comparator function is specified to the
 * built-in <tt>sort</tt> method, the default order is lexicographic, <i>not</i>
 * natural!
 *
 * @see <a
 * href="http://developer.mozilla.org/en/Core_JavaScript_1.5_Reference/Global_Objects/Array/sort">Array.sort</a>.
 * @param a an element to compare.
 * @param b an element to compare.
 * @returns {number} negative if a &lt; b; positive if a &gt; b; otherwise 0.
 */
pv.naturalOrder = function(a, b) {
  return (a < b) ? -1 : ((a > b) ? 1 : 0);
};

/**
 * The comparator function for reverse natural order. This can be used in
 * conjunction with the built-in array <tt>sort</tt> method to sort elements by
 * their natural order, descending. Note that if no comparator function is
 * specified to the built-in <tt>sort</tt> method, the default order is
 * lexicographic, <i>not</i> natural!
 *
 * @see #naturalOrder
 * @param a an element to compare.
 * @param b an element to compare.
 * @returns {number} negative if a &lt; b; positive if a &gt; b; otherwise 0.
 */
pv.reverseOrder = function(b, a) {
  return (a < b) ? -1 : ((a > b) ? 1 : 0);
};

/**
 * @private Computes the value of the specified CSS property <tt>p</tt> on the
 * specified element <tt>e</tt>.
 *
 * @param {string} p the name of the CSS property.
 * @param e the element on which to compute the CSS property.
 */
pv.css = function(e, p) {
  return window.getComputedStyle
      ? window.getComputedStyle(e, null).getPropertyValue(p)
      : e.currentStyle[p];
};

/**
 * Namespace constants for SVG, XMLNS, and XLINK.
 *
 * @namespace Namespace constants for SVG, XMLNS, and XLINK.
 */
pv.ns = {
  /**
   * The SVG namespace, "http://www.w3.org/2000/svg".
   *
   * @type string
   * @constant
   */
  svg: "http://www.w3.org/2000/svg",

  /**
   * The XMLNS namespace, "http://www.w3.org/2000/xmlns".
   *
   * @type string
   * @constant
   */
  xmlns: "http://www.w3.org/2000/xmlns",

  /**
   * The XLINK namespace, "http://www.w3.org/1999/xlink".
   *
   * @type string
   * @constant
   */
  xlink: "http://www.w3.org/1999/xlink"
};

/**
 * Protovis major and minor version numbers.
 *
 * @namespace Protovis major and minor version numbers.
 */
pv.version = {
  /**
   * The major version number.
   *
   * @type number
   * @constant
   */
  major: 3,

  /**
   * The minor version number.
   *
   * @type number
   * @constant
   */
  minor: 1
};

/**
 * @private Reports the specified error to the JavaScript console. Mozilla only
 * allows logging to the console for privileged code; if the console is
 * unavailable, the alert dialog box is used instead.
 *
 * @param e the exception that triggered the error.
 */
pv.error = function(e) {
  (typeof console == "undefined") ? alert(e) : console.error(e);
};

/**
 * @private Registers the specified listener for events of the specified type on
 * the specified target. For standards-compliant browsers, this method uses
 * <tt>addEventListener</tt>; for Internet Explorer, <tt>attachEvent</tt>.
 *
 * @param target a DOM element.
 * @param {string} type the type of event, such as "click".
 * @param {function} the listener callback function.
 */
pv.listen = function(target, type, listener) {
  return target.addEventListener
    ? target.addEventListener(type, listener, false)
    : target.attachEvent("on" + type, listener);
};

/**
 * Returns the logarithm with a given base value.
 *
 * @param {number} x the number for which to compute the logarithm.
 * @param {number} b the base of the logarithm.
 * @returns {number} the logarithm value.
 */
pv.log = function(x, b) {
  return Math.log(x) / Math.log(b);
};

/**
 * Computes a zero-symmetric logarithm. Computes the logarithm of the absolute
 * value of the input, and determines the sign of the output according to the
 * sign of the input value.
 *
 * @param {number} x the number for which to compute the logarithm.
 * @param {number} b the base of the logarithm.
 * @returns {number} the symmetric log value.
 */
pv.logSymmetric = function(x, b) {
  return (x == 0) ? 0 : ((x < 0) ? -pv.log(-x, b) : pv.log(x, b));
};

/**
 * Computes a zero-symmetric logarithm, with adjustment to values between zero
 * and the logarithm base. This adjustment introduces distortion for values less
 * than the base number, but enables simultaneous plotting of log-transformed
 * data involving both positive and negative numbers.
 *
 * @param {number} x the number for which to compute the logarithm.
 * @param {number} b the base of the logarithm.
 * @returns {number} the adjusted, symmetric log value.
 */
pv.logAdjusted = function(x, b) {
  var negative = x < 0;
  if (x < b) x += (b - x) / b;
  return negative ? -pv.log(x, b) : pv.log(x, b);
};

/**
 * Rounds an input value down according to its logarithm. The method takes the
 * floor of the logarithm of the value and then uses the resulting value as an
 * exponent for the base value.
 *
 * @param {number} x the number for which to compute the logarithm floor.
 * @param {number} b the base of the logarithm.
 * @return {number} the rounded-by-logarithm value.
 */
pv.logFloor = function(x, b) {
  return (x > 0)
      ? Math.pow(b, Math.floor(pv.log(x, b)))
      : -Math.pow(b, -Math.floor(-pv.log(-x, b)));
};

/**
 * Rounds an input value up according to its logarithm. The method takes the
 * ceiling of the logarithm of the value and then uses the resulting value as an
 * exponent for the base value.
 *
 * @param {number} x the number for which to compute the logarithm ceiling.
 * @param {number} b the base of the logarithm.
 * @return {number} the rounded-by-logarithm value.
 */
pv.logCeil = function(x, b) {
  return (x > 0)
      ? Math.pow(b, Math.ceil(pv.log(x, b)))
      : -Math.pow(b, -Math.ceil(-pv.log(-x, b)));
};

/**
 * Searches the specified array of numbers for the specified value using the
 * binary search algorithm. The array must be sorted (as by the <tt>sort</tt>
 * method) prior to making this call. If it is not sorted, the results are
 * undefined. If the array contains multiple elements with the specified value,
 * there is no guarantee which one will be found.
 *
 * <p>The <i>insertion point</i> is defined as the point at which the value
 * would be inserted into the array: the index of the first element greater than
 * the value, or <tt>array.length</tt>, if all elements in the array are less
 * than the specified value. Note that this guarantees that the return value
 * will be nonnegative if and only if the value is found.
 *
 * @param {number[]} array the array to be searched.
 * @param {number} value the value to be searched for.
 * @returns the index of the search value, if it is contained in the array;
 * otherwise, (-(<i>insertion point</i>) - 1).
 * @param {function} [f] an optional key function.
 */
pv.search = function(array, value, f) {
  if (!f) f = pv.identity;
  var low = 0, high = array.length - 1;
  while (low <= high) {
    var mid = (low + high) >> 1, midValue = f(array[mid]);
    if (midValue < value) low = mid + 1;
    else if (midValue > value) high = mid - 1;
    else return mid;
  }
  return -low - 1;
};

pv.search.index = function(array, value, f) {
  var i = pv.search(array, value, f);
  return (i < 0) ? (-i - 1) : i;
};
