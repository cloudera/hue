// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import ko from 'knockout';

// https://stackoverflow.com/questions/19865364/knockoutjs-linking-value-from-a-input-to-a-datalist-value

ko.bindingHandlers.datalist = (function() {
  function getVal(rawItem, prop) {
    const item = ko.unwrap(rawItem);
    return item && prop ? ko.unwrap(item[prop]) : item;
  }

  function findItem(options, prop, ref) {
    return ko.utils.arrayFirst(options, item => {
      return ref === getVal(item, prop);
    });
  }

  return {
    init: function(element, valueAccessor, allBindingsAccessor) {
      const setup = valueAccessor(),
        textProperty = ko.unwrap(setup.optionsText),
        valueProperty = ko.unwrap(setup.optionsValue),
        dataItems = ko.unwrap(setup.options),
        myValue = setup.value,
        koValue = allBindingsAccessor().value,
        datalist = document.createElement('DATALIST');

      // create an associated <datalist> element
      datalist.id = element.getAttribute('list');
      document.body.appendChild(datalist);

      // when the value is changed, write to the associated myValue observable
      function onNewValue(newVal) {
        const setup = valueAccessor(),
          dataItems = ko.unwrap(setup.options),
          selectedItem = findItem(dataItems, textProperty, newVal),
          newValue = selectedItem ? getVal(selectedItem, valueProperty) : newVal;

        if (ko.isWriteableObservable(myValue)) {
          myValue(newValue);
        }
      }

      // listen for value changes
      // - either via KO's value binding (preferred) or the change event
      if (ko.isSubscribable(koValue)) {
        const onNewValueSubscription = koValue.subscribe(onNewValue);
        ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
          onNewValueSubscription.remove();
        });
      } else {
        const event = allBindingsAccessor().valueUpdate === 'afterkeydown' ? 'input' : 'change';
        ko.utils.registerEventHandler(element, event, function() {
          onNewValue(this.value);
        });
      }

      // init the element's value
      // - either via the myValue observable (preferred) or KO's value binding
      if (ko.isObservable(myValue) && myValue()) {
        const selectedItem = findItem(dataItems, valueProperty, myValue());
        element.value = selectedItem ? getVal(selectedItem, textProperty) : myValue();
      } else if (ko.isObservable(koValue) && koValue()) {
        onNewValue(koValue());
      }
    },
    update: function(element, valueAccessor) {
      const setup = valueAccessor(),
        datalist = element.list,
        dataItems = ko.unwrap(setup.options),
        textProperty = ko.unwrap(setup.optionsText);

      // rebuild list of options when an underlying observable changes
      datalist.innerHTML = '';
      ko.utils.arrayForEach(dataItems, item => {
        const option = document.createElement('OPTION');
        option.value = getVal(item, textProperty);
        datalist.appendChild(option);
      });
      ko.utils.triggerEvent(element, 'change');
    }
  };
})();
