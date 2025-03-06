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

import { useLayoutEffect, useState } from 'react';

interface WindowSize {
  width: number;
  height: number;
}

interface WindowOffset {
  top: number;
  left: number;
}

export const useWindowSize = (
  ref?: React.RefObject<HTMLElement>
): {
  size: WindowSize;
  offset: WindowOffset;
} => {
  const [size, setSize] = useState<WindowSize>({
    width: window.innerWidth,
    height: window.innerHeight
  });

  const [offset, setOffset] = useState<WindowOffset>({
    top: 0,
    left: 0
  });

  const handleResize = () => {
    setSize({
      width: window.innerWidth,
      height: window.innerHeight
    });

    if (ref?.current) {
      const rect = ref.current.getBoundingClientRect();
      setOffset({
        top: rect.top + window.scrollY,
        left: rect.left + window.scrollX
      });
    }
  };

  useLayoutEffect(() => {
    handleResize();

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [ref]);

  return { size, offset };
};
