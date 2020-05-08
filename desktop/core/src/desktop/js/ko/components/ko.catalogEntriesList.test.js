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
import { koSetup } from 'jest/koTestUtils';
import { NAME } from './ko.catalogEntriesList';

import 'ko/components/ko.inlineAutocomplete';
import 'ko/components/ko.fieldSamples';
import 'ko/components/ko.dropDown';

describe('ko.catalogEntriesList.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const element = await setup.renderComponent(NAME, {
      catalogEntry: {
        isField: () => true,
        isComplex: () => false,
        isDatabase: () => false,
        getChildren: () => $.Deferred().resolve([]),
        getSample: () => $.Deferred().reject(),
        getDialect: () => 'impala',
        loadNavigatorMetaForChildren: () => $.Deferred().reject(),
        loadOptimizerPopularityForChildren: () => $.Deferred().reject(),
        isTableOrView: () => false,
        isSource: () => false
      }
    });

    expect(element.innerHTML).toMatchSnapshot();
  });
});
