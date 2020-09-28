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

import d3 from 'd3v3';

export function isExplainable(data: any): boolean {
  try {
    const stages = data['STAGE PLANS'];
    const isValidFetchStageAvailable = Object.keys(stages).find((cStageKey: any) =>
      stages[cStageKey].hasOwnProperty('Fetch Operator')
    );
    return !!isValidFetchStageAvailable;
  } catch (e) {
    return false;
  }
}

export function doRenderError(containerElement: HTMLElement): void {
  d3.select(containerElement).select('*').remove();

  d3.select(containerElement)
    .append('div')
    .attr('class', 'explain--error')
    .append('div')
    .text('No valid explain plan found.');
}
