/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/* eslint-disable  @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/explicit-module-boundary-types*/

import doTransform from './transformer';
import doRender from './renderer';
import { isExplainable, doRenderError } from './fallback';

export default function draw(
  data: any,
  containerElement: HTMLElement,
  onRequestDetail: any,
  queryDetails: any
): boolean {
  const explainable = isExplainable(data);
  if (explainable) {
    const transformed = doTransform(data, queryDetails);
    doRender(transformed, containerElement, onRequestDetail);
  } else {
    doRenderError(containerElement);
  }
  return explainable;
}
