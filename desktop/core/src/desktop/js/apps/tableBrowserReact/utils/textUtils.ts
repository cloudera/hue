// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

/**
 * Utility function to truncate text in the middle
 * @param text - The text to truncate
 * @param maxLength - Maximum length before truncation (default: 20)
 * @returns Object with truncated text and whether it was truncated
 */
export const truncateMiddle = (
  text: string,
  maxLength: number = 20
): { truncated: string; isTruncated: boolean } => {
  if (text.length <= maxLength) {
    return { truncated: text, isTruncated: false };
  }

  const start = Math.ceil(maxLength / 2) - 1;
  const end = Math.floor(maxLength / 2) - 2;

  return {
    truncated: `${text.substring(0, start)}...${text.substring(text.length - end)}`,
    isTruncated: true
  };
};
