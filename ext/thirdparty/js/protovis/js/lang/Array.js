/**
 * @class The built-in Array class.
 * @name Array
 */

if (!Array.prototype.map) {
  /**
   * Creates a new array with the results of calling a provided function on
   * every element in this array. Implemented in Javascript 1.6.
   *
   * @see <a
   * href="https://developer.mozilla.org/En/Core_JavaScript_1.5_Reference/Objects/Array/Map">map</a>
   * documentation.
   * @param {function} f function that produces an element of the new Array from
   * an element of the current one.
   * @param [o] object to use as <tt>this</tt> when executing <tt>f</tt>.
   */
  Array.prototype.map = function(f, o) {
      var n = this.length;
      var result = new Array(n);
      for (var i = 0; i < n; i++) {
        if (i in this) {
          result[i] = f.call(o, this[i], i, this);
        }
      }
      return result;
    };
}

if (!Array.prototype.filter) {
  /**
   * Creates a new array with all elements that pass the test implemented by the
   * provided function. Implemented in Javascript 1.6.
   *
   * @see <a
   * href="https://developer.mozilla.org/En/Core_JavaScript_1.5_Reference/Objects/Array/filter">filter</a>
   * documentation.
   * @param {function} f function to test each element of the array.
   * @param [o] object to use as <tt>this</tt> when executing <tt>f</tt>.
   */
  Array.prototype.filter = function(f, o) {
      var n = this.length;
      var result = new Array();
      for (var i = 0; i < n; i++) {
        if (i in this) {
          var v = this[i];
          if (f.call(o, v, i, this)) result.push(v);
        }
      }
      return result;
    };
}

if (!Array.prototype.forEach) {
  /**
   * Executes a provided function once per array element. Implemented in
   * Javascript 1.6.
   *
   * @see <a
   * href="https://developer.mozilla.org/En/Core_JavaScript_1.5_Reference/Objects/Array/ForEach">forEach</a>
   * documentation.
   * @param {function} f function to execute for each element.
   * @param [o] object to use as <tt>this</tt> when executing <tt>f</tt>.
   */
  Array.prototype.forEach = function(f, o) {
      var n = this.length >>> 0;
      for (var i = 0; i < n; i++) {
        if (i in this) f.call(o, this[i], i, this);
      }
    };
}

if (!Array.prototype.reduce) {
  /**
   * Apply a function against an accumulator and each value of the array (from
   * left-to-right) as to reduce it to a single value. Implemented in Javascript
   * 1.8.
   *
   * @see <a
   * href="https://developer.mozilla.org/En/Core_JavaScript_1.5_Reference/Objects/Array/Reduce">reduce</a>
   * documentation.
   * @param {function} f function to execute on each value in the array.
   * @param [v] object to use as the first argument to the first call of
   * <tt>t</tt>.
   */
  Array.prototype.reduce = function(f, v) {
      var len = this.length;
      if (!len && (arguments.length == 1)) {
        throw new Error("reduce: empty array, no initial value");
      }

      var i = 0;
      if (arguments.length < 2) {
        while (true) {
          if (i in this) {
            v = this[i++];
            break;
          }
          if (++i >= len) {
            throw new Error("reduce: no values, no initial value");
          }
        }
      }

      for (; i < len; i++) {
        if (i in this) {
          v = f(v, this[i], i, this);
        }
      }
      return v;
    };
}
