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

import * as ko from 'knockout';

const instances = {};

class componentUtils {
  static async registerComponent(name, model, template) {
    return new Promise((resolve, reject) => {
      if (!ko.components.isRegistered(name)) {
        const componentInfo = {
          template: template
        };
        if (model) {
          componentInfo['viewModel'] = model;
        }
        ko.components.register(name, componentInfo);
        resolve();
      } else {
        reject();
      }
    });
  }

  static async registerStaticComponent(name, model, template) {
    return componentUtils.registerComponent(
      name,
      {
        createViewModel: (params, componentInfo) => {
          if (!instances[name]) {
            if (model && model.createViewModel) {
              instances[name] = model.createViewModel(params, componentInfo);
            } else if (model) {
              instances[name] = new model(params);
            }
          }
          if (instances[name] && instances[name].dispose) {
            console.warn('"dispose" function present on static component ' + name);
          }
          return instances[name];
        }
      },
      template
    );
  }
}

export default componentUtils;
