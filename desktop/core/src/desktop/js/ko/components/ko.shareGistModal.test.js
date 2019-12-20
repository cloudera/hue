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

import { SHOWN_EVENT, SHOW_EVENT } from './ko.shareGistModal';
import huePubSub from 'utils/huePubSub';

import 'ext/bootstrap.2.3.2.min';

describe('ko.shareGistModal.js', () => {
  it('should render component', async () => {
    huePubSub.publish(SHOW_EVENT, {
      link: 'http://some.url'
    });

    await new Promise(resolve => {
      huePubSub.subscribeOnce(SHOWN_EVENT, resolve);
    });

    expect(document.documentElement.outerHTML).toMatchSnapshot();
  });

  it('should set the link as the input value', async () => {
    huePubSub.publish(SHOW_EVENT, {
      link: 'http://some.url'
    });

    await new Promise(resolve => {
      huePubSub.subscribeOnce(SHOWN_EVENT, resolve);
    });

    expect(document.querySelector('#gistLink').value).toEqual('http://some.url');
  });
});
