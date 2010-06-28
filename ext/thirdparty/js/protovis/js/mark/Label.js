/**
 * Constructs a new label mark with default properties. Labels are not typically
 * constructed directly, but by adding to a panel or an existing mark via
 * {@link pv.Mark#add}.
 *
 * @class Represents a text label, allowing textual annotation of other marks or
 * arbitrary text within the visualization. The character data must be plain
 * text (unicode), though the text can be styled using the {@link #font}
 * property. If rich text is needed, external HTML elements can be overlaid on
 * the canvas by hand.
 *
 * <p>Labels are positioned using the box model, similarly to {@link Dot}. Thus,
 * a label has no width or height, but merely a text anchor location. The text
 * is positioned relative to this anchor location based on the
 * {@link #textAlign}, {@link #textBaseline} and {@link #textMargin} properties.
 * Furthermore, the text may be rotated using {@link #textAngle}.
 *
 * <p>Labels ignore events, so as to not interfere with event handlers on
 * underlying marks, such as bars. In the future, we may support event handlers
 * on labels.
 *
 * <p>See also the <a href="../../api/Label.html">Label guide</a>.
 *
 * @extends pv.Mark
 */
pv.Label = function() {
  pv.Mark.call(this);
};

pv.Label.prototype = pv.extend(pv.Mark)
    .property("text")
    .property("font")
    .property("textAngle")
    .property("textStyle")
    .property("textAlign")
    .property("textBaseline")
    .property("textMargin")
    .property("textShadow");

pv.Label.prototype.type = "label";

/**
 * The character data to render; a string. The default value of the text
 * property is the identity function, meaning the label's associated datum will
 * be rendered using its <tt>toString</tt>.
 *
 * @type string
 * @name pv.Label.prototype.text
 */

/**
 * The font format, per the CSS Level 2 specification. The default font is "10px
 * sans-serif", for consistency with the HTML 5 canvas element specification.
 * Note that since text is not wrapped, any line-height property will be
 * ignored. The other font-style, font-variant, font-weight, font-size and
 * font-family properties are supported.
 *
 * @see <a href="http://www.w3.org/TR/CSS2/fonts.html#font-shorthand">CSS2 fonts</a>
 * @type string
 * @name pv.Label.prototype.font
 */

/**
 * The rotation angle, in radians. Text is rotated clockwise relative to the
 * anchor location. For example, with the default left alignment, an angle of
 * Math.PI / 2 causes text to proceed downwards. The default angle is zero.
 *
 * @type number
 * @name pv.Label.prototype.textAngle
 */

/**
 * The text color. The name "textStyle" is used for consistency with "fillStyle"
 * and "strokeStyle", although it might be better to rename this property (and
 * perhaps use the same name as "strokeStyle"). The default color is black.
 *
 * @type string
 * @name pv.Label.prototype.textStyle
 * @see pv.color
 */

/**
 * The horizontal text alignment. One of:<ul>
 *
 * <li>left
 * <li>center
 * <li>right
 *
 * </ul>The default horizontal alignment is left.
 *
 * @type string
 * @name pv.Label.prototype.textAlign
 */

/**
 * The vertical text alignment. One of:<ul>
 *
 * <li>top
 * <li>middle
 * <li>bottom
 *
 * </ul>The default vertical alignment is bottom.
 *
 * @type string
 * @name pv.Label.prototype.textBaseline
 */

/**
 * The text margin; may be specified in pixels, or in font-dependent units (such
 * as ".1ex"). The margin can be used to pad text away from its anchor location,
 * in a direction dependent on the horizontal and vertical alignment
 * properties. For example, if the text is left- and middle-aligned, the margin
 * shifts the text to the right. The default margin is 3 pixels.
 *
 * @type number
 * @name pv.Label.prototype.textMargin
 */

/**
 * A list of shadow effects to be applied to text, per the CSS Text Level 3
 * text-shadow property. An example specification is "0.1em 0.1em 0.1em
 * rgba(0,0,0,.5)"; the first length is the horizontal offset, the second the
 * vertical offset, and the third the blur radius.
 *
 * @see <a href="http://www.w3.org/TR/css3-text/#text-shadow">CSS3 text</a>
 * @type string
 * @name pv.Label.prototype.textShadow
 */

/**
 * Default properties for labels. See the individual properties for the default
 * values.
 *
 * @type pv.Label
 */
pv.Label.prototype.defaults = new pv.Label()
    .extend(pv.Mark.prototype.defaults)
    .text(pv.identity)
    .font("10px sans-serif")
    .textAngle(0)
    .textStyle("black")
    .textAlign("left")
    .textBaseline("bottom")
    .textMargin(3);
