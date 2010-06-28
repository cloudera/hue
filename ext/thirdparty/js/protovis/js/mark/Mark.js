/**
 * Constructs a new mark with default properties. Marks, with the exception of
 * the root panel, are not typically constructed directly; instead, they are
 * added to a panel or an existing mark via {@link pv.Mark#add}.
 *
 * @class Represents a data-driven graphical mark. The <tt>Mark</tt> class is
 * the base class for all graphical marks in Protovis; it does not provide any
 * specific rendering functionality, but together with {@link Panel} establishes
 * the core framework.
 *
 * <p>Concrete mark types include familiar visual elements such as bars, lines
 * and labels. Although a bar mark may be used to construct a bar chart, marks
 * know nothing about charts; it is only through their specification and
 * composition that charts are produced. These building blocks permit many
 * combinatorial possibilities.
 *
 * <p>Marks are associated with <b>data</b>: a mark is generated once per
 * associated datum, mapping the datum to visual <b>properties</b> such as
 * position and color. Thus, a single mark specification represents a set of
 * visual elements that share the same data and visual encoding. The type of
 * mark defines the names of properties and their meaning. A property may be
 * static, ignoring the associated datum and returning a constant; or, it may be
 * dynamic, derived from the associated datum or index. Such dynamic encodings
 * can be specified succinctly using anonymous functions. Special properties
 * called event handlers can be registered to add interactivity.
 *
 * <p>Protovis uses <b>inheritance</b> to simplify the specification of related
 * marks: a new mark can be derived from an existing mark, inheriting its
 * properties. The new mark can then override properties to specify new
 * behavior, potentially in terms of the old behavior. In this way, the old mark
 * serves as the <b>prototype</b> for the new mark. Most mark types share the
 * same basic properties for consistency and to facilitate inheritance.
 *
 * <p>The prioritization of redundant properties is as follows:<ol>
 *
 * <li>If the <tt>width</tt> property is not specified (i.e., null), its value
 * is the width of the parent panel, minus this mark's left and right margins;
 * the left and right margins are zero if not specified.
 *
 * <li>Otherwise, if the <tt>right</tt> margin is not specified, its value is
 * the width of the parent panel, minus this mark's width and left margin; the
 * left margin is zero if not specified.
 *
 * <li>Otherwise, if the <tt>left</tt> property is not specified, its value is
 * the width of the parent panel, minus this mark's width and the right margin.
 *
 * </ol>This prioritization is then duplicated for the <tt>height</tt>,
 * <tt>bottom</tt> and <tt>top</tt> properties, respectively.
 *
 * <p>While most properties are <i>variable</i>, some mark types, such as lines
 * and areas, generate a single visual element rather than a distinct visual
 * element per datum. With these marks, some properties may be <b>fixed</b>.
 * Fixed properties can vary per mark, but not <i>per datum</i>! These
 * properties are evaluated solely for the first (0-index) datum, and typically
 * are specified as a constant. However, it is valid to use a function if the
 * property varies between panels or is dynamically generated.
 *
 * <p>See also the <a href="../../api/">Protovis guide</a>.
 */
pv.Mark = function() {
  /*
   * TYPE 0 constant defs
   * TYPE 1 function defs
   * TYPE 2 constant properties
   * TYPE 3 function properties
   * in order of evaluation!
   */
  this.$properties = [];
};

/** @private TOOD */
pv.Mark.prototype.properties = {};

/**
 * @private Defines and registers a property method for the property with the
 * given name.  This method should be called on a mark class prototype to define
 * each exposed property. (Note this refers to the JavaScript
 * <tt>prototype</tt>, not the Protovis mark prototype, which is the {@link
 * #proto} field.)
 *
 * <p>The created property method supports several modes of invocation: <ol>
 *
 * <li>If invoked with a <tt>Function</tt> argument, this function is evaluated
 * for each associated datum. The return value of the function is used as the
 * computed property value. The context of the function (<tt>this</tt>) is this
 * mark. The arguments to the function are the associated data of this mark and
 * any enclosing panels. For example, a linear encoding of numerical data to
 * height is specified as
 *
 * <pre>m.height(function(d) d * 100);</pre>
 *
 * The expression <tt>d * 100</tt> will be evaluated for the height property of
 * each mark instance. The return value of the property method (e.g.,
 * <tt>m.height</tt>) is this mark (<tt>m</tt>)).<p>
 *
 * <li>If invoked with a non-function argument, the property is treated as a
 * constant. The return value of the property method (e.g., <tt>m.height</tt>)
 * is this mark.<p>
 *
 * <li>If invoked with no arguments, the computed property value for the current
 * mark instance in the scene graph is returned. This facilitates <i>property
 * chaining</i>, where one mark's properties are defined in terms of another's.
 * For example, to offset a mark's location from its prototype, you might say
 *
 * <pre>m.top(function() this.proto.top() + 10);</pre>
 *
 * Note that the index of the mark being evaluated (in the above example,
 * <tt>this.proto</tt>) is inherited from the <tt>Mark</tt> class and set by
 * this mark. So, if the fifth element's top property is being evaluated, the
 * fifth instance of <tt>this.proto</tt> will similarly be queried for the value
 * of its top property. If the mark being evaluated has a different number of
 * instances, or its data is unrelated, the behavior of this method is
 * undefined. In these cases it may be better to index the <tt>scene</tt>
 * explicitly to specify the exact instance.
 *
 * </ol><p>Property names should follow standard JavaScript method naming
 * conventions, using lowerCamel-style capitalization.
 *
 * <p>In addition to creating the property method, every property is registered
 * in the {@link #properties} map on the <tt>prototype</tt>. Although this is an
 * instance field, it is considered immutable and shared by all instances of a
 * given mark type. The <tt>properties</tt> map can be queried to see if a mark
 * type defines a particular property, such as width or height.
 *
 * @param {string} name the property name.
 */
pv.Mark.prototype.property = function(name) {
  if (!this.hasOwnProperty("properties")) {
    this.properties = pv.extend(this.properties);
  }
  this.properties[name] = true;

  /*
   * Define the setter-getter globally, since the default behavior should be the
   * same for all properties, and since the Protovis inheritance chain is
   * independent of the JavaScript inheritance chain. For example, anchors
   * define a "name" property that is evaluated on derived marks, even though
   * those marks don't normally have a name.
   */
  pv.Mark.prototype[name] = function(v) {
      if (arguments.length) {
        this.$properties.push({
            name: name,
            type: (typeof v == "function") ? 3 : 2,
            value: v
          });
        return this;
      }
      return this.scene[this.index][name];
    };

  return this;
};

/* Define all global properties. */
pv.Mark.prototype
    .property("data")
    .property("visible")
    .property("left")
    .property("right")
    .property("top")
    .property("bottom")
    .property("cursor")
    .property("title")
    .property("reverse");

/**
 * The mark type; a lower camelCase name. The type name controls rendering
 * behavior, and unless the rendering engine is extended, must be one of the
 * built-in concrete mark types: area, bar, dot, image, label, line, panel,
 * rule, or wedge.
 *
 * @type string
 * @name pv.Mark.prototype.type
 */

/**
 * The mark prototype, possibly undefined, from which to inherit property
 * functions. The mark prototype is not necessarily of the same type as this
 * mark. Any properties defined on this mark will override properties inherited
 * either from the prototype or from the type-specific defaults.
 *
 * @type pv.Mark
 * @name pv.Mark.prototype.proto
 */

/**
 * The enclosing parent panel. The parent panel is generally undefined only for
 * the root panel; however, it is possible to create "offscreen" marks that are
 * used only for inheritance purposes.
 *
 * @type pv.Panel
 * @name pv.Mark.prototype.parent
 */

/**
 * The child index. -1 if the enclosing parent panel is null; otherwise, the
 * zero-based index of this mark into the parent panel's <tt>children</tt> array.
 *
 * @type number
 */
pv.Mark.prototype.childIndex = -1;

/**
 * The mark index. The value of this field depends on which instance (i.e.,
 * which element of the data array) is currently being evaluated. During the
 * build phase, the index is incremented over each datum; when handling events,
 * the index is set to the instance that triggered the event.
 *
 * @type number
 */
pv.Mark.prototype.index = -1;

/**
 * The scene graph. The scene graph is an array of objects; each object (or
 * "node") corresponds to an instance of this mark and an element in the data
 * array. The scene graph can be traversed to lookup previously-evaluated
 * properties.
 *
 * <p>For instance, consider a stacked area chart. The bottom property of the
 * area can be defined using the <i>cousin</i> instance, which is the current
 * area instance in the previous instantiation of the parent panel. In this
 * sample code,
 *
 * <pre>new pv.Panel()
 *     .width(150).height(150)
 *   .add(pv.Panel)
 *     .data([[1, 1.2, 1.7, 1.5, 1.7],
 *            [.5, 1, .8, 1.1, 1.3],
 *            [.2, .5, .8, .9, 1]])
 *   .add(pv.Area)
 *     .data(function(d) d)
 *     .bottom(function() {
 *         var c = this.cousin();
 *         return c ? (c.bottom + c.height) : 0;
 *       })
 *     .height(function(d) d * 40)
 *     .left(function() this.index * 35)
 *   .root.render();</pre>
 *
 * the bottom property is computed based on the upper edge of the corresponding
 * datum in the previous series. The area's parent panel is instantiated once
 * per series, so the cousin refers to the previous (below) area mark. (Note
 * that the position of the upper edge is not the same as the top property,
 * which refers to the top margin: the distance from the top edge of the panel
 * to the top edge of the mark.)
 *
 * @see #first
 * @see #last
 * @see #sibling
 * @see #cousin
 * @name pv.Mark.prototype.scene
 */

/**
 * The root parent panel. This may be undefined for "offscreen" marks that are
 * created for inheritance purposes only.
 *
 * @type pv.Panel
 * @name pv.Mark.prototype.root
 */

/**
 * The data property; an array of objects. The size of the array determines the
 * number of marks that will be instantiated; each element in the array will be
 * passed to property functions to compute the property values. Typically, the
 * data property is specified as a constant array, such as
 *
 * <pre>m.data([1, 2, 3, 4, 5]);</pre>
 *
 * However, it is perfectly acceptable to define the data property as a
 * function. This function might compute the data dynamically, allowing
 * different data to be used per enclosing panel. For instance, in the stacked
 * area graph example (see {@link #scene}), the data function on the area mark
 * dereferences each series.
 *
 * @type array
 * @name pv.Mark.prototype.data
 */

/**
 * The visible property; a boolean determining whether or not the mark instance
 * is visible. If a mark instance is not visible, its other properties will not
 * be evaluated. Similarly, for panels no child marks will be rendered.
 *
 * @type boolean
 * @name pv.Mark.prototype.visible
 */

/**
 * The left margin; the distance, in pixels, between the left edge of the
 * enclosing panel and the left edge of this mark. Note that in some cases this
 * property may be redundant with the right property, or with the conjunction of
 * right and width.
 *
 * @type number
 * @name pv.Mark.prototype.left
 */

/**
 * The right margin; the distance, in pixels, between the right edge of the
 * enclosing panel and the right edge of this mark. Note that in some cases this
 * property may be redundant with the left property, or with the conjunction of
 * left and width.
 *
 * @type number
 * @name pv.Mark.prototype.right
 */

/**
 * The top margin; the distance, in pixels, between the top edge of the
 * enclosing panel and the top edge of this mark. Note that in some cases this
 * property may be redundant with the bottom property, or with the conjunction
 * of bottom and height.
 *
 * @type number
 * @name pv.Mark.prototype.top
 */

/**
 * The bottom margin; the distance, in pixels, between the bottom edge of the
 * enclosing panel and the bottom edge of this mark. Note that in some cases
 * this property may be redundant with the top property, or with the conjunction
 * of top and height.
 *
 * @type number
 * @name pv.Mark.prototype.bottom
 */

/**
 * The cursor property; corresponds to the CSS cursor property. This is
 * typically used in conjunction with event handlers to indicate interactivity.
 *
 * @type string
 * @name pv.Mark.prototype.cursor
 * @see <a href="http://www.w3.org/TR/CSS2/ui.html#propdef-cursor">CSS2 cursor</a>
 */

/**
 * The title property; corresponds to the HTML/SVG title property, allowing the
 * general of simple plain text tooltips.
 *
 * @type string
 * @name pv.Mark.prototype.title
 */

/**
 * The reverse property; a boolean determining whether marks are ordered from
 * front-to-back or back-to-front. SVG does not support explicit z-ordering;
 * shapes are rendered in the order they appear. Thus, by default, marks are
 * rendered in data order. Setting the reverse property to false reverses the
 * order in which they are rendered; however, the properties are still evaluated
 * (i.e., built) in forward order.
 *
 * @type boolean
 * @name pv.Mark.prototype.reverse
 */

/**
 * Default properties for all mark types. By default, the data array is the
 * parent data as a single-element array; if the data property is not specified,
 * this causes each mark to be instantiated as a singleton with the parents
 * datum. The visible property is true by default, and the reverse property is
 * false.
 *
 * @type pv.Mark
 */
pv.Mark.prototype.defaults = new pv.Mark()
    .data(function(d) { return [d]; })
    .visible(true)
    .reverse(false)
    .cursor("")
    .title("");

/* Private categorical colors for default fill & stroke styles. */
var defaultFillStyle = pv.Colors.category20().by(pv.parent),
    defaultStrokeStyle = pv.Colors.category10().by(pv.parent);

/**
 * Sets the prototype of this mark to the specified mark. Any properties not
 * defined on this mark may be inherited from the specified prototype mark, or
 * its prototype, and so on. The prototype mark need not be the same type of
 * mark as this mark. (Note that for inheritance to be useful, properties with
 * the same name on different mark types should have equivalent meaning.)
 *
 * @param {pv.Mark} proto the new prototype.
 * @return {pv.Mark} this mark.
 * @see #add
 */
pv.Mark.prototype.extend = function(proto) {
  this.proto = proto;
  return this;
};

/**
 * Adds a new mark of the specified type to the enclosing parent panel, whilst
 * simultaneously setting the prototype of the new mark to be this mark.
 *
 * @param {function} type the type of mark to add; a constructor, such as
 * <tt>pv.Bar</tt>.
 * @return {pv.Mark} the new mark.
 * @see #extend
 */
pv.Mark.prototype.add = function(type) {
  return this.parent.add(type).extend(this);
};

/**
 * Defines a local variable on this mark. Local variables are initialized once
 * per mark (i.e., per parent panel instance), and can be used to store local
 * state for the mark. Here are a few reasons you might want to use
 * <tt>def</tt>:
 *
 * <p>1. To store local state. For example, say you were visualizing employment
 * statistics, and your root panel had an array of occupations. In a child
 * panel, you might want to initialize a local scale, and reference it from a
 * property function:
 *
 * <pre>.def("y", function(d) pv.Scale.linear(0, pv.max(d.values)).range(0, h))
 * .height(function(d) this.y()(d))</pre>
 *
 * In this example, <tt>this.y()</tt> returns the defined local scale. We then
 * invoke the scale function, passing in the datum, to compute the height.  Note
 * that defs are similar to fixed properties: they are only evaluated once per
 * parent panel, and <tt>this.y()</tt> returns a function, rather than
 * automatically evaluating this function as a property.
 *
 * <p>2. To store temporary state for interaction. Say you have an array of
 * bars, and you want to color the bar differently if the mouse is over it. Use
 * <tt>def</tt> to define a local variable, and event handlers to override this
 * variable interactively:
 *
 * <pre>.def("i", -1)
 * .event("mouseover", function() this.i(this.index))
 * .event("mouseout", function() this.i(-1))
 * .fillStyle(function() this.i() == this.index ? "red" : "blue")</pre>
 *
 * Notice that <tt>this.i()</tt> can be used both to set the value of <i>i</i>
 * (when an argument is specified), and to get the value of <i>i</i> (when no
 * arguments are specified). In this way, it's like other property methods.
 *
 * <p>3. To specify fixed properties efficiently. Sometimes, the value of a
 * property may be locally a constant, but dependent on parent panel data which
 * is variable. In this scenario, you can use <tt>def</tt> to define a property;
 * it will only get computed once per mark, rather than once per datum.
 *
 * @param {string} name the name of the local variable.
 * @param {function} [value] an optional initializer; may be a constant or a
 * function.
 */
pv.Mark.prototype.def = function(name, value) {
  this.$properties.push({
      name: name,
      type: (typeof value == "function") ? 1 : 0,
      value: value
    });
  return this;
};

/**
 * Returns an anchor with the specified name. While anchor names are typically
 * constants, the anchor name is a true property, which means you can specify a
 * function to compute the anchor name dynamically. See the
 * {@link pv.Anchor#name} property for details.
 *
 * @param {string} name the anchor name; either a string or a property function.
 * @returns {pv.Anchor} the new anchor.
 */
pv.Mark.prototype.anchor = function(name) {
  var anchor = new pv.Anchor().extend(this).name(name);
  anchor.parent = this.parent;
  return anchor;
};

/**
 * Returns the anchor target of this mark, if it is derived from an anchor;
 * otherwise returns null. For example, if a label is derived from a bar anchor,
 *
 * <pre>bar.anchor("top").add(pv.Label);</pre>
 *
 * then property functions on the label can refer to the bar via the
 * <tt>anchorTarget</tt> method. This method is also useful for mark types
 * defining properties on custom anchors.
 *
 * @returns {pv.Mark} the anchor target of this mark; possibly null.
 */
pv.Mark.prototype.anchorTarget = function() {
  var target = this;
  while (!(target instanceof pv.Anchor)) {
    target = target.proto;
    if (!target) return null;
  }
  return target.proto;
};

/**
 * Returns the first instance of this mark in the scene graph. This method can
 * only be called when the mark is bound to the scene graph (for example, from
 * an event handler, or within a property function).
 *
 * @returns a node in the scene graph.
 */
pv.Mark.prototype.first = function() {
  return this.scene[0];
};

/**
 * Returns the last instance of this mark in the scene graph. This method can
 * only be called when the mark is bound to the scene graph (for example, from
 * an event handler, or within a property function). In addition, note that mark
 * instances are built sequentially, so the last instance of this mark may not
 * yet be constructed.
 *
 * @returns a node in the scene graph.
 */
pv.Mark.prototype.last = function() {
  return this.scene[this.scene.length - 1];
};

/**
 * Returns the previous instance of this mark in the scene graph, or null if
 * this is the first instance.
 *
 * @returns a node in the scene graph, or null.
 */
pv.Mark.prototype.sibling = function() {
  return (this.index == 0) ? null : this.scene[this.index - 1];
};

/**
 * Returns the current instance in the scene graph of this mark, in the previous
 * instance of the enclosing parent panel. May return null if this instance
 * could not be found. See the {@link pv.Layout.stack} function for an example
 * property function using cousin.
 *
 * @see pv.Layout.stack
 * @returns a node in the scene graph, or null.
 */
pv.Mark.prototype.cousin = function() {
  var p = this.parent, s = p && p.sibling();
  return (s && s.children) ? s.children[this.childIndex][this.index] : null;
};

/**
 * Renders this mark, including recursively rendering all child marks if this is
 * a panel.
 */
pv.Mark.prototype.render = function() {
  /*
   * Rendering consists of three phases: bind, build and update. The update
   * phase is decoupled to allow different rendering engines.
   *
   * In the bind phase, inherited property definitions are cached so they do not
   * need to be queried during build. In the build phase, properties are
   * evaluated, and the scene graph is generated. In the update phase, the scene
   * is rendered by creating and updating elements and attributes in the SVG
   * image. No properties are evaluated during the update phase; instead the
   * values computed previously in the build phase are simply translated into
   * SVG.
   */
  this.bind();
  this.build();
  pv.Scene.updateAll(this.scene);
};

/** @private Computes the root data stack for the specified mark. */
function argv(mark) {
  var stack = [];
  while (mark) {
    stack.push(mark.scene[mark.index].data);
    mark = mark.parent;
  }
  return stack;
}

/** @private TODO */
pv.Mark.prototype.bind = function() {
  var seen = {}, types = [[], [], [], []], data, visible;

  /** TODO */
  function bind(mark) {
    do {
      var properties = mark.$properties;
      for (var i = properties.length - 1; i >= 0 ; i--) {
        var p = properties[i];
        if (!(p.name in seen)) {
          seen[p.name] = 1;
          switch (p.name) {
            case "data": data = p; break;
            case "visible": visible = p; break;
            default: types[p.type].push(p); break;
          }
        }
      }
    } while (mark = mark.proto);
  }

  /** TODO */
  function def(name) {
    return function(v) {
      var defs = this.scene.defs;
      if (arguments.length) {
        if (v == undefined) {
          delete defs.locked[name];
        } else {
          defs.locked[name] = true;
        }
        defs.values[name] = v;
        return this;
      } else {
        return defs.values[name];
      }
    };
  }

  /* Scan the proto chain for all defined properties. */
  bind(this);
  bind(this.defaults);
  types[1].reverse();
  types[3].reverse();

  /* Any undefined properties are null. */
  var mark = this;
  do for (var name in mark.properties) {
    if (!(name in seen)) {
      seen[name] = 1;
      types[2].push({name: name, type: 2, value: null});
    }
  } while (mark = mark.proto);

  /* Define setter-getter for inherited defs. */
  var defs = types[0].concat(types[1]);
  for (var i = 0; i < defs.length; i++) {
    var d = defs[i];
    this[d.name] = def(d.name);
  }

  /* Setup binds to evaluate constants before functions. */
  this.binds = {
    data: data,
    visible: visible,
    defs: defs,
    properties: pv.blend(types)
  };
};

/**
 * @private Evaluates properties and computes implied properties. Properties are
 * stored in the {@link #scene} array for each instance of this mark.
 *
 * <p>As marks are built recursively, the {@link #index} property is updated to
 * match the current index into the data array for each mark. Note that the
 * index property is only set for the mark currently being built and its
 * enclosing parent panels. The index property for other marks is unset, but is
 * inherited from the global <tt>Mark</tt> class prototype. This allows mark
 * properties to refer to properties on other marks <i>in the same panel</i>
 * conveniently; however, in general it is better to reference mark instances
 * specifically through the scene graph rather than depending on the magical
 * behavior of {@link #index}.
 *
 * <p>The root scene array has a special property, <tt>data</tt>, which stores
 * the current data stack. The first element in this stack is the current datum,
 * followed by the datum of the enclosing parent panel, and so on. The data
 * stack should not be accessed directly; instead, property functions are passed
 * the current data stack as arguments.
 *
 * <p>The evaluation of the <tt>data</tt> and <tt>visible</tt> properties is
 * special. The <tt>data</tt> property is evaluated first; unlike the other
 * properties, the data stack is from the parent panel, rather than the current
 * mark, since the data is not defined until the data property is evaluated.
 * The <tt>visisble</tt> property is subsequently evaluated for each instance;
 * only if true will the {@link #buildInstance} method be called, evaluating
 * other properties and recursively building the scene graph.
 *
 * <p>If this mark is being re-built, any old instances of this mark that no
 * longer exist (because the new data array contains fewer elements) will be
 * cleared using {@link #clearInstance}.
 *
 * @param parent the instance of the parent panel from the scene graph.
 */
pv.Mark.prototype.build = function() {
  var scene = this.scene;
  if (!scene) {
    scene = this.scene = [];
    scene.mark = this;
    scene.type = this.type;
    scene.childIndex = this.childIndex;
    if (this.parent) {
      scene.parent = this.parent.scene;
      scene.parentIndex = this.parent.index;
    }
  }

  /* Set the data stack. */
  var stack = this.root.scene.data;
  if (!stack) this.root.scene.data = stack = argv(this.parent);

  /* Evaluate defs. */
  if (this.binds.defs.length) {
    var defs = scene.defs;
    if (!defs) scene.defs = defs = {values: {}, locked: {}};
    for (var i = 0; i < this.binds.defs.length; i++) {
      var d = this.binds.defs[i];
      if (!(d.name in defs.locked)) {
        var v = d.value;
        if (d.type == 1) {
          property = d.name;
          v = v.apply(this, stack);
        }
        defs.values[d.name] = v;
      }
    }
  }

  /* Evaluate special data property. */
  var data = this.binds.data;
  switch (data.type) {
    case 0: case 1: data = defs.values.data; break;
    case 2: data = data.value; break;
    case 3: {
      property = "data";
      data = data.value.apply(this, stack);
      break;
    }
  }

  /* Create, update and delete scene nodes. */
  stack.unshift(null);
  scene.length = data.length;
  for (var i = 0; i < data.length; i++) {
    pv.Mark.prototype.index = this.index = i;
    var s = scene[i];
    if (!s) scene[i] = s = {};
    s.data = stack[0] = data[i];

    /* Evaluate special visible property. */
    var visible = this.binds.visible;
    switch (visible.type) {
      case 0: case 1: visible = defs.values.visible; break;
      case 2: visible = visible.value; break;
      case 3: {
        property = "visible";
        visible = visible.value.apply(this, stack);
        break;
      }
    }

    if (s.visible = visible) this.buildInstance(s);
  }
  stack.shift();
  delete this.index;
  pv.Mark.prototype.index = -1;
  if (!this.parent) scene.data = null;

  return this;
};

/**
 * @private Evaluates the specified array of properties for the specified
 * instance <tt>s</tt> in the scene graph.
 *
 * @param s a node in the scene graph; the instance of the mark to build.
 * @param properties an array of properties.
 */
pv.Mark.prototype.buildProperties = function(s, properties) {
  for (var i = 0, n = properties.length; i < n; i++) {
    var p = properties[i], v = p.value;
    switch (p.type) {
      case 0: case 1: v = this.scene.defs.values[p.name]; break;
      case 3: {
        property = p.name;
        v = v.apply(this, this.root.scene.data);
        break;
      }
    }
    s[p.name] = v;
  }
};

/**
 * @private Evaluates all of the properties for this mark for the specified
 * instance <tt>s</tt> in the scene graph. The set of properties to evaluate is
 * retrieved from the {@link #properties} array for this mark type (see {@link
 * #type}).  After these properties are evaluated, any <b>implied</b> properties
 * may be computed by the mark and set on the scene graph; see
 * {@link #buildImplied}.
 *
 * <p>For panels, this method recursively builds the scene graph for all child
 * marks as well. In general, this method should not need to be overridden by
 * concrete mark types.
 *
 * @param s a node in the scene graph; the instance of the mark to build.
 */
pv.Mark.prototype.buildInstance = function(s) {
  this.buildProperties(s, this.binds.properties);
  this.buildImplied(s);
};

/**
 * @private Computes the implied properties for this mark for the specified
 * instance <tt>s</tt> in the scene graph. Implied properties are those with
 * dependencies on multiple other properties; for example, the width property
 * may be implied if the left and right properties are set. This method can be
 * overridden by concrete mark types to define new implied properties, if
 * necessary.
 *
 * @param s a node in the scene graph; the instance of the mark to build.
 */
pv.Mark.prototype.buildImplied = function(s) {
  var l = s.left;
  var r = s.right;
  var t = s.top;
  var b = s.bottom;

  /* Assume width and height are zero if not supported by this mark type. */
  var p = this.properties;
  var w = p.width ? s.width : 0;
  var h = p.height ? s.height : 0;

  /* Compute implied width, right and left. */
  var width = this.parent ? this.parent.width() : (w + l + r);
  if (w == null) {
    w = width - (r = r || 0) - (l = l || 0);
  } else if (r == null) {
    r = width - w - (l = l || 0);
  } else if (l == null) {
    l = width - w - (r = r || 0);
  }

  /* Compute implied height, bottom and top. */
  var height = this.parent ? this.parent.height() : (h + t + b);
  if (h == null) {
    h = height - (t = t || 0) - (b = b || 0);
  } else if (b == null) {
    b = height - h - (t = t || 0);
  } else if (t == null) {
    t = height - h - (b = b || 0);
  }

  s.left = l;
  s.right = r;
  s.top = t;
  s.bottom = b;

  /* Only set width and height if they are supported by this mark type. */
  if (p.width) s.width = w;
  if (p.height) s.height = h;
};

/**
 * @private The name of the property being evaluated, for so-called "smart"
 * functions that change behavior depending on which property is being
 * evaluated. This functionality is somewhat magical, so for now, this feature
 * is not exposed outside the library.
 *
 * @type string
 */
var property;

/** @private The current mouse location. */
var pageX = 0, pageY = 0;
pv.listen(window, "mousemove", function(e) { pageX = e.pageX; pageY = e.pageY; });

/**
 * Returns the current location of the mouse (cursor) relative to this mark's
 * parent. The <i>x</i> coordinate corresponds to the left margin, while the
 * <i>y</i> coordinate corresponds to the top margin.
 *
 * @returns {pv.Vector} the mouse location.
 */
pv.Mark.prototype.mouse = function() {
  var x = 0, y = 0, mark = (this instanceof pv.Panel) ? this : this.parent;
  do {
    x += mark.left();
    y += mark.top();
  } while (mark = mark.parent);
  var node = this.root.canvas();
  do {
    x += node.offsetLeft;
    y += node.offsetTop;
  } while (node = node.offsetParent);
  return pv.vector(pageX - x, pageY - y);
};

/**
 * Registers an event handler for the specified event type with this mark. When
 * an event of the specified type is triggered, the specified handler will be
 * invoked. The handler is invoked in a similar method to property functions:
 * the context is <tt>this</tt> mark instance, and the arguments are the full
 * data stack. Event handlers can use property methods to manipulate the display
 * properties of the mark:
 *
 * <pre>m.event("click", function() this.fillStyle("red"));</pre>
 *
 * Alternatively, the external data can be manipulated and the visualization
 * redrawn:
 *
 * <pre>m.event("click", function(d) {
 *     data = all.filter(function(k) k.name == d);
 *     vis.render();
 *   });</pre>
 *
 * The return value of the event handler determines which mark gets re-rendered.
 * Use defs ({@link #def}) to set temporary state from event handlers.
 *
 * <p>The complete set of event types is defined by SVG; see the reference
 * below. The set of supported event types is:<ul>
 *
 * <li>click
 * <li>mousedown
 * <li>mouseup
 * <li>mouseover
 * <li>mousemove
 * <li>mouseout
 *
 * </ul>Since Protovis does not specify any concept of focus, it does not
 * support key events; these should be handled outside the visualization using
 * standard JavaScript. In the future, support for interaction may be extended
 * to support additional event types, particularly those most relevant to
 * interactive visualization, such as selection.
 *
 * <p>TODO In the current implementation, event handlers are not inherited from
 * prototype marks. They must be defined explicitly on each interactive mark. In
 * addition, only one event handler for a given event type can be defined; when
 * specifying multiple event handlers for the same type, only the last one will
 * be used.
 *
 * @see <a href="http://www.w3.org/TR/SVGTiny12/interact.html#SVGEvents">SVG events</a>
 * @param {string} type the event type.
 * @param {function} handler the event handler.
 * @returns {pv.Mark} this.
 */
pv.Mark.prototype.event = function(type, handler) {
  if (!this.$handlers) this.$handlers = {};
  this.$handlers[type] = handler;
  return this;
};

/** @private TODO */
pv.Mark.prototype.dispatch = function(type, scenes, index) {
  var l = this.$handlers && this.$handlers[type];
  if (!l) {
    if (this.parent) {
      this.parent.dispatch(type, scenes.parent, scenes.parentIndex);
    }
    return;
  }
  try {

    /* Setup the scene stack. */
    var mark = this;
    do {
      mark.index = index;
      mark.scene = scenes;
      index = scenes.parentIndex;
      scenes = scenes.parent;
    } while (mark = mark.parent);

    /* Execute the event listener. */
    try {
      mark = l.apply(this, this.root.scene.data = argv(this));
    } finally {
      this.root.scene.data = null;
    }

    /* Update the display. TODO dirtying. */
    if (mark instanceof pv.Mark) mark.render();

  } finally {

    /* Restore the scene stack. */
    var mark = this;
    do {
      if (mark.parent) delete mark.scene;
      delete mark.index;
    } while (mark = mark.parent);
  }
};
