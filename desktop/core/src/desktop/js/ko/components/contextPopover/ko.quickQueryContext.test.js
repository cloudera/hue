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

import { koSetup } from 'jest/koTestUtils';
import { NAME } from './ko.quickQueryContext';
import * as hueConfig from 'utils/hueConfig';
import apiHelper from 'api/apiHelper';

import $ from 'jquery';

describe('ko.quickQueryContext.js', () => {
  const setup = koSetup();

  it('should render component', async () => {
    const connectorsSpy = jest
      .spyOn(hueConfig, 'filterEditorConnectors')
      .mockImplementation(() => [{ id: 'impala' }]);
    const computeSpy = jest
      .spyOn(apiHelper, 'fetchContextComputes')
      .mockImplementation(() => $.Deferred().resolve({}));
    const fetchContextNamespaces = jest
      .spyOn(apiHelper, 'fetchContextNamespaces')
      .mockImplementation(() => $.Deferred().resolve({}));

    const element = await setup.renderComponent(NAME, {});

    expect(connectorsSpy).toHaveBeenCalled();
    expect(computeSpy).toHaveBeenCalled();
    expect(fetchContextNamespaces).toHaveBeenCalled();

    expect(
      element.innerHTML.replace(/[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}/gi, 'uuid-uuid')
    ).toMatchSnapshot();

    connectorsSpy.mockRestore();
    connectorsSpy.mockClear();
  });
});
