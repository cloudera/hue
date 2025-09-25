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
import { useHuePubSub } from '../useHuePubSub/useHuePubSub';
import huePubSub from '../../huePubSub';
import { HueAppName } from '../../appUtils';

interface UseCurrentAppReturnType {
  currentApp: HueAppName | undefined;
  isApp: (targetApp: HueAppName) => boolean;
}

export const useCurrentApp = (): UseCurrentAppReturnType => {
  const [currentApp, setCurrentApp] = useState<HueAppName | undefined>(undefined);

  useHuePubSub<HueAppName>({
    topic: 'set.current.app.name',
    callback: (appName: HueAppName) => setCurrentApp(appName)
  });

  useEffect(() => {
    huePubSub.publish('get.current.app.name', (appName: HueAppName) => {
      setCurrentApp(appName);
    });
  }, []);

  const isApp = (targetApp: HueAppName): boolean => {
    return currentApp === targetApp;
  };

  return {
    currentApp,
    isApp
  };
};

export default useCurrentApp;
