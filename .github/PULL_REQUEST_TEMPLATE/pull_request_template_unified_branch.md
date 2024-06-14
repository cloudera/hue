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
- [x] CI Pre-commit Tier Tests
------------------------------------------
To override the job votes use the labels below (Only Gatekeepers and Privileged Users)

* GATEKEEPING-TICKET    (starts automatically on PR creation and new commit push)  = gk-ticket-validation-pass
* CDH-BUILD             (requires successful GATEKEEPING-TICKET to start)  = ci-build-pass
* SMOKE-TESTS           (requires successful CDH-BUILD to start)                   = smoketest-pass
* PRECOMMIT-TIER-TESTS  (requires successful CDH-BUILD and SMOKE-TESTS to start)   = precommit-tier-tests-pass
-----------
* To re-run build use [Re-run all jobs / Re-run failed jobs option from the Github UI](https://cloudera.atlassian.net/wiki/spaces/ENG/pages/10207297891/GitHub+Actions#recheck%2Cre-trigger-in-Github-actions)
* To re-run tests follow [label-based triggering](https://cloudera.atlassian.net/wiki/spaces/ENG/pages/10776412161)
