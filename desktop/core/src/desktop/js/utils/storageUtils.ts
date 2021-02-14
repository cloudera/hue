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

type LocalStorageGet = {
  <T = string>(key: string): T | null;
  <T = string>(key: string, defaultValue: T): T;
};
export const getFromLocalStorage: LocalStorageGet = <T>(key: string, defaultValue?: T) => {
  const defaultOrNull = typeof defaultValue !== 'undefined' ? defaultValue : null;
  if (!window.localStorage || (<hueWindow>window).DISABLE_LOCAL_STORAGE) {
    return defaultOrNull;
  }

  const userKey = (<hueWindow>window).LOGGED_USERNAME
    ? `${(<hueWindow>window).LOGGED_USERNAME}.${key}`
    : key;
  const storedValue = window.localStorage.getItem(userKey);
  if (storedValue === null) {
    return defaultOrNull;
  }

  if (storedValue && storedValue.length) {
    try {
      return JSON.parse(storedValue);
    } catch (e) {}
    return <T>(<unknown>storedValue);
  }
  return defaultOrNull;
};

export const setInLocalStorage = (key: string, value: unknown): void => {
  if (!window.localStorage) {
    return;
  }
  if ((<hueWindow>window).DISABLE_LOCAL_STORAGE) {
    window.localStorage.clear();
    return;
  }
  const userKey = (<hueWindow>window).LOGGED_USERNAME
    ? `${(<hueWindow>window).LOGGED_USERNAME}.${key}`
    : key;
  if (typeof value === 'undefined' || value === null) {
    window.localStorage.removeItem(userKey);
  } else {
    let jsonString: string | undefined = undefined;
    try {
      jsonString = JSON.stringify(value);
    } catch (e) {}
    try {
      window.localStorage.setItem(userKey, jsonString || String(value));
    } catch (e) {}
  }
};

export const hueLocalStorage = <T = string>(key: string, value?: T): T | null => {
  if (typeof value !== 'undefined') {
    setInLocalStorage(key, value);
    return value;
  }
  return getFromLocalStorage(key);
};

export const withLocalStorage = <T = string>(
  key: string,
  observable: KnockoutObservable<T>,
  defaultValue?: T,
  noInit = false
): KnockoutSubscription => {
  const cachedValue = getFromLocalStorage<T>(key);
  if (!noInit && cachedValue !== null) {
    observable(cachedValue);
  } else if (defaultValue) {
    observable(defaultValue);
  }

  return observable.subscribe(newValue => {
    setInLocalStorage(key, newValue);
  });
};
