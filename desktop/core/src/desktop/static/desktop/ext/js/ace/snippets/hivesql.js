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

ace.define("ace/snippets/hivesql",["require","exports","module"], function(require, exports, module) {
"use strict";

exports.snippetText = "snippet tbl\n\
	CREATE TABLE ${1:table} (\n\
		${2:column_name} ${3:column_type}\n\
	) ${4:COMMENT ''};\n\
snippet s*\n\
	SELECT * FROM ${1:table}\n\
";
exports.scope = "hivesql";

});
