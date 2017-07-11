## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
${'<'}%!from desktop.views import commonheader, commonfooter %>
${'<'}%namespace name="shared" file="shared_components.mako" />

${'%'}if not is_embeddable:
${'$'}{commonheader("${" ".join(word.capitalize() for word in app_name.split("_"))}", "${app_name}", user, request) | n,unicode}
${'%'}endif

${'$'}{shared.menubar(section='mytab')}

${'#'}# Use double hashes for a mako template comment
${'#'}# Main body

<div class="container-fluid">
  <div class="card">
    <h2 class="card-heading simple">${" ".join(word.capitalize() for word in app_name.split("_"))} app is successfully setup!</h2>
    <div class="card-body">
      ## Pass through literal $
      <p>It's now ${'$'}{date}.</p>
    </div>
  </div>
</div>
${'%'}if not is_embeddable:
${'$'}{commonfooter(request, messages) | n,unicode}
${'%'}endif
