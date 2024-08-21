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

While creating the PR, Please go to the `Preview` tab and select appropriate template:

* [cdpd-master](?expand=1&template=pull_request_template_cdpd-master.md)
* [cdw-master|cdw-master-staging|CDWH-*|CDH-7.3.0.2](?expand=1&template=pull_request_template_cdw-master.md)
* [unified-branch|cdh_main](?expand=1&template=pull_request_template_unified_branch.md)
* [CDH-7.1.\*](?expand=1&template=pull_request_template_private_cloud.md)
* [CDH-7.2.\*|cdh_backport](?expand=1&template=pull_request_template_public_cloud.md)

-----
* If your branch regex does not follow the above list, do not select the PR template.

Template Issues
* If a template was not selected, then follow the [label-based triggering](https://cloudera.atlassian.net/wiki/spaces/ENG/pages/10776412161) approach to trigger required jobs on demand.

* If a wrong template was selected, close and create another PR by selecting the right template to execute the pre-commit CI pipeline automatically.
