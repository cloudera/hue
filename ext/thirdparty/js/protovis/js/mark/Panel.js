/**
 * Constructs a new, empty panel with default properties. Panels, with the
 * exception of the root panel, are not typically constructed directly; instead,
 * they are added to an existing panel or mark via {@link pv.Mark#add}.
 *
 * @class Represents a container mark. Panels allow repeated or nested
 * structures, commonly used in small multiple displays where a small
 * visualization is tiled to facilitate comparison across one or more
 * dimensions. Other types of visualizations may benefit from repeated and
 * possibly overlapping structure as well, such as stacked area charts. Panels
 * can also offset the position of marks to provide padding from surrounding
 * content.
 *
 * <p>All Protovis displays have at least one panel; this is the root panel to
 * which marks are rendered. The box model properties (four margins, width and
 * height) are used to offset the positions of contained marks. The data
 * property determines the panel count: a panel is generated once per associated
 * datum. When nested panels are used, property functions can declare additional
 * arguments to access the data associated with enclosing panels.
 *
 * <p>Panels can be rendered inline, facilitating the creation of sparklines.
 * This allows designers to reuse browser layout features, such as text flow and
 * tables; designers can also overlay HTML elements such as rich text and
 * images.
 *
 * <p>All panels have a <tt>children</tt> array (possibly empty) containing the
 * child marks in the order they were added. Panels also have a <tt>root</tt>
 * field which points to the root (outermost) panel; the root panel's root field
 * points to itself.
 *
 * <p>See also the <a href="../../api/">Protovis guide</a>.
 *
 * @extends pv.Bar
 */
pv.Panel = function() {
  pv.Bar.call(this);

  /**
   * The child marks; zero or more {@link pv.Mark}s in the order they were
   * added.
   *
   * @see #add
   * @type pv.Mark[]
   */
  this.children = [];
  this.root = this;

  /**
   * The internal $dom field is set by the Protovis loader; see lang/init.js. It
   * refers to the script element that contains the Protovis specification, so
   * that the panel knows where in the DOM to insert the generated SVG element.
   *
   * @private
   */
  this.$dom = pv.Panel.$dom;
};

pv.Panel.prototype = pv.extend(pv.Bar)
    .property("canvas")
    .property("overflow");

pv.Panel.prototype.type = "panel";

/**
 * The canvas element; either the string ID of the canvas element in the current
 * document, or a reference to the canvas element itself. If null, a canvas
 * element will be created and inserted into the document at the location of the
 * script element containing the current Protovis specification. This property
 * only applies to root panels and is ignored on nested panels.
 *
 * <p>Note: the "canvas" element here refers to a <tt>div</tt> (or other suitable
 * HTML container element), <i>not</i> a <tt>canvas</tt> element. The name of
 * this property is a historical anachronism from the first implementation that
 * used HTML 5 canvas, rather than SVG.
 *
 * @type string
 * @name pv.Panel.prototype.canvas
 */

/**
 * Default properties for panels. By default, the margins are zero, the fill
 * style is transparent.
 *
 * @type pv.Panel
 */
pv.Panel.prototype.defaults = new pv.Panel()
    .extend(pv.Bar.prototype.defaults)
    .fillStyle(null)
    .overflow("visible");

/**
 * Returns an anchor with the specified name. This method is overridden since
 * the behavior of Panel anchors is slightly different from normal anchors:
 * adding to an anchor adds to the anchor target's, rather than the anchor
 * target's parent. To avoid double margins, we override the anchor's proto so
 * that the margins are zero.
 *
 * @param {string} name the anchor name; either a string or a property function.
 * @returns {pv.Anchor} the new anchor.
 */
pv.Panel.prototype.anchor = function(name) {

  /* A "view" of this panel whose margins appear to be zero. */
  function z() { return 0; }
  z.prototype = this;
  z.prototype.left = z.prototype.right = z.prototype.top = z.prototype.bottom = z;

  var anchor = pv.Bar.prototype.anchor.call(new z(), name)
      .data(function(d) { return [d]; });
  anchor.parent = this;
  return anchor;
};

/**
 * Adds a new mark of the specified type to this panel. Unlike the normal
 * {@link Mark#add} behavior, adding a mark to a panel does not cause the mark
 * to inherit from the panel. Since the contained marks are offset by the panel
 * margins already, inheriting properties is generally undesirable; of course,
 * it is always possible to change this behavior by calling {@link Mark#extend}
 * explicitly.
 *
 * @param {function} type the type of the new mark to add.
 * @returns {pv.Mark} the new mark.
 */
pv.Panel.prototype.add = function(type) {
  var child = new type();
  child.parent = this;
  child.root = this.root;
  child.childIndex = this.children.length;
  this.children.push(child);
  return child;
};

/** @private TODO */
pv.Panel.prototype.bind = function() {
  pv.Mark.prototype.bind.call(this);
  for (var i = 0; i < this.children.length; i++) {
    this.children[i].bind();
  }
};

/**
 * @private Evaluates all of the properties for this panel for the specified
 * instance <tt>s</tt> in the scene graph, including recursively building the
 * scene graph for child marks.
 *
 * @param s a node in the scene graph; the instance of the panel to build.
 * @see Mark#scene
 */
pv.Panel.prototype.buildInstance = function(s) {
  pv.Bar.prototype.buildInstance.call(this, s);
  if (!s.children) s.children = [];

  /*
   * Build each child, passing in the parent (this panel) scene graph node. The
   * child mark's scene is initialized from the corresponding entry in the
   * existing scene graph, such that properties from the previous build can be
   * reused; this is largely to facilitate the recycling of SVG elements.
   */
  for (var i = 0; i < this.children.length; i++) {
    this.children[i].scene = s.children[i]; // possibly undefined
    this.children[i].build();
  }

  /*
   * Once the child marks have been built, the new scene graph nodes are removed
   * from the child marks and placed into the scene graph. The nodes cannot
   * remain on the child nodes because this panel (or a parent panel) may be
   * instantiated multiple times!
   */
  for (var i = 0; i < this.children.length; i++) {
    s.children[i] = this.children[i].scene;
    delete this.children[i].scene;
  }

  /* Delete any expired child scenes, should child marks have been removed. */
  s.children.length = this.children.length;
};

/**
 * @private Computes the implied properties for this panel for the specified
 * instance <tt>s</tt> in the scene graph. Panels have two implied
 * properties:<ul>
 *
 * <li>The <tt>canvas</tt> property references the DOM element, typically a DIV,
 * that contains the SVG element that is used to display the visualization. This
 * property may be specified as a string, referring to the unique ID of the
 * element in the DOM. The string is converted to a reference to the DOM
 * element. The width and height of the SVG element is inferred from this DOM
 * element. If no canvas property is specified, a new SVG element is created and
 * inserted into the document, using the panel dimensions; see
 * {@link #createCanvas}.
 *
 * <li>The <tt>children</tt> array, while not a property per se, contains the
 * scene graph for each child mark. This array is initialized to be empty, and
 * is populated above in {@link #buildInstance}.
 *
 * </ul>The current implementation creates the SVG element, if necessary, during
 * the build phase; in the future, it may be preferrable to move this to the
 * update phase, although then the canvas property would be undefined. In
 * addition, DOM inspection is necessary to define the implied width and height
 * properties that may be inferred from the DOM.
 *
 * @param s a node in the scene graph; the instance of the panel to build.
 */
pv.Panel.prototype.buildImplied = function(s) {
  if (!this.parent) {
    var c = s.canvas;
    if (c) {
      if (typeof c == "string") c = document.getElementById(c);

      /* Clear the container if it's not associated with this panel. */
      if (c.$panel != this) {
        c.$panel = this;
        c.innerHTML = "";
      }

      /* If width and height weren't specified, inspect the container. */
      var w, h;
      if (s.width == null) {
        w = parseFloat(pv.css(c, "width"));
        s.width = w - s.left - s.right;
      }
      if (s.height == null) {
        h = parseFloat(pv.css(c, "height"));
        s.height = h - s.top - s.bottom;
      }
    } else if (s.$canvas) {

      /*
       * If the canvas property is null, and we previously created a canvas for
       * this scene node, reuse the previous canvas rather than creating a new
       * one.
       */
      c = s.$canvas;
    } else {

      /**
       * Returns the last element in the current document's body. The canvas
       * element is appended to this last element if another DOM element has not
       * already been specified via the <tt>$dom</tt> field.
       */
      function lastElement() {
        var node = document.body;
        while (node.lastChild && node.lastChild.tagName) {
          node = node.lastChild;
        }
        return (node == document.body) ? node : node.parentNode;
      }

      /* Insert a new container into the DOM. */
      c = s.$canvas = document.createElement("span");
      this.$dom // script element for text/javascript+protovis
     	  // HUE CHANGE
          ? ((this.$dom.tagName != 'SCRIPT') ? this.$dom.appendChild(c) : this.$dom.parentNode.insertBefore(c, this.$dom))
          : lastElement().appendChild(c);
    }
    s.canvas = c;
  }
  pv.Bar.prototype.buildImplied.call(this, s);
};
