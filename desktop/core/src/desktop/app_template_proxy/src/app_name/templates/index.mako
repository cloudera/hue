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
${'<'}%!from ${app_name}.conf import URL %>

${'<'}%namespace name="shared" file="shared_components.mako" />

${'%'}if not is_embeddable:
${'$'}{commonheader("${" ".join(word.capitalize() for word in app_name.split("_"))}", "${app_name}", user, request, "28px") | n,unicode}
${'%'}endif

${'#'}# Use double hashes for a mako template comment
${'#'}# Main body

<style type="text/css">
  #appframe {
    width: 100%;
    border: 0;
  }
</style>

<iframe id="appframe" src="${'${'} URL.get() if URL.get() else '${ app_url }' }"></iframe>

<script type="text/javascript">
  $(document).ready(function () {
    var _resizeTimeout = -1;
    $(window).on("resize", function () {
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(resizeAppframe, 300);
    });

    function resizeAppframe() {
      $("#appframe").height($(window).height() - 48); // magic: navigator height + safety pixels
    }

    resizeAppframe();
  });
</script>

${'%'}if not is_embeddable:
${'$'}{commonfooter(request, messages) | n,unicode}
${'%'}endif
