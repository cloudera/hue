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

/**
 * Calculates the duration between two dates.
 * @param start The start date.
 * @param end The end date.
 * @returns The duration as a string in the format "hh:mm:ss".
 */
export const calculateDuration = (start: Date | string, end: Date | string): string => {
  if (!start || !end) {
    return 'N/A'; // If either start or end is missing
  }

  const startDate = new Date(start);
  const endDate = new Date(end);
  const duration = endDate.getTime() - startDate.getTime(); // Duration in milliseconds

  if (isNaN(duration)) {
    return 'Invalid Dates'; // If dates can't be parsed
  }

  // Convert duration to hours, minutes, and seconds
  const seconds = Math.floor((duration / 1000) % 60);
  const minutes = Math.floor((duration / (1000 * 60)) % 60);
  const hours = Math.floor(duration / (1000 * 60 * 60));

  // Build duration string
  let durationStr = '';
  if (hours > 0) {
    durationStr += `${hours}h, `;
  }
  if (minutes > 0 || hours > 0) {
    durationStr += `${minutes}m, `;
  }
  durationStr += `${seconds}s`;

  return durationStr;
};

/**
 * Formats a timestamp to a readable string.
 * @param timestamp The timestamp to format.
 * @returns The formatted timestamp as a string.
 */
export const formatTimestamp = (timestamp: Date | string): string => {
  const options = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  };
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', options);
};
