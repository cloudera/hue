#!/usr/bin/env bash

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -x
AVATICA_VER=rel/avatica-1.10.0

set -e

rm -rf avatica-tmp

mkdir avatica-tmp
cd avatica-tmp
wget -O avatica.tar.gz https://github.com/apache/calcite-avatica/archive/$AVATICA_VER.tar.gz
tar -x --strip-components=1 -f avatica.tar.gz

cd ..
rm -f phoenixdb/avatica/proto/*_pb2.py
protoc --proto_path=avatica-tmp/core/src/main/protobuf/ --python_out=phoenixdb/avatica/proto avatica-tmp/core/src/main/protobuf/*.proto
if [[ "$(uname)" == "Darwin" ]]; then
  sed -i '' 's/import common_pb2/from . import common_pb2/' phoenixdb/avatica/proto/*_pb2.py
else
  sed -i 's/import common_pb2/from . import common_pb2/' phoenixdb/avatica/proto/*_pb2.py
fi

for f in $(find phoenixdb/avatica/proto -name '*.py'); do
  cat << EOF > ${f}-with-header
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
EOF
  cat $f >> ${f}-with-header
done

rm -rf avatica-tmp
