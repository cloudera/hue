/**
 * Constructs a new mark anchor with default properties.
 *
 * @class Represents an anchor on a given mark. An anchor is itself a mark, but
 * without a visual representation. It serves only to provide useful default
 * properties that can be inherited by other marks. Each type of mark can define
 * any number of named anchors for convenience. If the concrete mark type does
 * not define an anchor implementation specifically, one will be inherited from
 * the mark's parent class.
 *
 * <p>For example, the bar mark provides anchors for its four sides: left,
 * right, top and bottom. Adding a label to the top anchor of a bar,
 *
 * <pre>bar.anchor("top").add(pv.Label);</pre>
 *
 * will render a text label on the top edge of the bar; the top anchor defines
 * the appropriate position properties (top and left), as well as text-rendering
 * properties for convenience (textAlign and textBaseline).
 *
 * @extends pv.Mark
 */
pv.Anchor = function() {
  pv.Mark.call(this);
};

pv.Anchor.prototype = pv.extend(pv.Mark)
    .property("name");

/**
 * The anchor name. The set of supported anchor names is dependent on the
 * concrete mark type; see the mark type for details. For example, bars support
 * left, right, top and bottom anchors.
 *
 * <p>While anchor names are typically constants, the anchor name is a true
 * property, which means you can specify a function to compute the anchor name
 * dynamically. For instance, if you wanted to alternate top and bottom anchors,
 * saying
 *
 * <pre>m.anchor(function() (this.index % 2) ? "top" : "bottom").add(pv.Dot);</pre>
 *
 * would have the desired effect.
 *
 * @type string
 * @name pv.Anchor.prototype.name
 */
