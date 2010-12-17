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
${'<'}%namespace name="shared" file="shared_components.mako" />

${'$'}{shared.header("${" ".join(word.capitalize() for word in app_name.split("_"))}")}

${'#'}# use double hashes for a mako template comment

${'#'}# this id in the div below ("index") is stripped by Hue.JFrame
${'#'}# and passed along as the "view" argument in its onLoad event

${'#'}# the class 'jframe_padded' will give the contents of your window a standard padding
<div id="index" class="view jframe_padded">
  <h2>${" ".join(word.capitalize() for word in app_name.split("_"))} app is successfully setup!</h2>
  ## Pass through literal $
  <p>It's now ${'$'}{date}.</p>
</div>
${'$'}{shared.footer()}