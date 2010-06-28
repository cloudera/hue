// TODO code-sharing between scales

/**
 * @ignore
 * @class
 */
pv.Scale = function() {};

/**
 * @private Returns a function that interpolators from the start value to the
 * end value, given a parameter <i>t</i> in [0, 1].
 *
 * @param start the start value.
 * @param end the end value.
 */
pv.Scale.interpolator = function(start, end) {
  if (typeof start == "number") {
    return function(t) {
      return t * (end - start) + start;
    };
  }

  /* For now, assume color. */
  start = pv.color(start).rgb();
  end = pv.color(end).rgb();
  return function(t) {
    var a = start.a * (1 - t) + end.a * t;
    if (a < 1e-5) a = 0; // avoid scientific notation
    return (start.a == 0) ? pv.rgb(end.r, end.g, end.b, a)
        : ((end.a == 0) ? pv.rgb(start.r, start.g, start.b, a)
        : pv.rgb(
            Math.round(start.r * (1 - t) + end.r * t),
            Math.round(start.g * (1 - t) + end.g * t),
            Math.round(start.b * (1 - t) + end.b * t), a));
  };
};
