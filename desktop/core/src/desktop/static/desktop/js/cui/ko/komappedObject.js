// Copyright (c) 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/komappedObject
 * @description The view model of base object.
 */

var komappingHelper = require('cloudera-ui/ko/komappingHelper');
var komapping = require('komapping');
var ko = require('knockout');
var _ = require('_');

/**
 * This behavior finds properties that have been mapped in KO model but that in
 * the data have been deleted. This is useful for merging updates to the model.
 * NOTE: this supports nested *mapped* objects; i.e. when you override 'create'
 * and return a sub-model which in turn is using komapping; in this case
 * komapping will map the nested object and save mapping metadata on the nested
 * object itself.
 * The case not supported is a nested object without an explicit 'create' mapping
 * override, because the komapping metadata is attached to the parent only.
 *
 * @private
 * @param {object} JS data
 * @param {object} KO viewmodel
 */
function removeOrphanedProperties(data, model) {
  if (!komapping.isMapped(model)) {
    return;
  }

  var mappedProperties = _.keys(model.__ko_mapping__.mappedProperties);
  var submodelProperties = [];
  _.each(mappedProperties, function(name) {
    if (_.isUndefined(model[name])) {
      // was declared in the mapping, but not found in the model
      return;
    }

    if (komapping.isMapped(model[name])) {
      // recursively mapped submodel
      submodelProperties.push(name);
    } else {
      // detect if property was removed in the updated data
      if (_.isUndefined(data[name])) {
        if (ko.isObservable(model[name])) {
          model[name](undefined);
        } else {
          model[name] = undefined;
        }
      }
    }
  });
  _.each(submodelProperties, function(name) {
    removeOrphanedProperties(data[name], ko.unwrap(model[name]));
  });
}

var komappedObject = {
  /**
   * Maps source data to a KO viewmodel.
   * Note the optional defaultValue in the viewmodel can be either a plain JS object or a
   * function generating the default data.
   * @param {object} data source data, if context.defaultValue available it's used as defaults
   * @param {object} context KO viewmodel
   * @param {object} [overrideMapping] overrides the mapping otherwise used by default: viewmodel.mapping
   */
  fromJS: function(data, context, overrideMapping) {
    var defaultValue = _.isFunction(context.defaultValue) ? context.defaultValue() : context.defaultValue;
    data = _.extend({}, defaultValue, data);
    komappingHelper.fromJS(data, overrideMapping || context.mapping, context);
  },

  /**
   * To be used when updating an already mapped KO view-model.
   * In addition to performing a KO 'merge' mapping this handles deleted properties:
   * the corresponding obsolete value in the model is updated with 'undefined'
   */
  mergeJS: function(data, context) {
    komapping.fromJS(data, context);
    removeOrphanedProperties(data, context);
  },

  /**
   * Map a member field to another view model using a specific constructor.
   * <code>
   * // Say the incoming raw data for the parent view model is:
   * {
   *   info: {...},
   *   children: [ {id: '...', ...}, {id: '...', ...} ]
   * }
   * // The parent view model's mapping function could look like:
   * ParentViewModel.prototype.mapping = {
   *   info: komappedObject.mapField(Info),
   *   children: komappedObject.mapField(ChildViewModel, 'id')
   * };
   * </code>
   *
   * @param {function} ConstructorFunc the constructor function to call
   * when mapping a particular field.
   * @param {string} [keyField] if present, data[keyField] will be used
   * as the identifier of this object when it is inside an observable array.
   */
  mapField: function(ConstructorFunc, keyField) {
    var result = {
      create: function(options) {
        return new ConstructorFunc(options.data);
      },
      update: function(options) {
        if (options.target) {
          options.target.fromJS(options.data);
        }

        return options.target;
      }
    };

    if (keyField) {
      // This allows objects to be identifiable in an observable array.
      // So they don't get destroyed and re-created.
      result.key = function(data) {
        // using unwrapObservable is very important, because
        // sometimes the data argument passed in is raw data,
        // sometimes the data argument passed in is an observable.
        return ko.utils.unwrapObservable(data[keyField]);
      };
    }

    return result;
  }
};

module.exports = komappedObject;
