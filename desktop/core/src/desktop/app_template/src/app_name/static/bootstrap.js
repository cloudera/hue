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
Hue.Desktop.register({
	${app_name_camel} : {
		name : '${app_name_spaces}',
		//autolaunch: "/${app_name}/",
		css : '/${app_name}/static/css/${app_name}.css',
		require: [ '${app_name}/${app_name_camel}' ],
		launch: function(path, options){
			// application launch code here 
			// example code below: 
			return new ${app_name_camel}(path || '/${app_name}/', options);
		},
		menu: {
			id: 'hue-${app_name}-menu',
			img: {
				// Replace this with a real icon!
				// ideally a 55x55 transparent png
				src: '/${app_name}/static/art/${app_name}.png'
			}
		},
		help: '/help/${app_name}/'
	}
});
