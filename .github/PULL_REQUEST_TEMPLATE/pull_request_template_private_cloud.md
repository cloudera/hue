<!--
 Licensed to Cloudera, Inc. under one
 or more contributor license agreements.  See the NOTICE file
 distributed with this work for additional information
 regarding copyright ownership.  Cloudera, Inc. licenses this file
 to you under the Apache License, Version 2.0 (the
 "License"); you may not use this file except in compliance
 with the License.  You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

Automated Triggers
==============
Trigger tests:
- [x] Smoke Tests
## Gatekeeping Tests [How to use ?](https://cloudera.atlassian.net/wiki/spaces/ENG/pages/9945481342/Automated+gatekeeping#How-to-use-it.2)
(Select only one option from the list below)
- [ ] Gate Smoke
- [ ] Fresh Install
#### Additional flags (Optional) Please add additional flags in the line below -C -O etc..



------------------------------------------
To override the job votes use the labels below (Only Gatekeepers and Admins)

* CDH-BUILD                       = ci-build-pass
* SMOKE-TESTS                     = smoketest-pass
* GATEKEEPING-TICKET-VALIDATION   = gk-ticket-validation-pass
* GATEKEEPING-SMOKE-TESTS         = gk-system-test-pass
-----------
* To re-run build use Re-run all jobs / Re-run failed jobs option from the Github UI
* To re-run tests follow [label-based triggering](https://cloudera.atlassian.net/wiki/spaces/ENG/pages/10776412161)
