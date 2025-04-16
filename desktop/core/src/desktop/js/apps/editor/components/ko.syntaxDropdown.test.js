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

import { SHOW_EVENT, SHOWN_EVENT, SYNTAX_DROPDOWN_ID } from './ko.syntaxDropdown';
import huePubSub from 'utils/huePubSub';

describe('ko.syntaxDropdown.js', () => {
  const publishShowEvent = () => {
    huePubSub.publish(SHOW_EVENT, {
      data: {
        text: 'floo',
        expected: [{ text: 'foo' }],
        ruleId: 123
      },
      source: {
        left: 10,
        bottom: 20
      }
    });
  };

  it('should render component on show event', async () => {
    expect(document.querySelectorAll(`#${SYNTAX_DROPDOWN_ID}`)).toHaveLength(0);

    publishShowEvent();

    expect(document.querySelectorAll(`#${SYNTAX_DROPDOWN_ID}`)).toHaveLength(1);
    expect(window.document.documentElement.outerHTML).toMatchSnapshot();
  });

  it('should match snapshot', async () => {
    const shownPromise = new Promise(resolve => {
      huePubSub.subscribeOnce(SHOWN_EVENT, resolve);
    });
    publishShowEvent();

    await shownPromise;

    expect(window.document.documentElement.outerHTML).toMatchSnapshot();
  });
});
