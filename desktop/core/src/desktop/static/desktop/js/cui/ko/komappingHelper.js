// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/komappingHelper
 * @description Provides helper functions to komapping and abstracts away any
 * references to komapping directly.
 */

var ko = require('knockout');
var komapping = require('komapping');
var $ = require('jquery');
var _ = require('_');

/**
 * A name value pair object.
 *
 * @param {string} value The value.
 * @param {string} name The name.
 */
var NVPair = function(value, name) {
  this.value = ko.observable(value || this.defaultValue);
  this.name = ko.observable(name || '');

  /**
   * Returns true if the object is valid.
   * This method can be overwritten.
   *
   * @return {boolean}
   */
  this.isValid = ko.computed(function() {
    return !_.isEmpty(this.name()) &&
      !_.isEmpty(this.value());
  }, this);

};

NVPair.prototype.defaultValue = '';

/**
 * A single value object.
 *
 * @param {string} value The value.
 */
var Value = function(value) {
  this.value = ko.observable(value || this.defaultValue);

  /**
   * Returns true if the object is valid.
   * This method can be overwritten.
   *
   * @return {boolean}
   */
  this.isValid = ko.computed(function() {
    return !_.isEmpty(this.value());
  }, this);
};

Value.prototype.defaultValue = '';

/**
 * Initializes a list to back an array of member fields as view models.
 * @param {object} viewModel The context view model object.
 * @param {string} listName The name of the backing list.
 * @param {function} ConstructorFunc The function to construct a new member.
 * The ConstructorFunc should work correctly when no arguments are given.
 */
var initializeBackingList = function(viewModel, listName, ConstructorFunc) {
  // Initializes a backing list.
  viewModel[listName] = ko.observableArray();

  // Adds a helper method to add entries to the list.
  viewModel[listName].insertAfter = _.bind(function(entry, element) {
    var index = 0;
    if (entry) {
      index = this[listName].indexOf(entry);
    }

    this[listName].splice(index + 1, 0, new ConstructorFunc());

    // After the item is added, focus on the first input element.
    $(element).closest('li').next().find('input').first().focus();
  }, viewModel);

  // Adds a helper method to remove entries from the list.
  viewModel[listName].removeItem = _.bind(function(entry, element) {
    // Find the element to focus on after removal.
    var $li = $(element).closest('li'), $elemToFocus;
    if ($li.next().length !== 0) {
      $elemToFocus = $li.next().find('button');
    } else if ($li.prev().length !== 0) {
      $elemToFocus = $li.prev().find('button');
    }

    // Remove the entry.
    this[listName].remove(entry);

    // After removal, focus on the new element.
    if ($elemToFocus) {
      $elemToFocus.first().focus();
    }
  }, viewModel);

  // Adds a helper method to check for validity.
  viewModel[listName].isValid = ko.computed(function() {
    return _.every(this[listName](), function(entry) {
      return entry.isValid();
    });
  }, viewModel);
};

/**
 * @typedef SerializeOptionsType
 * @property {boolean} [optional=false] forces presence of the field on output, writes 'null' if no value
 * @property {boolean} [emptyStringToNull=false] when true, any value === '' is converted to null on output
 * @property {SerializeOptionsType} [serializeOptions] for recursive models, options of a submodel
 */

/**
 * Further processing to customize serialization of the model to JS.
 * This will transform data according to options specified
 *
 * @see SerializeOptionsType
 * @example Given view-model 'var model'
 * model.serializeOptions: {
 *   userName: { optional: false, emptyStringToNull: true }
 * }
 */
function processSerializeOptions(data, options) {
  _.each(options, function(opt, key) {
    if (opt.serializeOptions && _.isObject(data[key])) {
      // recursively descend
      processSerializeOptions(data[key], opt.serializeOptions);
    }

    if (opt.emptyStringToNull && data[key] === '') {
      data[key] = null;
    }

    if (_.isUndefined(data[key]) && !opt.optional) {
      data[key] = null;
    }
  });
}

module.exports = {
  /**
   * Populates data into the viewModel object using komapping.
   *
   * @param {object} data The plain js object.
   * @param {object} mapping The komapping rules.
   * @param {object} viewModel The view model containing ko observables.
   */
  fromJS: function(data, mapping, viewModel) {
    try {
      komapping.fromJS(data, mapping || {}, viewModel);
    } catch (e) {
      console.error(e);
    }
  },

  /**
   * Converts a view model object into a plain js object.
   * Additionally support custom serialization options in the view-model:
   * performed when it finds a field 'serializeOptions' in the model.
   *
   * @param {object} viewModel The view model containing ko observables.
   * @return {object}
   * @see processSerializeOptions
   */
  toJS: function(viewModel) {
    var data = komapping.toJS(viewModel);
    if (viewModel.serializeOptions) {
      processSerializeOptions(data, viewModel.serializeOptions);
    }

    return data;
  },

  /**
   * Converts a view model object into a JSON string.
   *
   * @param {object} viewModel The view model containing ko observables.
   * @return {string}
   */
  toJSON: function(viewModel) {
    return komapping.toJSON(viewModel);
  },

  /**
   * Converts viewModel[paramName], a source map containing keys and values,
   * into a list of name value pairs as viewModel[listName].
   *
   * The list is easier to manipulate with using knockout.
   *
   * @param {object} viewModel The view model containing ko observables.
   * @param {string} paramName The name of the source object map.
   * @param {string} listName The name of the output list.
   * @param {object} paramValue The source object map. e.g. {
   *   key1: 'value1',
   *   key2: 'value2'
   * }
   * @example
   * var viewModel = {}, data = {
   *   name1: 'value1',
   *   name2: 'value2'
   * };
   *
   * komappingHelper.convertMapToListObservable(viewModel,
   *   'field', '_field', data);
   * // _field is now a ko array of NVPair.
   * viewModel._field()[0].name('newName1');
   * viewModel._field()[0].value('newValue1');
   *
   * // viewModel.toJS() now returns
   * {
   *   field: {
   *     newName1: 'newValue1',
   *     name2: 'value2'
   *   }
   * }
   */
  convertMapToListObservable: function(viewModel, paramName, listName,
                                       paramValue) {
    return this.convertObjectToListObservable(viewModel, paramName,
                                              listName, paramValue, NVPair);
  },

  /**
   * Converts viewModel[paramName], a source object map containing keys and
   * objects, into a list of objects, each constructed via the
   * ConstructorFunc function.
   *
   * The list is easier to manipulate with using knockout.
   *
   * @param {object} viewModel The view model containing ko observables.
   * @param {string} paramName The name of the source object map.
   * @param {string} listName The name of the output list.
   * @param {object} paramValue The source object map. e.g. {
   *   key1: { some object }
   *   key2: { some object }
   * }
   * @param {function} ConstructorFunc The function to construct the members.
   * This constructor should take one or two parameters
   * (object value, [string key]) and has an isValid() method, a name()
   * method that returns the key, a value() method that returns the value.
   * @example
   * var viewModel = {}, data = {
   *   name1: 'value1',
   *   name2: 'value2'
   * };
   *
   * komappingHelper.convertObjectToListObservable(viewModel,
   *   'field', '_field', data, NVPair);
   * // _field is now a ko array of NVPair.
   * viewModel._field()[0].name('newName1');
   * viewModel._field()[0].value('newValue1');
   *
   * // viewModel.toJS() now returns
   * {
   *   field: {
   *     newName1: 'newValue1',
   *     name2: 'value2'
   *   }
   * }
   */
  convertObjectToListObservable: function(viewModel, paramName, listName,
                                          paramValue, ConstructorFunc) {
    if (!ko.isObservable(viewModel[listName])) {
      initializeBackingList(viewModel, listName, ConstructorFunc);
    }

    /**
     * Replaces the original map with a dependency to the backing list.
     * komapping.toJS(viewModel) or komapping.toJS(parentViewModel) now
     * automatically picks up the latest state.
     * @private
     */
    viewModel[paramName] = ko.computed({
      /**
       * Returns an object containing name to objects. e.g. {
       *   key1: { some object },
       *   key2: { some object }
       * }
       * @return {object}
       * @private
       */
      read: function() {
        var result = {}, n, v;
        _.each(this[listName](), function(entry) {
          n = entry[ConstructorFunc.nameAccessor || 'name']();
          v = entry.value();

          // Skip any key values that are not defined.
          if (!_.isEmpty(n) && !_.isEmpty(v)) {
            // Skip any entries that are marked for removal.
            if (!_.isFunction(entry.isDeletingMode) || !entry.isDeletingMode()) {
              result[n] = v;
            }
          }
        });
        return result;
      },

      /**
       * Updates with a new object map.
       * @param {object} data The new object map.
       * @private
       */
      write: function(data) {
        // This allows clone to work without special handling.
        if (_.isObject(data)) {
          this[listName].valueWillMutate();
          this[listName].removeAll();

          _.each(data, function(v, k) {
            this[listName].push(new ConstructorFunc(v, k));
          }, this);
          this[listName].valueHasMutated();
        }
      }
    }, viewModel);

    // Performs initial conversion.
    viewModel[paramName](_.cloneDeep(paramValue));
  },

  /**
   * Converts viewModel[paramName], a string list into a Value array.
   *
   * The list is easier to manipulate with using knockout because
   * insertAfter and removeItem are added.
   *
   * @param {object} viewModel The view model containing ko observables.
   * @param {string} paramName The name of the source string list.
   * @param {string} listName The name of the output list. It should appear
   * in the ignore array of the viewModel's mapping object.
   * @param {string} paramValue The current comma separated value.
   * @example
   * var viewModel = {}, data = [
   *   'value1',
   *   'value2'
   * ];
   *
   * komappingHelper.convertListToListObservable(viewModel,
   *   'field', '_field', data);
   *
   * // _field is now a ko array of Value.
   * viewModel._field()[0].value('newValue1');
   *
   * // viewModel.toJS() now returns
   * {
   *   field: [
   *     'newValue1',
   *     'value2'
   *   ]
   * }
   */
  convertListToListObservable: function(viewModel, paramName, listName,
                                        paramValue) {
    if (!ko.isObservable(viewModel[listName])) {
      initializeBackingList(viewModel, listName, Value);
    }

    /**
     * Replaces the original list observable with a dependency to the list.
     * komapping.toJS(viewModel) or komapping.toJS(parentViewModel) now
     * automatically picks up the latest state.
     * @private
     */
    viewModel[paramName] = ko.computed({
      /**
       * Returns the new combined comma separated value.
       * @return {string}
       * @private
       */
      read: function() {
        var result = [];
        _.each(this[listName](), function(value) {
          result.push(value.value());
        });
        return result;
      },

      /**
       * Updates with a new string list.
       * @param {string[]} value The new string list.
       * @private
       */
      write: function(value) {
        // This allows clone to work without special handling.
        if (_.isArray(value)) {
          this[listName].valueWillMutate();
          this[listName].removeAll();

          _.each(value, function(v) {
            this[listName].push(new Value(v));
          }, this);
          this[listName].valueHasMutated();
        }
      }
    }, viewModel);

    // Performs initial conversion.
    viewModel[paramName](paramValue);
  },

  /**
   * Converts viewModel[paramName], an observable containing a string of
   * comma separated values into a list of strings as viewModel[listName].
   *
   * The list is much easier to manipulate with using knockout.
   *
   * @param {object} viewModel The view model containing ko observables.
   * @param {string} paramName The name of the source string observable.
   * @param {string} listName The name of the output list.
   * @param {string} paramValue The current comma separated value.
   * @param {string} [separator] The optional separator to use.
   * @example
   * var viewModel = {}, data = 'value1,value2';
   *
   * komappingHelper.convertStringToListObservable(viewModel,
   *   'field', '_field', data);
   *
   * // _field is now a ko array of Value.
   * viewModel._field()[0].value('newValue1');
   *
   * // viewModel.toJS() now returns
   * {
   *   field: 'newValue1,value2'
   * }
   */
  convertStringToListObservable: function(viewModel, paramName, listName,
                                          paramValue, separator) {
    separator = separator || ',';

    if (!ko.isObservable(viewModel[listName])) {
      initializeBackingList(viewModel, listName, Value);
    }

    /**
     * Replaces the original string observable with a dependency to the list.
     * komapping.toJS(viewModel) or komapping.toJS(parentViewModel) now
     * automatically picks up the latest state.
     * @private
     */
    viewModel[paramName] = ko.computed({
      /**
       * Returns the new combined comma separated value.
       * @return {string}
       * @private
       */
      read: function() {
        var result = [];
        _.each(this[listName](), function(value) {
          result.push(value.value());
        });
        return result.join(separator);
      },

      /**
       * Updates with a new comma separated value.
       * @param {string} value The new comma separated value.
       * @private
       */
      write: function(value) {
        // This allows clone to work without special handling.
        if (_.isString(value)) {
          this[listName].valueWillMutate();
          this[listName].removeAll();

          _.each(value.split(separator), function(v) {
            this[listName].push(new Value(v));
          }, this);
          this[listName].valueHasMutated();
        }
      }
    }, viewModel);

    // Performs initial conversion.
    viewModel[paramName](paramValue);
  },

  /**
   * @param {object} viewModel The model to change.
   * @param {string} paramName The attribute that is undefined if empty.
   * @param {*} paramValue The initial value.
   */
  optionalIfEmpty: function(viewModel, paramName, paramValue) {
    var internalName = '_' + paramName;

    // don't create another observable
    if (!ko.isObservable(viewModel[internalName])) {
      // save existing observable as an internal attribute
      viewModel[internalName] = viewModel[paramName];
    }

    viewModel[paramName] = ko.computed({
      read: function() {
        var result = this[internalName]();
        if (_.isString(result) && _.isEmpty(result)) {
          return undefined;
        }

        return result;
      },
      write: function(value) {
        this[internalName](value);
      }
    }, viewModel);

    // initialize the attribute if any custom behavior is defined
    viewModel[paramName](paramValue);
  }
};
