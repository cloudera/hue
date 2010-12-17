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
	FileBrowser: {
		name: 'File Browser',
		css: '/filebrowser/static/css/fb.css',
		require: ['filebrowser/Hue.FileBrowser'],
		launch: function(path, options){
			return new Hue.FileBrowser(path || 'filebrowser/view/?default_to_home=1', options);
		},
		menu: {
			id: 'hue-filebrowser-menu',
			img: {
				src: '/filebrowser/static/art/icon.png'
			}
		},
		help: '/help/filebrowser/'
	},
	FileViewer: {
		name: 'File Viewer',
		css: '/filebrowser/static/css/fb.css',
		launch: function(path, options){
			return new Hue.FileViewer(path, options);
		},
		require: ['Hue.FileViewer'],
		help: '/help/filebrowser/'
		
	},
	FileEditor: {
		name: 'File Editor',
		css: '/filebrowser/static/css/fb.css',
		launch: function(path, options){
			return new Hue.FileEditor(path, options);
		},
		require: ['Hue.FileEditor'],
		help: '/help/filebrowser/'
	}
});
