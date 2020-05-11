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

import ApiStrategy from './apiStrategy';
import BaseStrategy from './baseStrategy';
import LocalStrategy from './localStrategy';

const optimizerInstances = {};

export const LOCAL_STRATEGY = 'local';
export const API_STRATEGY = 'api';

const createOptimizer = connector => {
  // TODO: Remove window.OPTIMIZER_MODE and hardcoded { optimizer: 'api' } when 'connector.optimizer_mode' works.
  if (window.OPTIMIZER_MODE === LOCAL_STRATEGY) {
    return new LocalStrategy(connector);
  }
  if (window.OPTIMIZER_MODE === API_STRATEGY) {
    return new ApiStrategy(connector);
  }
  return new BaseStrategy(connector);
};

export const getOptimizer = connector => {
  if (!optimizerInstances[connector.id]) {
    optimizerInstances[connector.id] = createOptimizer(connector);
  }
  return optimizerInstances[connector.id];
};
