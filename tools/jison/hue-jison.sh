#!/bin/bash
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

echo "Make sure you install jison first (npm install jison -g)"
echo ""
echo "Generating parser..."

pushd ../../desktop/core/src/desktop/static/desktop/js/autocomplete/jison

# For quick version of select and no support for value expressions (i.e. a = b or a IN (1, 2, 3))
# cat sql_main.jison ../sql_end.jison > sql.jison

# For quick version of select with value expressions
#cat sql_valueExpression_dev.jison sql_valueExpression.jison ../sql_end.jison > sql.jison

# For quick version of select with create only and no support for value expressions (i.e. a = b or a IN (1, 2, 3))
# cat sql_main.jison sql_create.jison sql_end.jison > sql.jison

cat sql_main.jison sql_valueExpression.jison sql_error.jison sql_alter.jison sql_analyze.jison sql_create.jison sql_drop.jison sql_grant.jison sql_insert.jison sql_load.jison sql_set.jison sql_show.jison sql_update.jison sql_use.jison ../sql_end.jison > sql.jison

jison sql.jison sql.jisonlex
cat license.txt sql.js > ../sql.js
rm sql.jison
rm sql.js
popd
echo "Done!"
