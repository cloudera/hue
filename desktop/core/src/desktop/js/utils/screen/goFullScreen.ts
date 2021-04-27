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

import isFullScreen from './isFullScreen';

interface FullscreenElement extends HTMLElement {
  msRequestFullscreen?: HTMLElement['requestFullscreen'];
  mozRequestFullScreen?: HTMLElement['requestFullscreen'];
  webkitRequestFullscreen?(allowKeyboardInput?: boolean): Promise<void>;
  ALLOW_KEYBOARD_INPUT?: boolean;
}

const goFullScreen = async (element: Element): Promise<void> => {
  if (isFullScreen()) {
    return;
  }
  if (!element) {
    element = document.documentElement;
  }

  if (element.requestFullscreen) {
    return element.requestFullscreen();
  }
  const mixedBrowserElement = element as FullscreenElement;
  if (mixedBrowserElement.msRequestFullscreen) {
    return mixedBrowserElement.msRequestFullscreen();
  }
  if (mixedBrowserElement.mozRequestFullScreen) {
    return mixedBrowserElement.mozRequestFullScreen();
  }
  if (mixedBrowserElement.webkitRequestFullscreen) {
    return mixedBrowserElement.webkitRequestFullscreen(mixedBrowserElement.ALLOW_KEYBOARD_INPUT);
  }
};

export default goFullScreen;
