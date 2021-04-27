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

import { hueWindow } from 'types/types';
import huePubSub from 'utils/huePubSub';

const onHueLinkClick = (event: Event, url: string, target?: string): void => {
  if (url.indexOf('http') === 0) {
    window.open(url, target);
  } else {
    const prefix = (<hueWindow>window).HUE_BASE_URL + '/hue' + (url.indexOf('/') === 0 ? '' : '/');
    if (target) {
      window.open(prefix + url, target);
    } else if (
      (<KeyboardEvent>event).ctrlKey ||
      (<KeyboardEvent>event).metaKey ||
      (<KeyboardEvent>event).which === 2
    ) {
      window.open(prefix + url, '_blank');
    } else {
      huePubSub.publish('open.link', url);
    }
  }
};

export default onHueLinkClick;
