/*! knockout-secure-binding - v0.5.5 - 2016-04-03
 *  https://github.com/brianmhunt/knockout-secure-binding
 *  Copyright (c) 2013 - 2016 Brian M Hunt; License: MIT */
;(function(factory) {
    //AMD
    if (typeof define === "function" && define.amd) {
        define(["knockout", "exports"], factory);
        //normal script tag
    } else {
        factory(ko);
    }
}(function(ko, exports, undefined) {
  var Identifier, Expression, Parser, Node;

  function value_of(item) {
    if (item instanceof Identifier || item instanceof Expression) {
      return item.get_value();
    }
    return item;
  }

  // We re-use the cache/parsing from the original binding provider,
  // in nodeParamsToObject (ala. getComponentParamsFromCustomElement)
  var originalBindingProviderInstance = new ko.bindingProvider();

  // The following are also in ko.*, but not exposed.
  function _object_map(source, mapping) {
    // ko.utils.objectMap
    if (!source) {
      return source;
    }
    var target = {};
    for (var prop in source) {
      if (source.hasOwnProperty(prop)) {
        target[prop] = mapping(source[prop], prop, source);
      }
    }
    return target;
  }

  // ko.virtualElements.virtualNodeBindingValue
  var commentNodesHaveTextProperty = document && document.createComment("test").text === "<!--test-->";
  var startCommentRegex = commentNodesHaveTextProperty ? /^<!--\s*ko(?:\s+([\s\S]+))?\s*-->$/ : /^\s*ko(?:\s+([\s\S]+))?\s*$/;

  function _virtualNodeBindingValue(node) {
    var regexMatch = (commentNodesHaveTextProperty ? node.text : node.nodeValue).match(startCommentRegex);
    return regexMatch ? regexMatch[1] : null;
  }



Identifier = (function () {
  function Identifier(parser, token, dereferences) {
    this.token = token;
    this.dereferences = dereferences;
    this.parser = parser;
  }

  /**
   * Return the value of the given
   *
   * @param  {Object} parent  (optional) source of the identifier e.g. for
   *                          membership. e.g. `a.b`, one would pass `a` in as
   *                          the parent when calling lookup_value for `b`.
   * @return {Mixed}          The value of the token for this Identifier.
   */
  Identifier.prototype.lookup_value = function (parent) {
    var token = this.token,
        parser = this.parser,
        $context = parser.context,
        $data = $context.$data || {},
        globals = parser.globals || {};

    if (parent) {
      return value_of(parent)[token];
    }

    // short circuits
    switch (token) {
      case '$element': return parser.node;
      case '$context': return $context;
      case '$data': return $data;
      default:
    }

    return $data[token] || $context[token] || globals[token];
  };

  /**
   * Apply all () and [] functions on the identifier to the lhs value e.g.
   * a()[3] has deref functions that are essentially this:
   *     [_deref_call, _deref_this where this=3]
   *
   * @param  {mixed} value  Should be an object.
   * @return {mixed}        The dereferenced value.
   */
  Identifier.prototype.dereference = function (value) {
    var member,
        refs = this.dereferences || [],
        parser = this.parser,
        $context = parser.context || {},
        $data = $context.$data || {},
        self = { // top-level `this` in function calls
          $context: $context,
          $data: $data,
          globals: parser.globals || {},
          $element: parser.node
        },
        last_value,  // becomes `this` in function calls to object properties.
        i, n;

    for (i = 0, n = refs.length; i < n; ++i) {
      member = refs[i];
      if (member === true) {
        value = value.call(last_value || self);
        last_value = value;
      } else {
        last_value = value;
        value = value[value_of(member)];
      }
    }
    return value;
  };

  /**
   * Return the value as one would get it from the top-level i.e.
   * $data.token/$context.token/globals.token; this does not return intermediate
   * values on a chain of members i.e. $data.hello.there -- requesting the
   * Identifier('there').value will return $data/$context/globals.there.
   *
   * This will dereference using () or [arg] member.
   * @param  {object | Identifier | Expression} parent
   * @return {mixed}  Return the primitive or an accessor.
   */
  Identifier.prototype.get_value = function (parent) {
    return this.dereference(this.lookup_value(parent));
  };

  /**
   * Set the value of the Identifier.
   *
   * @param {Mixed} new_value The value that Identifier is to be set to.
   */
  Identifier.prototype.set_value = function (new_value) {
    var parser = this.parser,
        $context = parser.context,
        $data = $context.$data || {},
        globals = parser.globals || {},
        refs = this.dereferences || [],
        leaf = this.token,
        i, n, root;

    if (Object.hasOwnProperty.call($data, leaf)) {
      root = $data;
    } else if (Object.hasOwnProperty.call($context, leaf)) {
      root = $context;
    } else if (Object.hasOwnProperty.call(globals, leaf)) {
      root = globals;
    } else {
      throw new Error("Identifier::set_value -- " +
        "The property '" + leaf + "' does not exist " +
        "on the $data, $context, or globals.");
    }

    // Degenerate case. {$data|$context|global}[leaf] = something;
    n = refs.length;
    if (n === 0) {
      root[leaf] = new_value;
    }

    // First dereference is {$data|$context|global}[token].
    root = root[leaf];

    // We cannot use this.dereference because that gives the leaf; to evoke
    // the ES5 setter we have to call `obj[leaf] = new_value`
    for (i = 0; i < n - 1; ++i) {
      leaf = refs[i];
      if (leaf === true) {
        root = root();
      } else {
        root = root[value_of(leaf)];
      }
    }

    // We indicate that a dereference is a function when it is `true`.
    if (refs[i] === true) {
      throw new Error("Cannot assign a value to a function.");
    }

    // Call the setter for the leaf.
    root[value_of(refs[i])] = new_value;
  };

  return Identifier;
})();

/**
 * Determine if a character is a valid item in an identifier.
 * Note that we do not check whether the first item is a number, nor do we
 * support unicode identifiers here.
 *
 * See: http://docstore.mik.ua/orelly/webprog/jscript/ch02_07.htm
 * @param  {String}  ch  The character
 * @return {Boolean}     True if [A-Za-z0-9_]
 */
function is_identifier_char(ch) {
  return (ch >= 'A' && ch <= 'Z') ||
         (ch >= 'a' && ch <= 'z') ||
         (ch >= '0' && ch <= 9) ||
          ch === '_' || ch === '$';
}


Node = (function () {
  function Node(lhs, op, rhs) {
    this.lhs = lhs;
    this.op = op;
    this.rhs = rhs;
  }

  var operators =  {
    // unary
    '!': function not(a, b) { return !b; },
    '!!': function notnot(a, b) { return !!b; },
    // mul/div
    '*': function mul(a, b) { return a * b; },
    '/': function div(a, b) { return a / b; },
    '%': function mod(a, b) { return a % b; },
    // sub/add
    '+': function add(a, b) { return a + b; },
    '-': function sub(a, b) { return a - b; },
    // relational
    '<': function lt(a, b) { return a < b; },
    '<=': function le(a, b) { return a <= b; },
    '>': function gt(a, b) { return a > b; },
    '>=': function ge(a, b) { return a >= b; },
    //    TODO: 'in': function (a, b) { return a in b; },
    //    TODO: 'instanceof': function (a, b) { return a instanceof b; },
    // equality
    '==': function equal(a, b) { return a === b; },
    '!=': function ne(a, b) { return a !== b; },
    '===': function sequal(a, b) { return a === b; },
    '!==': function sne(a, b) { return a !== b; },
    // bitwise
    '&': function bit_and(a, b) { return a & b; },
    '^': function xor(a, b) { return a ^ b; },
    '|': function bit_or(a, b) { return a | b; },
    // logic
    '&&': function logic_and(a, b) { return a && b; },
    '||': function logic_or(a, b) { return a || b; },
  };

  /* In order of precedence, see:
  https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Operator_Precedence#Table
  */
    // logical not
  operators['!'].precedence = 4;
  operators['!!'].precedence = 4; // explicit double-negative
    // multiply/divide/mod
  operators['*'].precedence = 5;
  operators['/'].precedence = 5;
  operators['%'].precedence = 5;
    // add/sub
  operators['+'].precedence = 6;
  operators['-'].precedence = 6;
    // relational
  operators['<'].precedence = 8;
  operators['<='].precedence = 8;
  operators['>'].precedence = 8;
  operators['>='].precedence = 8;
  // operators['in'].precedence = 8;
  // operators['instanceof'].precedence = 8;
    // equality
  operators['=='].precedence = 9;
  operators['!='].precedence = 9;
  operators['==='].precedence = 9;
  operators['!=='].precedence = 9;
    // bitwise
  operators['&'].precedence = 10;
  operators['^'].precedence = 11;
  operators['|'].precedence = 12;
    // logic
  operators['&&'].precedence = 13;
  operators['||'].precedence = 14;

  Node.operators = operators;


  Node.prototype.get_leaf_value = function (leaf, member_of) {
    if (typeof(leaf) === 'function') {
      // Expressions on observables are nonsensical, so we unwrap any
      // function values (e.g. identifiers).
      return ko.unwrap(leaf());
    }

    // primitives
    if (typeof(leaf) !== 'object') {
      return member_of ? member_of[leaf] : leaf;
    }

    // Identifiers and Expressions
    if (leaf instanceof Identifier || leaf instanceof Expression) {
      // lhs is passed in as the parent of the leaf. It will be defined in
      // cases like a.b.c as 'a' for 'b' then as 'b' for 'c'.
      return ko.unwrap(leaf.get_value(member_of));
    }

    if (leaf instanceof Node) {
      return leaf.get_node_value(member_of);
    }

    throw new Error("Invalid type of leaf node: " + leaf);
  };

  /**
   * Return a function that calculates and returns an expression's value
   * when called.
   * @param  {array} ops  The operations to perform
   * @return {function}   The function that calculates the expression.
   *
   * Exported for testing.
   */
  Node.prototype.get_node_value = function () {
    return this.op(this.get_leaf_value(this.lhs),
                   this.get_leaf_value(this.rhs));
  };

  return Node;
})();

Expression = (function () {
  function Expression(nodes) {
    this.nodes = nodes;
    this.root = this.build_tree(nodes);
  }

  // Exports for testing.
  Expression.operators = Node.operators;
  Expression.Node = Node;

  /**
   *  Convert an array of nodes to an executable tree.
   *  @return {object} An object with a `lhs`, `rhs` and `op` key, corresponding
   *                      to the left hand side, right hand side, and
   *                      operation function.
   */
  Expression.prototype.build_tree = function (nodes) {
    var root,
        leaf,
        op,
        value;

    // console.log("build_tree", nodes.slice(0))

    // primer
    leaf = root = new Node(nodes.shift(), nodes.shift(), nodes.shift());

    while (nodes) {
      op = nodes.shift();
      value = nodes.shift();
      if (!op) {
        break;
      }
      if (op.precedence > root.op.precedence) {
        // rebase
        root = new Node(root, op, value);
        leaf = root;
      } else {
        leaf.rhs = new Node(leaf.rhs, op, value);
        leaf = leaf.rhs;
      }
    }
    // console.log("tree", root)
    return root;
  }; // build_tree

  Expression.prototype.get_value = function () {
    if (!this.root) {
      this.root = this.build_tree(this.nodes);
    }
    return this.root.get_node_value();
  };

  return Expression;
})();


/**
 * Originally based on (public domain):
 * https://github.com/douglascrockford/JSON-js/blob/master/json_parse.js
 */
/* jshint -W083 */
Parser = (function () {
  var escapee = {
    "'": "'",
    '"':  '"',
    '\\': '\\',
    '/':  '/',
    b:    '\b',
    f:    '\f',
    n:    '\n',
    r:    '\r',
    t:    '\t'
  },
    operators = Expression.operators;

  /**
   * Construct a new Parser instance with new Parser(node, context)
   * @param {Node} node    The DOM element from which we parsed the
   *                         content.
   * @param {object} context The Knockout context.
   * @param {object} globals An object containing any desired globals.
   */
  function Parser(node, context, globals) {
    this.node = node;
    this.context = context;
    this.globals = globals || {};
  }

  // exported for testing.
  Parser.Expression = Expression;
  Parser.Identifier = Identifier;
  Parser.Node = Node;

  Parser.prototype.white = function () {
    var ch = this.ch;
    while (ch && ch <= ' ') {
      ch = this.next();
    }
    return ch;
  };

  Parser.prototype.next = function (c) {
    if (c && c !== this.ch) {
      this.error("Expected '" + c + "' but got '" + this.ch + "'");
    }
    this.ch = this.text.charAt(this.at);
    this.at += 1;
    return this.ch;
  };

  Parser.prototype.error = function (m) {
      // console.trace()
      throw {
          name:    'SyntaxError',
          message: m,
          at:      this.at,
          text:    this.text
      };
  };

  Parser.prototype.name = function () {
    // A name of a binding
    var name = '';
    this.white();

    var ch = this.ch;

    while (ch) {
      if (ch === ':' || ch <= ' ' || ch === ',') {
          return name;
      }
      name += ch;
      ch = this.next();
    }

    return name;
  };

  Parser.prototype.number = function () {
    var number,
        string = '',
        ch = this.ch;

    if (ch === '-') {
      string = '-';
      ch = this.next('-');
    }
    while (ch >= '0' && ch <= '9') {
      string += ch;
      ch = this.next();
    }
    if (ch === '.') {
      string += '.';
      ch = this.next();
      while (ch && ch >= '0' && ch <= '9') {
        string += ch;
        ch = this.next();
      }
    }
    if (ch === 'e' || ch === 'E') {
      string += ch;
      ch = this.next();
      if (ch === '-' || ch === '+') {
        string += ch;
        ch = this.next();
      }
      while (ch >= '0' && ch <= '9') {
        string += ch;
        ch = this.next();
      }
    }
    number = +string;
    if (!isFinite(number)) {
      error("Bad number");
    } else {
      return number;
    }
  };

  /**
   * Add a property to 'object' that equals the given value.
   * @param  {Object} object The object to add the value to.
   * @param  {String} key    object[key] is set to the given value.
   * @param  {mixed}  value  The value, may be a primitive or a function. If a
   *                         function it is unwrapped as a property.
   */
  Parser.prototype.object_add_value = function (object, key, value) {
    if (value instanceof Identifier || value instanceof Expression) {
      Object.defineProperty(object, key, {
        get: function () {
          return value.get_value();
        },
        enumerable: true,
      });
    } else {
      // primitives
      object[key] = value;
    }
  };

  Parser.prototype.object = function () {
    var key,
        object = {},
        ch = this.ch;

    if (ch === '{') {
      this.next('{');
      ch = this.white();
      if (ch === '}') {
        ch = this.next('}');
        return object;
      }
      while (ch) {
        if (ch === '"' || ch === "'") {
          key = this.string();
        } else {
          key = this.name();
        }
        this.white();
        ch = this.next(':');
        if (Object.hasOwnProperty.call(object, key)) {
          this.error('Duplicate key "' + key + '"');
        }

        this.object_add_value(object, key, this.expression());

        ch = this.white();
        if (ch === '}') {
          ch = this.next('}');
          return object;
        }

        this.next(',');
        ch = this.white();
      }
    }
    this.error("Bad object");
  };


  /**
   * Read up to delim and return the string
   * @param  {string} delim The delimiter, either ' or "
   * @return {string}       The string read.
   */
  Parser.prototype.read_string = function (delim) {
    var string = '',
        hex,
        i,
        uffff,
        ch = this.next();

    while (ch) {
      if (ch === delim) {
        ch = this.next();
        return string;
      }
      if (ch === '\\') {
        ch = this.next();
        if (ch === 'u') {
          uffff = 0;
          for (i = 0; i < 4; i += 1) {
            hex = parseInt(ch = this.next(), 16);
            if (!isFinite(hex)) {
              break;
            }
            uffff = uffff * 16 + hex;
          }
          string += String.fromCharCode(uffff);
        } else if (typeof escapee[ch] === 'string') {
          string += escapee[ch];
        } else {
          break;
        }
      } else {
        string += ch;
      }
      ch = this.next();
    }

    this.error("Bad string");
  };

  Parser.prototype.string = function () {
    var ch = this.ch;
    if (ch === '"') {
      return this.read_string('"');
    } else if (ch === "'") {
      return this.read_string("'");
    }

    this.error("Bad string");
  };

  Parser.prototype.array = function () {
    var array = [],
        ch = this.ch;
    if (ch === '[') {
      ch = this.next('[');
      this.white();
      if (ch === ']') {
        ch = this.next(']');
        return array;
      }
      while (ch) {
        array.push(this.expression());
        ch = this.white();
        if (ch === ']') {
          ch = this.next(']');
          return array;
        }
        this.next(',');
        ch = this.white();
      }
    }
    this.error("Bad array");
  };

  Parser.prototype.value = function () {
    var ch;
    this.white();
    ch = this.ch;
    switch (ch) {
      case '{': return this.object();
      case '[': return this.array();
      case '"': case "'": return this.string();
      case '-': return this.number();
      default:
      return ch >= '0' && ch <= '9' ? this.number() : this.identifier();
    }
  };

  /**
   * Get the function for the given operator.
   * A `.precedence` value is added to the function, with increasing
   * precedence having a higher number.
   * @return {function} The function that performs the infix operation
   */
  Parser.prototype.operator = function () {
    var op = '',
        op_fn,
        ch = this.white();

    while (ch) {
      if (is_identifier_char(ch) || ch <= ' ' || ch === '' ||
          ch === '"' || ch === "'" || ch === '{' || ch === '[' ||
          ch === '(') {
        break;
      }
      op += ch;
      ch = this.next();
    }

    if (op !== '') {
      op_fn = operators[op];

      if (!op_fn) {
        this.error("Bad operator: '" + op + "'.");
      }
    }

    return op_fn;
  };

  /**
   * Parse an expression – builds an operator tree, in something like
   * Shunting-Yard.
   *   See: http://en.wikipedia.org/wiki/Shunting-yard_algorithm
   *
   * @return {function}   A function that computes the value of the expression
   *                      when called or a primitive.
   */
  Parser.prototype.expression = function () {
    var root,
        nodes = [],
        node_value,
        ch = this.white();

    while (ch) {
      // unary prefix operators
      op = this.operator();
      if (op) {
        nodes.push(undefined);  // padding.
        nodes.push(op);
      }

      if (ch === '(') {
        this.next();
        nodes.push(this.expression());
        this.next(')');
      } else {
        node_value = this.value();
        nodes.push(node_value);
      }
      ch = this.white();
      if (ch === ':' || ch === '}' || ch === ',' || ch === ']' ||
          ch === ')' || ch === '') {
        break;
      }
      // infix operators
      op = this.operator();
      if (op) {
        nodes.push(op);
      }
      ch = this.white();
    }

    if (nodes.length === 0) {
      return undefined;
    }

    if (nodes.length === 1) {
      return nodes[0];
    }

    return new Expression(nodes);
  };

  /**
   * A dereference applies to an identifer, being either a function
   * call "()" or a membership lookup with square brackets "[member]".
   * @return {fn or undefined}  Dereference function to be applied to the
   *                            Identifier
   */
  Parser.prototype.dereference = function () {
    var member,
        ch = this.white();

    while (ch) {
      if (ch === '(') {
        // a() function call
        this.next('(');
        this.white();
        this.next(')');
        return true;  // in Identifier::dereference we check this
      } else if (ch === '[') {
        // a[x] membership
        this.next('[');
        member = this.expression();
        this.white();
        this.next(']');

        return member;
      } else if (ch === '.') {
        // a.x membership
        member = '';
        this.next('.');
        ch = this.white();
        while (ch) {
          if (!is_identifier_char(ch)) {
            break;
          }
          member += ch;
          ch = this.next();
        }
        return member;
      } else {
        break;
      }
      ch = this.white();
    }
    return;
  };

  Parser.prototype.identifier = function () {
    var token = '', ch, deref, dereferences = [];
    ch = this.white();
    while (ch) {
      if (!is_identifier_char(ch)) {
        break;
      }
      token += ch;
      ch = this.next();
    }
    switch (token) {
      case 'true': return true;
      case 'false': return false;
      case 'null': return null;
      // we use `void 0` because `undefined` can be redefined.
      case 'undefined': return void 0;
      default:
    }
    while (ch) {
      deref = this.dereference();
      if (deref !== undefined) {
        dereferences.push(deref);
      } else {
        break;
      }
    }
    return new Identifier(this, token, dereferences);
  };

  Parser.prototype.bindings = function () {
    var key,
        bindings = {},
        sep,
        ch = this.ch;

    while (ch) {
      key = this.name();
      sep = this.white();
      if (!sep || sep === ',') {
        if (sep) {
          ch = this.next(',');
        } else {
          ch = '';
        }
        // A "bare" binding e.g. "text"; substitute value of 'null'
        // so it becomes "text: null".
        bindings[key] = null;
      } else {
        ch = this.next(':');
        bindings[key] = this.expression();
        this.white();
        if (this.ch) {
          ch = this.next(',');
        } else {
          ch = '';
        }
      }
    }
    return bindings;
  };

/**
 * Convert result[name] from a value to a function (i.e. `valueAccessor()`)
 * @param  {object} result [Map of top-level names to values]
 * @return {object}        [Map of top-level names to functions]
 *
 * Accessors may be one of constAccessor (below), identifierAccessor or
 * expressionAccessor.
 */
  Parser.prototype.convert_to_accessors = function (result) {
    var propertyWriters = {};
    ko.utils.objectForEach(result, function (name, value) {
      if (value instanceof Identifier) {
        // use _twoWayBindings so the binding can update Identifier
        // See http://stackoverflow.com/questions/21580173
        result[name] = function () {
          return value.get_value();
        };

        if (ko.expressionRewriting._twoWayBindings[name]) {
          propertyWriters[name] = function(new_value) {
            value.set_value(new_value);
          };
        }
      } else if (value instanceof Expression) {
        result[name] = function expressionAccessor() {
          return value.get_value();
        };
      } else if (typeof(value) != 'function') {
        result[name] = function constAccessor() {
          return value;
        };
      }
    });

    if (Object.keys(propertyWriters).length > 0) {
      result._ko_property_writers = function () {
        return propertyWriters;
      };
    }

    return result;
  };

  /**
   * Get the bindings as name: accessor()
   * @param  {string} source The binding string to parse.
   * @return {object}        Map of name to accessor function.
   */
  Parser.prototype.parse = function (source) {
    this.text = (source || '').trim();
    this.at = 0;
    this.ch = ' ';

    if (!this.text) {
      return null;
    }

    var result = this.bindings();

    this.white();
    if (this.ch) {
      this.error("Syntax Error");
    }

    return this.convert_to_accessors(result);
  };

  return Parser;
})();


// See knockout/src/binding/bindingProvider.js

function secureBindingsProvider(options) {
    var existingProvider = new ko.bindingProvider();
    options = options || {};

    // override the attribute
    this.attribute = options.attribute || "data-sbind";

    // do we bind to the ko: virtual elements
    this.noVirtualElements = options.noVirtualElements || false;

    // set globals
    this.globals = options.globals || {};

    // the binding classes -- defaults to ko bindingsHandlers
    this.bindings = options.bindings || ko.bindingHandlers;

    // Cache the result of parsing binding strings.
    // TODO
    // this.cache = {};
}

function registerBindings(newBindings) {
    ko.utils.extend(this.bindings, newBindings);
}

function nodeHasBindings(node) {
    var value;
    if (node.nodeType === node.ELEMENT_NODE) {
        return node.getAttribute(this.attribute) ||
            (ko.components && ko.components.getComponentNameForNode(node));
    } else if (node.nodeType === node.COMMENT_NODE) {
        if (this.noVirtualElements) {
            return false;
        }
        value = ("" + node.nodeValue || node.text).trim();
        // See also: knockout/src/virtualElements.js
        return value.indexOf("ko ") === 0;
    }
}

function getBindingsString(node) {
    switch (node.nodeType) {
        case node.ELEMENT_NODE:
            return node.getAttribute(this.attribute);
        case node.COMMENT_NODE:
            return _virtualNodeBindingValue(node);
        default:
            return null;
    }
}

// This mirrors ko's native getComponentParamsFromCustomElement
function nodeParamsToObject(node, parser) {
    var accessors = parser.parse(node.getAttribute('params'));
    if (!accessors || Object.keys(accessors).length === 0) {
        return {$raw: {}};
    }
    var rawParamComputedValues = _object_map(accessors,
        function(paramValue, paramName) {
            return ko.computed(paramValue, null,
                { disposeWhenNodeIsRemoved: node }
            );
        }
    );
    var params = _object_map(rawParamComputedValues,
        function(paramValueComputed, paramName) {
            var paramValue = paramValueComputed.peek();
            if (!paramValueComputed.isActive()) {
                return paramValue;
            } else {
                return ko.computed({
                    read: function() {
                        return ko.unwrap(paramValueComputed());
                    },
                    write: ko.isWriteableObservable(paramValue) && function(value) {
                        paramValueComputed()(value);
                    },
                    disposeWhenNodeIsRemoved: node
                });
            }
        }
    );
    if (!params.hasOwnProperty('$raw')) {
        params.$raw = rawParamComputedValues;
    }
    return params;
}


// Note we do not seem to need both getBindings and getBindingAccessors; just
// the latter appears to suffice.
//
// Return the name/valueAccessor pairs.
// (undocumented replacement for getBindings)
// see https://github.com/knockout/knockout/pull/742
function getBindingAccessors(node, context) {
    var bindings = {},
        component_name,
        parser = new Parser(node, context, this.globals),
        sbind_string = this.getBindingsString(node);

    if (node.nodeType === node.ELEMENT_NODE && ko.components) {
        component_name = ko.components.getComponentNameForNode(node);
    }

    if (sbind_string) {
        bindings = parser.parse(sbind_string || '');
    }

    // emulate ko.components.addBindingsForCustomElement(bindings, node,
    //     context, true);
    if (component_name) {
        if (bindings.component) {
            throw new Error("Cannot use a component binding on custom elements");
        }
        var componentBindingValue = {
            'name': component_name,
            'params': nodeParamsToObject(node, parser),
        };
        bindings.component =  function() { return componentBindingValue; };
    }

    return bindings;
}


ko.utils.extend(secureBindingsProvider.prototype, {
    registerBindings: registerBindings,
    nodeHasBindings: nodeHasBindings,
    getBindingAccessors: getBindingAccessors,
    getBindingsString: getBindingsString,
    nodeParamsToObject: nodeParamsToObject,
    Parser: Parser
});
    if (!exports) {
        ko.secureBindingsProvider = secureBindingsProvider;
    }
    return secureBindingsProvider;
}));