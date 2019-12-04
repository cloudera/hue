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

import ApiHelper from 'api/apiHelper';
import { koSetup } from 'jest/koTestUtils';
import { NAME } from './ko.favoriteApp';

describe('ko.favoriteApp.js', () => {
  const setup = koSetup();

  it('should render non-favorite', async () => {
    const apiPromise = new Promise(resolve => {
      jest.spyOn(ApiHelper, 'fetchFavoriteApp').mockImplementation(async () => {
        resolve();
        return Promise.resolve({
          status: 0,
          data: {
            default_app: JSON.stringify({ app: 'bar' })
          }
        });
      });
    });
    const element = await setup.renderComponent(NAME, {
      app: 'foo'
    });

    await apiPromise;
    // await sleep(100);
    expect(element.innerHTML).toMatchSnapshot();
  });

  it('should render favorite', async () => {
    const apiPromise = new Promise(resolve => {
      jest.spyOn(ApiHelper, 'fetchFavoriteApp').mockImplementation(async () => {
        resolve();
        return Promise.resolve({
          status: 0,
          data: {
            default_app: JSON.stringify({ app: 'foo' })
          }
        });
      });
    });
    const element = await setup.renderComponent(NAME, {
      app: 'foo'
    });

    await apiPromise;
    // await sleep(100);
    expect(element.innerHTML).toMatchSnapshot();
  });
});
