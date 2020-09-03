<!--
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
-->

# DAS-ui

You would need node 6.9.0 & yarn to run the UI

# Install dependencies

    npm install -g yarn
    npm install -g ember
    yarn install

# Running UI

    ember serve --proxy=<das-address>
    // ember serve --proxy=http://localhost:8080

# Building

* `npm run build` (production)
* Files would be stored in "dist/"
