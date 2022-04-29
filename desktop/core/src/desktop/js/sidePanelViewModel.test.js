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

import SidePanelViewModel from './sidePanelViewModel';
import huePubSub from 'utils/huePubSub';
import { BOTH_ASSIST_TOGGLE_EVENT } from 'ko/components/assist/events';
import hueAnalytics from 'utils/hueAnalytics';
import * as storageUtils from 'utils/storageUtils';

describe('SidePanelViewModel', () => {
  beforeAll(() => {
    jest.spyOn(hueAnalytics, 'convert').mockImplementation();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('Should hide the assistspanels on BOTH_ASSIST_TOGGLE_EVENT when visible', () => {
    jest.spyOn(storageUtils, 'getFromLocalStorage').mockImplementation(() => true);
    jest.spyOn(storageUtils, 'setInLocalStorage').mockImplementation(() => {});
    const sidePanelViewModel = new SidePanelViewModel();
    expect(sidePanelViewModel.rightAssistVisible()).toBeTruthy();
    expect(sidePanelViewModel.leftAssistVisible()).toBeTruthy();
    expect(storageUtils.setInLocalStorage).not.toHaveBeenCalledWith(
      'assist.left_assist_panel_visible',
      false
    );
    expect(storageUtils.setInLocalStorage).not.toHaveBeenCalledWith(
      'assist.right_assist_panel_visible',
      false
    );

    huePubSub.publish(BOTH_ASSIST_TOGGLE_EVENT);
    expect(sidePanelViewModel.rightAssistVisible()).toBeFalsy();
    expect(sidePanelViewModel.leftAssistVisible()).toBeFalsy();
    expect(storageUtils.setInLocalStorage).toHaveBeenCalledWith(
      'assist.left_assist_panel_visible',
      false
    );
    expect(storageUtils.setInLocalStorage).toHaveBeenCalledWith(
      'assist.right_assist_panel_visible',
      false
    );
  });

  it('Should show the assistspanels on BOTH_ASSIST_TOGGLE_EVENT when hidden', () => {
    jest.spyOn(storageUtils, 'getFromLocalStorage').mockImplementation(() => false);
    jest.spyOn(storageUtils, 'setInLocalStorage').mockImplementation(() => {});
    const sidePanelViewModel = new SidePanelViewModel();

    expect(sidePanelViewModel.rightAssistVisible()).toBeFalsy();
    expect(sidePanelViewModel.leftAssistVisible()).toBeFalsy();
    expect(storageUtils.setInLocalStorage).not.toHaveBeenCalledWith(
      'assist.left_assist_panel_visible',
      true
    );
    expect(storageUtils.setInLocalStorage).not.toHaveBeenCalledWith(
      'assist.right_assist_panel_visible',
      true
    );

    huePubSub.publish(BOTH_ASSIST_TOGGLE_EVENT);
    expect(sidePanelViewModel.rightAssistVisible()).toBeTruthy();
    expect(sidePanelViewModel.leftAssistVisible()).toBeTruthy();
    expect(storageUtils.setInLocalStorage).toHaveBeenCalledWith(
      'assist.left_assist_panel_visible',
      true
    );
    expect(storageUtils.setInLocalStorage).toHaveBeenCalledWith(
      'assist.right_assist_panel_visible',
      true
    );
  });
});
