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
define([
], function() {
  return {
    autocompleteMatcher : {
      toEqualAutocompleteValues : function() {
        return {
          compare: function(actualItems, expectedValues) {
            var itemIndex = {};

            if (actualItems.length !== expectedValues.length) {
              return { pass: false };
            }
            $.each(actualItems, function(i, item) {
              itemIndex[item.value] = true;
            });

            for (var i = 0; i < expectedValues.length; i++) {
              if (! itemIndex[expectedValues[i]]) {
                return { pass: false };
              }
            }
            return { pass: true };
          }
        }
      }
    }
  }
});