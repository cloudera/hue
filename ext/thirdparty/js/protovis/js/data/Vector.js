/**
 * Returns a {@link pv.Vector} for the specified <i>x</i> and <i>y</i>
 * coordinate. This is a convenience factory method, equivalent to <tt>new
 * pv.Vector(x, y)</tt>.
 *
 * @see pv.Vector
 * @param {number} x the <i>x</i> coordinate.
 * @param {number} y the <i>y</i> coordinate.
 * @returns {pv.Vector} a vector for the specified coordinates.
 */
pv.vector = function(x, y) {
  return new pv.Vector(x, y);
};

/**
 * Constructs a {@link pv.Vector} for the specified <i>x</i> and <i>y</i>
 * coordinate. This constructor should not be invoked directly; use
 * {@link pv.vector} instead.
 *
 * @class Represents a two-dimensional vector; a 2-tuple <i>&#x27e8;x,
 * y&#x27e9;</i>.
 *
 * @param {number} x the <i>x</i> coordinate.
 * @param {number} y the <i>y</i> coordinate.
 */
pv.Vector = function(x, y) {
  this.x = x;
  this.y = y;
};

/**
 * Returns a vector perpendicular to this vector: <i>&#x27e8;-y, x&#x27e9;</i>.
 *
 * @returns {pv.Vector} a perpendicular vector.
 */
pv.Vector.prototype.perp = function() {
  return new pv.Vector(-this.y, this.x);
};

/**
 * Returns a normalized copy of this vector: a vector with the same direction,
 * but unit length. If this vector has zero length this method returns a copy of
 * this vector.
 *
 * @returns {pv.Vector} a unit vector.
 */
pv.Vector.prototype.norm = function() {
  var l = this.length();
  return this.times(l ? (1 / l) : 1);
};

/**
 * Returns the magnitude of this vector, defined as <i>sqrt(x * x + y * y)</i>.
 *
 * @returns {number} a length.
 */
pv.Vector.prototype.length = function() {
  return Math.sqrt(this.x * this.x + this.y * this.y);
};

/**
 * Returns a scaled copy of this vector: <i>&#x27e8;x * k, y * k&#x27e9;</i>.
 * To perform the equivalent divide operation, use <i>1 / k</i>.
 *
 * @param {number} k the scale factor.
 * @returns {pv.Vector} a scaled vector.
 */
pv.Vector.prototype.times = function(k) {
  return new pv.Vector(this.x * k, this.y * k);
};

/**
 * Returns this vector plus the vector <i>v</i>: <i>&#x27e8;x + v.x, y +
 * v.y&#x27e9;</i>. If only one argument is specified, it is interpreted as the
 * vector <i>v</i>.
 *
 * @param {number} x the <i>x</i> coordinate to add.
 * @param {number} y the <i>y</i> coordinate to add.
 * @returns {pv.Vector} a new vector.
 */
pv.Vector.prototype.plus = function(x, y) {
  return (arguments.length == 1)
      ? new pv.Vector(this.x + x.x, this.y + x.y)
      : new pv.Vector(this.x + x, this.y + y);
};

/**
 * Returns this vector minus the vector <i>v</i>: <i>&#x27e8;x - v.x, y -
 * v.y&#x27e9;</i>. If only one argument is specified, it is interpreted as the
 * vector <i>v</i>.
 *
 * @param {number} x the <i>x</i> coordinate to subtract.
 * @param {number} y the <i>y</i> coordinate to subtract.
 * @returns {pv.Vector} a new vector.
 */
pv.Vector.prototype.minus = function(x, y) {
  return (arguments.length == 1)
      ? new pv.Vector(this.x - x.x, this.y - x.y)
      : new pv.Vector(this.x - x, this.y - y);
};

/**
 * Returns the dot product of this vector and the vector <i>v</i>: <i>x * v.x +
 * y * v.y</i>. If only one argument is specified, it is interpreted as the
 * vector <i>v</i>.
 *
 * @param {number} x the <i>x</i> coordinate to dot.
 * @param {number} y the <i>y</i> coordinate to dot.
 * @returns {number} a dot product.
 */
pv.Vector.prototype.dot = function(x, y) {
  return (arguments.length == 1)
      ? this.x * x.x + this.y * x.y
      : this.x * x + this.y * y;
};
