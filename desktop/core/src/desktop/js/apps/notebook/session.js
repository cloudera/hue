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

import $ from 'jquery';
import ko from 'knockout';
import komapping from 'knockout.mapping';

class Session {
  constructor(vm, session) {
    const self = this;
    komapping.fromJS(session, {}, self);

    self.selectedSessionProperty = ko.observable('');

    self.restarting = ko.observable(false);

    if (!ko.isObservable(self.properties)) {
      self.properties = ko.observableArray();
    }

    self.availableNewProperties = ko.computed(() => {
      const addedIndex = {};
      $.each(self.properties(), (index, property) => {
        addedIndex[property.key] = true;
      });
      const result = $.grep(vm.availableSessionProperties(), property => {
        return !addedIndex[property.name];
      });
      return result;
    });
  }
}

export default Session;
