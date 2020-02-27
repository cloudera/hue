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

import * as ko from 'knockout';

import { koSetup, waitForObservableChange } from 'jest/koTestUtils';
import { NAME } from './ko.linkSharing';
import ApiHelper, { LINK_SHARING_PERMS } from 'api/apiHelper';

describe('ko.linkSharing.js', () => {
  const setup = koSetup();

  let params;

  beforeEach(() => {
    params = {
      docDefinition: {
        uuid: 'some-uuid',
        perms: {
          read: {
            groups: [],
            users: []
          },
          write: {
            groups: [],
            users: []
          },
          link_write: false,
          link_read: false,
          link_sharing_on: false
        }
      }
    };
  });

  it('should render component deactivated', async () => {
    const element = await setup.renderComponent(NAME, params);

    expect(element.innerHTML).toMatchSnapshot();
  });

  it('should render component activated', async () => {
    params.docDefinition.perms.link_read = true;
    params.docDefinition.perms.link_sharing_on = true;
    const element = await setup.renderComponent(NAME, params);

    expect(element.innerHTML).toMatchSnapshot();
  });

  it('should activate sharing', async () => {
    let apiHelperCalled = false;
    jest.spyOn(ApiHelper, 'setLinkSharingPermsAsync').mockImplementation(async options => {
      expect(options.perm).toEqual(LINK_SHARING_PERMS.READ);
      apiHelperCalled = true;
      return Promise.resolve({
        status: 0,
        document: {
          uuid: 'some-uuid',
          perms: {
            link_write: false,
            link_read: true,
            link_sharing_on: true
          }
        }
      });
    });
    const element = await setup.renderComponent(NAME, params);

    // Activate should be visible
    expect(element.querySelector('[data-test="activate"]')).toBeTruthy();
    expect(element.querySelector('[data-test="deactivate"]')).toBeFalsy();
    const model = ko.dataFor(element.querySelector('[data-test="activate"]'));
    expect(model.perms().link_sharing_on).toBeFalsy();
    expect(apiHelperCalled).toBeFalsy();

    // Click activate
    element.querySelector('[data-test="activate"]').click();
    await waitForObservableChange(model.perms);

    // Deactivate should be visible
    expect(element.querySelector('[data-test="activate"]')).toBeFalsy();
    expect(element.querySelector('[data-test="deactivate"]')).toBeTruthy();
    expect(model.perms().link_sharing_on).toBeTruthy();
    expect(apiHelperCalled).toBeTruthy();
  });

  it('should deactivate sharing', async () => {
    let apiHelperCalled = false;
    jest.spyOn(ApiHelper, 'setLinkSharingPermsAsync').mockImplementation(async options => {
      expect(options.perm).toEqual(LINK_SHARING_PERMS.OFF);
      apiHelperCalled = true;
      return Promise.resolve({
        status: 0,
        document: {
          uuid: 'some-uuid',
          perms: {
            link_write: false,
            link_read: false,
            link_sharing_on: false
          }
        }
      });
    });
    params.docDefinition.perms.link_read = true;
    params.docDefinition.perms.link_sharing_on = true;
    const element = await setup.renderComponent(NAME, params);

    // Deactivate should be visible
    expect(element.querySelector('[data-test="activate"]')).toBeFalsy();
    expect(element.querySelector('[data-test="deactivate"]')).toBeTruthy();
    const model = ko.dataFor(element.querySelector('[data-test="deactivate"]'));
    expect(model.perms().link_sharing_on).toBeTruthy();
    expect(apiHelperCalled).toBeFalsy();

    // Click deactivate
    element.querySelector('[data-test="deactivate"]').click();
    await waitForObservableChange(model.perms);

    // Activate should be visible
    expect(element.querySelector('[data-test="activate"]')).toBeTruthy();
    expect(element.querySelector('[data-test="deactivate"]')).toBeFalsy();
    expect(model.perms().link_sharing_on).toBeFalsy();
    expect(apiHelperCalled).toBeTruthy();
  });
});
