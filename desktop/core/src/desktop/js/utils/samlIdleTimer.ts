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
import { getFromLocalStorage, setInLocalStorage } from './storageUtils';

const ALIVE_EVENTS: (keyof WindowEventMap)[] = [
  'click',
  'keydown',
  'mousemove',
  'mousewheel',
  'scroll',
  'touchstart'
];
const LOCAL_STORAGE_ID = 'hue.idle.timeout.expires';

let updateThrottle = -1;
let idleTimeoutExpires = -1;
let pendingUpdate = false;

const updateExpired = (): void => {
  idleTimeoutExpires = Date.now() + (window as hueWindow).IDLE_SESSION_TIMEOUT! * 500;
  setInLocalStorage(LOCAL_STORAGE_ID, idleTimeoutExpires); // Local storage to support multiple open tabs
  pendingUpdate = false;
};

const throttledUpdateExpired = (): void => {
  pendingUpdate = true;
  window.clearTimeout(updateThrottle);
  updateThrottle = window.setTimeout(updateExpired, 500);
};

const doSamlLogout = (): void => {
  const formElement = document.createElement('form');
  formElement.setAttribute('action', (window as hueWindow).SAML_LOGOUT_URL!);
  if ((window as hueWindow).SAML_REDIRECT_URL) {
    const inputElement = document.createElement('input');
    inputElement.setAttribute('name', 'logoutRedirect');
    inputElement.setAttribute('type', 'hidden');
    inputElement.setAttribute('value', (window as hueWindow).SAML_REDIRECT_URL!);
    formElement.appendChild(inputElement);
  }
  document.body.appendChild(formElement).submit();
};

const checkExpired = (): void => {
  const expires = getFromLocalStorage(LOCAL_STORAGE_ID, idleTimeoutExpires);
  if (!pendingUpdate && expires !== -1 && Date.now() > expires) {
    doSamlLogout();
  }
};

let checkInterval = -1;

export const attachSamlIdleTimer = (): void => {
  if (
    (window as hueWindow).SAML_LOGOUT_URL &&
    (window as hueWindow).IDLE_SESSION_TIMEOUT &&
    (window as hueWindow).IDLE_SESSION_TIMEOUT! > 0
  ) {
    window.clearInterval(checkInterval);
    ALIVE_EVENTS.forEach(event => {
      window.removeEventListener(event, throttledUpdateExpired);
      window.addEventListener(event, throttledUpdateExpired);
    });
    updateExpired();
    checkInterval = window.setInterval(checkExpired, 1000);
  }
};
