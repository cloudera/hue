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

import { useState, useEffect } from 'react';

interface Location {
  href: string;
  pathname: string;
  search: URLSearchParams;
  hash: string;
}

const getLatestLocation = (): Location => {
  const { pathname, hash, href, search } = window.location;
  let searchParams: URLSearchParams;

  try {
    searchParams = new URLSearchParams(decodeURIComponent(search));
  } catch {
    searchParams = new URLSearchParams();
  }

  return { pathname, hash, href, search: searchParams };
};
const useUrlListener = (): Location => {
  const [location, setLocation] = useState<Location>(getLatestLocation());

  const updateLocation = () => {
    const lastestLocation = getLatestLocation();
    setLocation(lastestLocation);
  };

  useEffect(() => {
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;

    window.addEventListener('popstate', updateLocation);

    history.pushState = (...args) => {
      originalPushState.apply(history, args);
      updateLocation();
    };

    history.replaceState = (...args) => {
      originalReplaceState.apply(history, args);
      updateLocation();
    };

    return () => {
      window.removeEventListener('popstate', updateLocation);
      history.pushState = originalPushState;
      history.replaceState = originalReplaceState;
    };
  }, []);

  return location;
};

export default useUrlListener;
