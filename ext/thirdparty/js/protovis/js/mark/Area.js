/**
 * Constructs a new area mark with default properties. Areas are not typically
 * constructed directly, but by adding to a panel or an existing mark via
 * {@link pv.Mark#add}.
 *
 * @class Represents an area mark: the solid area between two series of
 * connected line segments. Unsurprisingly, areas are used most frequently for
 * area charts.
 *
 * <p>Just as a line represents a polyline, the <tt>Area</tt> mark type
 * represents a <i>polygon</i>. However, an area is not an arbitrary polygon;
 * vertices are paired either horizontally or vertically into parallel
 * <i>spans</i>, and each span corresponds to an associated datum. Either the
 * width or the height must be specified, but not both; this determines whether
 * the area is horizontally-oriented or vertically-oriented.  Like lines, areas
 * can be stroked and filled with arbitrary colors.
 *
 * <p>See also the <a href="../../api/Area.html">Area guide</a>.
 *
 * @extends pv.Mark
 */
pv.Area = function() {
  pv.Mark.call(this);
};

pv.Area.prototype = pv.extend(pv.Mark)
    .property("width")
    .property("height")
    .property("lineWidth")
    .property("strokeStyle")
    .property("fillStyle")
    .property("segmented")
    .property("interpolate");

pv.Area.prototype.type = "area";

/**
 * The width of a given span, in pixels; used for horizontal spans. If the width
 * is specified, the height property should be 0 (the default). Either the top
 * or bottom property should be used to space the spans vertically, typically as
 * a multiple of the index.
 *
 * @type number
 * @name pv.Area.prototype.width
 */

/**
 * The height of a given span, in pixels; used for vertical spans. If the height
 * is specified, the width property should be 0 (the default). Either the left
 * or right property should be used to space the spans horizontally, typically
 * as a multiple of the index.
 *
 * @type number
 * @name pv.Area.prototype.height
 */

/**
 * The width of stroked lines, in pixels; used in conjunction with
 * <tt>strokeStyle</tt> to stroke the perimeter of the area. Unlike the
 * {@link Line} mark type, the entire perimeter is stroked, rather than just one
 * edge. The default value of this property is 1.5, but since the default stroke
 * style is null, area marks are not stroked by default.
 *
 * <p>This property is <i>fixed</i> for non-segmented areas. See
 * {@link pv.Mark}.
 *
 * @type number
 * @name pv.Area.prototype.lineWidth
 */

/**
 * The style of stroked lines; used in conjunction with <tt>lineWidth</tt> to
 * stroke the perimeter of the area. Unlike the {@link Line} mark type, the
 * entire perimeter is stroked, rather than just one edge. The default value of
 * this property is null, meaning areas are not stroked by default.
 *
 * <p>This property is <i>fixed</i> for non-segmented areas. See
 * {@link pv.Mark}.
 *
 * @type string
 * @name pv.Area.prototype.strokeStyle
 * @see pv.color
 */

/**
 * The area fill style; if non-null, the interior of the polygon forming the
 * area is filled with the specified color. The default value of this property
 * is a categorical color.
 *
 * <p>This property is <i>fixed</i> for non-segmented areas. See
 * {@link pv.Mark}.
 *
 * @type string
 * @name pv.Area.prototype.fillStyle
 * @see pv.color
 */

/**
 * Whether the area is segmented; whether variations in fill style, stroke
 * style, and the other properties are treated as fixed. Rendering segmented
 * areas is noticeably slower than non-segmented areas.
 *
 * <p>This property is <i>fixed</i>. See {@link pv.Mark}.
 *
 * @type boolean
 * @name pv.Area.prototype.segmented
 */

/**
 * How to interpolate between values. Linear interpolation ("linear") is the
 * default, producing a straight line between points. For piecewise constant
 * functions (i.e., step functions), either "step-before" or "step-after" can be
 * specified.
 *
 * <p>Note: this property is currently supported only on non-segmented areas.
 *
 * <p>This property is <i>fixed</i>. See {@link pv.Mark}.
 *
 * @type string
 * @name pv.Area.prototype.interpolate
 */

/**
 * Default properties for areas. By default, there is no stroke and the fill
 * style is a categorical color.
 *
 * @type pv.Area
 */
pv.Area.prototype.defaults = new pv.Area()
    .extend(pv.Mark.prototype.defaults)
    .lineWidth(1.5)
    .fillStyle(defaultFillStyle)
    .interpolate("linear");

/**
 * Constructs a new area anchor with default properties. Areas support five
 * different anchors:<ul>
 *
 * <li>top
 * <li>left
 * <li>center
 * <li>bottom
 * <li>right
 *
 * </ul>In addition to positioning properties (left, right, top bottom), the
 * anchors support text rendering properties (text-align, text-baseline). Text is
 * rendered to appear inside the area polygon.
 *
 * <p>To facilitate stacking of areas, the anchors are defined in terms of their
 * opposite edge. For example, the top anchor defines the bottom property, such
 * that the area grows upwards; the bottom anchor instead defines the top
 * property, such that the area grows downwards. Of course, in general it is
 * more robust to use panels and the cousin accessor to define stacked area
 * marks; see {@link pv.Mark#scene} for an example.
 *
 * @param {string} name the anchor name; either a string or a property function.
 * @returns {pv.Anchor}
 */
pv.Area.prototype.anchor = function(name) {
  var area = this;
  return pv.Mark.prototype.anchor.call(this, name)
    .left(function() {
        switch (this.name()) {
          case "bottom":
          case "top":
          case "center": return area.left() + area.width() / 2;
          case "right": return area.left() + area.width();
        }
        return null;
      })
    .right(function() {
        switch (this.name()) {
          case "bottom":
          case "top":
          case "center": return area.right() + area.width() / 2;
          case "left": return area.right() + area.width();
        }
        return null;
      })
    .top(function() {
        switch (this.name()) {
          case "left":
          case "right":
          case "center": return area.top() + area.height() / 2;
          case "bottom": return area.top() + area.height();
        }
        return null;
      })
    .bottom(function() {
        switch (this.name()) {
          case "left":
          case "right":
          case "center": return area.bottom() + area.height() / 2;
          case "top": return area.bottom() + area.height();
        }
        return null;
      })
    .textAlign(function() {
        switch (this.name()) {
          case "bottom":
          case "top":
          case "center": return "center";
          case "right": return "right";
        }
        return "left";
      })
    .textBaseline(function() {
        switch (this.name()) {
          case "right":
          case "left":
          case "center": return "middle";
          case "top": return "top";
        }
        return "bottom";
      });
};

/**
 * @private Overrides the default behavior of {@link pv.Mark.buildImplied} such
 * that the width and height are set to zero if null.
 *
 * @param s a node in the scene graph; the instance of the mark to build.
 */
pv.Area.prototype.buildImplied = function(s) {
  if (s.height == null) s.height = 0;
  if (s.width == null) s.width = 0;
  pv.Mark.prototype.buildImplied.call(this, s);
};

/** @private */
var pv_Area_specials = {left:1, top:1, right:1, bottom:1, width:1, height:1, name:1};

/** @private */
pv.Area.prototype.bind = function() {
  pv.Mark.prototype.bind.call(this);
  var binds = this.binds,
      properties = binds.properties,
      specials = binds.specials = [];
  for (var i = 0, n = properties.length; i < n; i++) {
    var p = properties[i];
    if (p.name in pv_Area_specials) specials.push(p);
  }
};

/** @private */
pv.Area.prototype.buildInstance = function(s) {
  if (this.index && !this.scene[0].segmented) {
    this.buildProperties(s, this.binds.specials);
    this.buildImplied(s);
  } else {
    pv.Mark.prototype.buildInstance.call(this, s);
  }
};
