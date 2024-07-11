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
import { useRef, useEffect } from 'react';
import { DEBOUNCE_DELAY } from './constants/common';

type Timer = ReturnType<typeof setTimeout>;
export type SomeFunction = (arg: string) => void;

const useDebounce = <Func extends SomeFunction>(func: Func, delay = DEBOUNCE_DELAY): Func => {
  const timer = useRef<Timer>();

  useEffect(() => {
    return () => {
      if (!timer.current) {
        return;
      }
      clearTimeout(timer.current);
    };
  }, []);

  const debouncedFunction = ((...args) => {
    if (timer.current) {
      clearTimeout(timer.current);
    }
    const newTimer = setTimeout(() => {
      func(...args);
    }, delay);

    timer.current = newTimer;
  }) as Func;

  return debouncedFunction;
};

export default useDebounce;
