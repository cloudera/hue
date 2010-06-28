/**
 * Returns the {@link pv.Color} for the specified color format string. Colors
 * may have an associated opacity, or alpha channel. Color formats are specified
 * by CSS Color Modular Level 3, using either in RGB or HSL color space. For
 * example:<ul>
 *
 * <li>#f00 // #rgb
 * <li>#ff0000 // #rrggbb
 * <li>rgb(255, 0, 0)
 * <li>rgb(100%, 0%, 0%)
 * <li>hsl(0, 100%, 50%)
 * <li>rgba(0, 0, 255, 0.5)
 * <li>hsla(120, 100%, 50%, 1)
 *
 * </ul>The SVG 1.0 color keywords names are also supported, such as "aliceblue"
 * and "yellowgreen". The "transparent" keyword is supported for a
 * fully-transparent color.
 *
 * <p>If the <tt>format</tt> argument is already an instance of <tt>Color</tt>,
 * the argument is returned with no further processing.
 *
 * @param {string} format the color specification string, such as "#f00".
 * @returns {pv.Color} the corresponding <tt>Color</tt>.
 * @see <a href="http://www.w3.org/TR/SVG/types.html#ColorKeywords">SVG color
 * keywords</a>
 * @see <a href="http://www.w3.org/TR/css3-color/">CSS3 color module</a>
 */
pv.color = function(format) {
  if (!format || (format == "transparent")) {
    return pv.rgb(0, 0, 0, 0);
  }
  if (format instanceof pv.Color) {
    return format;
  }

  /* Handle hsl, rgb. */
  var m1 = /([a-z]+)\((.*)\)/i.exec(format);
  if (m1) {
    var m2 = m1[2].split(","), a = 1;
    switch (m1[1]) {
      case "hsla":
      case "rgba": {
        a = parseFloat(m2[3]);
        break;
      }
    }
    switch (m1[1]) {
      case "hsla":
      case "hsl": {
        var h = parseFloat(m2[0]), // degrees
            s = parseFloat(m2[1]) / 100, // percentage
            l = parseFloat(m2[2]) / 100; // percentage
        return (new pv.Color.Hsl(h, s, l, a)).rgb();
      }
      case "rgba":
      case "rgb": {
        function parse(c) { // either integer or percentage
          var f = parseFloat(c);
          return (c[c.length - 1] == '%') ? Math.round(f * 2.55) : f;
        }
        var r = parse(m2[0]), g = parse(m2[1]), b = parse(m2[2]);
        return pv.rgb(r, g, b, a);
      }
    }
  }

  /* Named colors. */
  format = pv.Color.names[format] || format;

  /* Hexadecimal colors: #rgb and #rrggbb. */
  if (format.charAt(0) == "#") {
    var r, g, b;
    if (format.length == 4) {
      r = format.charAt(1); r += r;
      g = format.charAt(2); g += g;
      b = format.charAt(3); b += b;
    } else if (format.length == 7) {
      r = format.substring(1, 3);
      g = format.substring(3, 5);
      b = format.substring(5, 7);
    }
    return pv.rgb(parseInt(r, 16), parseInt(g, 16), parseInt(b, 16), 1);
  }

  /* Otherwise, assume named colors. TODO allow lazy conversion to RGB. */
  return new pv.Color(format, 1);
};

/**
 * Constructs a color with the specified color format string and opacity. This
 * constructor should not be invoked directly; use {@link pv.color} instead.
 *
 * @class Represents an abstract (possibly translucent) color. The color is
 * divided into two parts: the <tt>color</tt> attribute, an opaque color format
 * string, and the <tt>opacity</tt> attribute, a float in [0, 1]. The color
 * space is dependent on the implementing class; all colors support the
 * {@link #rgb} method to convert to RGB color space for interpolation.
 *
 * <p>See also the <a href="../../api/Color.html">Color guide</a>.
 *
 * @param {string} color an opaque color format string, such as "#f00".
 * @param {number} opacity the opacity, in [0,1].
 * @see pv.color
 */
pv.Color = function(color, opacity) {
  /**
   * An opaque color format string, such as "#f00".
   *
   * @type string
   * @see <a href="http://www.w3.org/TR/SVG/types.html#ColorKeywords">SVG color
   * keywords</a>
   * @see <a href="http://www.w3.org/TR/css3-color/">CSS3 color module</a>
   */
  this.color = color;

  /**
   * The opacity, a float in [0, 1].
   *
   * @type number
   */
  this.opacity = opacity;
};

/**
 * Returns a new color that is a brighter version of this color. The behavior of
 * this method may vary slightly depending on the underlying color space.
 * Although brighter and darker are inverse operations, the results of a series
 * of invocations of these two methods might be inconsistent because of rounding
 * errors.
 *
 * @param [k] {number} an optional scale factor; defaults to 1.
 * @see #darker
 * @returns {pv.Color} a brighter color.
 */
pv.Color.prototype.brighter = function(k) {
  return this.rgb().brighter(k);
};

/**
 * Returns a new color that is a brighter version of this color. The behavior of
 * this method may vary slightly depending on the underlying color space.
 * Although brighter and darker are inverse operations, the results of a series
 * of invocations of these two methods might be inconsistent because of rounding
 * errors.
 *
 * @param [k] {number} an optional scale factor; defaults to 1.
 * @see #brighter
 * @returns {pv.Color} a darker color.
 */
pv.Color.prototype.darker = function(k) {
  return this.rgb().darker(k);
};

/**
 * Constructs a new RGB color with the specified channel values.
 *
 * @param {number} r the red channel, an integer in [0,255].
 * @param {number} g the green channel, an integer in [0,255].
 * @param {number} b the blue channel, an integer in [0,255].
 * @param {number} [a] the alpha channel, a float in [0,1].
 * @returns pv.Color.Rgb
 */
pv.rgb = function(r, g, b, a) {
  return new pv.Color.Rgb(r, g, b, (arguments.length == 4) ? a : 1);
};

/**
 * Constructs a new RGB color with the specified channel values.
 *
 * @class Represents a color in RGB space.
 *
 * @param {number} r the red channel, an integer in [0,255].
 * @param {number} g the green channel, an integer in [0,255].
 * @param {number} b the blue channel, an integer in [0,255].
 * @param {number} a the alpha channel, a float in [0,1].
 * @extends pv.Color
 */
pv.Color.Rgb = function(r, g, b, a) {
  pv.Color.call(this, a ? ("rgb(" + r + "," + g + "," + b + ")") : "none", a);

  /**
   * The red channel, an integer in [0, 255].
   *
   * @type number
   */
  this.r = r;

  /**
   * The green channel, an integer in [0, 255].
   *
   * @type number
   */
  this.g = g;

  /**
   * The blue channel, an integer in [0, 255].
   *
   * @type number
   */
  this.b = b;

  /**
   * The alpha channel, a float in [0, 1].
   *
   * @type number
   */
  this.a = a;
};
pv.Color.Rgb.prototype = pv.extend(pv.Color);

/**
 * Constructs a new RGB color with the same green, blue and alpha channels as
 * this color, with the specified red channel.
 *
 * @param {number} r the red channel, an integer in [0,255].
 */
pv.Color.Rgb.prototype.red = function(r) {
  return pv.rgb(r, this.g, this.b, this.a);
};

/**
 * Constructs a new RGB color with the same red, blue and alpha channels as this
 * color, with the specified green channel.
 *
 * @param {number} g the green channel, an integer in [0,255].
 */
pv.Color.Rgb.prototype.green = function(g) {
  return pv.rgb(this.r, g, this.b, this.a);
};

/**
 * Constructs a new RGB color with the same red, green and alpha channels as
 * this color, with the specified blue channel.
 *
 * @param {number} b the blue channel, an integer in [0,255].
 */
pv.Color.Rgb.prototype.blue = function(b) {
  return pv.rgb(this.r, this.g, b, this.a);
};

/**
 * Constructs a new RGB color with the same red, green and blue channels as this
 * color, with the specified alpha channel.
 *
 * @param {number} a the alpha channel, a float in [0,1].
 */
pv.Color.Rgb.prototype.alpha = function(a) {
  return pv.rgb(this.r, this.g, this.b, a);
};

/**
 * Returns the RGB color equivalent to this color. This method is abstract and
 * must be implemented by subclasses.
 *
 * @returns {pv.Color.Rgb} an RGB color.
 * @function
 * @name pv.Color.prototype.rgb
 */

/**
 * Returns this.
 *
 * @returns {pv.Color.Rgb} this.
 */
pv.Color.Rgb.prototype.rgb = function() { return this; };

/**
 * Returns a new color that is a brighter version of this color. This method
 * applies an arbitrary scale factor to each of the three RGB components of this
 * color to create a brighter version of this color. Although brighter and
 * darker are inverse operations, the results of a series of invocations of
 * these two methods might be inconsistent because of rounding errors.
 *
 * @param [k] {number} an optional scale factor; defaults to 1.
 * @see #darker
 * @returns {pv.Color.Rgb} a brighter color.
 */
pv.Color.Rgb.prototype.brighter = function(k) {
  k = Math.pow(0.7, arguments.length ? k : 1);
  var r = this.r, g = this.g, b = this.b, i = 30;
  if (!r && !g && !b) return pv.rgb(i, i, i, this.a);
  if (r && (r < i)) r = i;
  if (g && (g < i)) g = i;
  if (b && (b < i)) b = i;
  return pv.rgb(
      Math.min(255, Math.floor(r / k)),
      Math.min(255, Math.floor(g / k)),
      Math.min(255, Math.floor(b / k)),
      this.a);
};

/**
 * Returns a new color that is a darker version of this color. This method
 * applies an arbitrary scale factor to each of the three RGB components of this
 * color to create a darker version of this color. Although brighter and darker
 * are inverse operations, the results of a series of invocations of these two
 * methods might be inconsistent because of rounding errors.
 *
 * @param [k] {number} an optional scale factor; defaults to 1.
 * @see #brighter
 * @returns {pv.Color.Rgb} a darker color.
 */
pv.Color.Rgb.prototype.darker = function(k) {
  k = Math.pow(0.7, arguments.length ? k : 1);
  return pv.rgb(
      Math.max(0, Math.floor(k * this.r)),
      Math.max(0, Math.floor(k * this.g)),
      Math.max(0, Math.floor(k * this.b)),
      this.a);
};

/**
 * Constructs a new HSL color with the specified values.
 *
 * @param {number} h the hue, an integer in [0, 360].
 * @param {number} s the saturation, a float in [0, 1].
 * @param {number} l the lightness, a float in [0, 1].
 * @param {number} [a] the opacity, a float in [0, 1].
 * @returns pv.Color.Hsl
 */
pv.hsl = function(h, s, l, a) {
  return new pv.Color.Hsl(h, s, l,  (arguments.length == 4) ? a : 1);
};

/**
 * Constructs a new HSL color with the specified values.
 *
 * @class Represents a color in HSL space.
 *
 * @param {number} h the hue, an integer in [0, 360].
 * @param {number} s the saturation, a float in [0, 1].
 * @param {number} l the lightness, a float in [0, 1].
 * @param {number} a the opacity, a float in [0, 1].
 * @extends pv.Color
 */
pv.Color.Hsl = function(h, s, l, a) {
  pv.Color.call(this, "hsl(" + h + "," + (s * 100) + "%," + (l * 100) + "%)", a);

  /**
   * The hue, an integer in [0, 360].
   *
   * @type number
   */
  this.h = h;

  /**
   * The saturation, a float in [0, 1].
   *
   * @type number
   */
  this.s = s;

  /**
   * The lightness, a float in [0, 1].
   *
   * @type number
   */
  this.l = l;

  /**
   * The opacity, a float in [0, 1].
   *
   * @type number
   */
  this.a = a;
};
pv.Color.Hsl.prototype = pv.extend(pv.Color);

/**
 * Constructs a new HSL color with the same saturation, lightness and alpha as
 * this color, and the specified hue.
 *
 * @param {number} h the hue, an integer in [0, 360].
 */
pv.Color.Hsl.prototype.hue = function(h) {
  return pv.hsl(h, this.s, this.l, this.a);
};

/**
 * Constructs a new HSL color with the same hue, lightness and alpha as this
 * color, and the specified saturation.
 *
 * @param {number} s the saturation, a float in [0, 1].
 */
pv.Color.Hsl.prototype.saturation = function(s) {
  return pv.hsl(this.h, s, this.l, this.a);
};

/**
 * Constructs a new HSL color with the same hue, saturation and alpha as this
 * color, and the specified lightness.
 *
 * @param {number} l the lightness, a float in [0, 1].
 */
pv.Color.Hsl.prototype.lightness = function(l) {
  return pv.hsl(this.h, this.s, l, this.a);
};

/**
 * Constructs a new HSL color with the same hue, saturation and lightness as
 * this color, and the specified alpha.
 *
 * @param {number} a the opacity, a float in [0, 1].
 */
pv.Color.Hsl.prototype.alpha = function(a) {
  return pv.hsl(this.h, this.s, this.l, a);
};

/**
 * Returns the RGB color equivalent to this HSL color.
 *
 * @returns {pv.Color.Rgb} an RGB color.
 */
pv.Color.Hsl.prototype.rgb = function() {
  var h = this.h, s = this.s, l = this.l;

  /* Some simple corrections for h, s and l. */
  h = h % 360; if (h < 0) h += 360;
  s = Math.max(0, Math.min(s, 1));
  l = Math.max(0, Math.min(l, 1));

  /* From FvD 13.37, CSS Color Module Level 3 */
  var m2 = (l <= .5) ? (l * (1 + s)) : (l + s - l * s);
  var m1 = 2 * l - m2;
  function v(h) {
    if (h > 360) h -= 360;
    else if (h < 0) h += 360;
    if (h < 60) return m1 + (m2 - m1) * h / 60;
    if (h < 180) return m2;
    if (h < 240) return m1 + (m2 - m1) * (240 - h) / 60;
    return m1;
  }
  function vv(h) {
    return Math.round(v(h) * 255);
  }

  return pv.rgb(vv(h + 120), vv(h), vv(h - 120), this.a);
};

/**
 * @private SVG color keywords, per CSS Color Module Level 3.
 *
 * @see <a href="http://www.w3.org/TR/SVG/types.html#ColorKeywords">SVG color
 * keywords</a>
 */
pv.Color.names = {
  aliceblue: "#f0f8ff",
  antiquewhite: "#faebd7",
  aqua: "#00ffff",
  aquamarine: "#7fffd4",
  azure: "#f0ffff",
  beige: "#f5f5dc",
  bisque: "#ffe4c4",
  black: "#000000",
  blanchedalmond: "#ffebcd",
  blue: "#0000ff",
  blueviolet: "#8a2be2",
  brown: "#a52a2a",
  burlywood: "#deb887",
  cadetblue: "#5f9ea0",
  chartreuse: "#7fff00",
  chocolate: "#d2691e",
  coral: "#ff7f50",
  cornflowerblue: "#6495ed",
  cornsilk: "#fff8dc",
  crimson: "#dc143c",
  cyan: "#00ffff",
  darkblue: "#00008b",
  darkcyan: "#008b8b",
  darkgoldenrod: "#b8860b",
  darkgray: "#a9a9a9",
  darkgreen: "#006400",
  darkgrey: "#a9a9a9",
  darkkhaki: "#bdb76b",
  darkmagenta: "#8b008b",
  darkolivegreen: "#556b2f",
  darkorange: "#ff8c00",
  darkorchid: "#9932cc",
  darkred: "#8b0000",
  darksalmon: "#e9967a",
  darkseagreen: "#8fbc8f",
  darkslateblue: "#483d8b",
  darkslategray: "#2f4f4f",
  darkslategrey: "#2f4f4f",
  darkturquoise: "#00ced1",
  darkviolet: "#9400d3",
  deeppink: "#ff1493",
  deepskyblue: "#00bfff",
  dimgray: "#696969",
  dimgrey: "#696969",
  dodgerblue: "#1e90ff",
  firebrick: "#b22222",
  floralwhite: "#fffaf0",
  forestgreen: "#228b22",
  fuchsia: "#ff00ff",
  gainsboro: "#dcdcdc",
  ghostwhite: "#f8f8ff",
  gold: "#ffd700",
  goldenrod: "#daa520",
  gray: "#808080",
  green: "#008000",
  greenyellow: "#adff2f",
  grey: "#808080",
  honeydew: "#f0fff0",
  hotpink: "#ff69b4",
  indianred: "#cd5c5c",
  indigo: "#4b0082",
  ivory: "#fffff0",
  khaki: "#f0e68c",
  lavender: "#e6e6fa",
  lavenderblush: "#fff0f5",
  lawngreen: "#7cfc00",
  lemonchiffon: "#fffacd",
  lightblue: "#add8e6",
  lightcoral: "#f08080",
  lightcyan: "#e0ffff",
  lightgoldenrodyellow: "#fafad2",
  lightgray: "#d3d3d3",
  lightgreen: "#90ee90",
  lightgrey: "#d3d3d3",
  lightpink: "#ffb6c1",
  lightsalmon: "#ffa07a",
  lightseagreen: "#20b2aa",
  lightskyblue: "#87cefa",
  lightslategray: "#778899",
  lightslategrey: "#778899",
  lightsteelblue: "#b0c4de",
  lightyellow: "#ffffe0",
  lime: "#00ff00",
  limegreen: "#32cd32",
  linen: "#faf0e6",
  magenta: "#ff00ff",
  maroon: "#800000",
  mediumaquamarine: "#66cdaa",
  mediumblue: "#0000cd",
  mediumorchid: "#ba55d3",
  mediumpurple: "#9370db",
  mediumseagreen: "#3cb371",
  mediumslateblue: "#7b68ee",
  mediumspringgreen: "#00fa9a",
  mediumturquoise: "#48d1cc",
  mediumvioletred: "#c71585",
  midnightblue: "#191970",
  mintcream: "#f5fffa",
  mistyrose: "#ffe4e1",
  moccasin: "#ffe4b5",
  navajowhite: "#ffdead",
  navy: "#000080",
  oldlace: "#fdf5e6",
  olive: "#808000",
  olivedrab: "#6b8e23",
  orange: "#ffa500",
  orangered: "#ff4500",
  orchid: "#da70d6",
  palegoldenrod: "#eee8aa",
  palegreen: "#98fb98",
  paleturquoise: "#afeeee",
  palevioletred: "#db7093",
  papayawhip: "#ffefd5",
  peachpuff: "#ffdab9",
  peru: "#cd853f",
  pink: "#ffc0cb",
  plum: "#dda0dd",
  powderblue: "#b0e0e6",
  purple: "#800080",
  red: "#ff0000",
  rosybrown: "#bc8f8f",
  royalblue: "#4169e1",
  saddlebrown: "#8b4513",
  salmon: "#fa8072",
  sandybrown: "#f4a460",
  seagreen: "#2e8b57",
  seashell: "#fff5ee",
  sienna: "#a0522d",
  silver: "#c0c0c0",
  skyblue: "#87ceeb",
  slateblue: "#6a5acd",
  slategray: "#708090",
  slategrey: "#708090",
  snow: "#fffafa",
  springgreen: "#00ff7f",
  steelblue: "#4682b4",
  tan: "#d2b48c",
  teal: "#008080",
  thistle: "#d8bfd8",
  tomato: "#ff6347",
  turquoise: "#40e0d0",
  violet: "#ee82ee",
  wheat: "#f5deb3",
  white: "#ffffff",
  whitesmoke: "#f5f5f5",
  yellow: "#ffff00",
  yellowgreen: "#9acd32"
};
