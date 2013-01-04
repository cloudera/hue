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
<%!
from desktop.views import commonheader, commonfooter
%>
${ commonheader("Hue Help", "help", user, "100px") | n,unicode }
	<div class="subnav subnav-fixed">
		<div class="container-fluid">
		<ul class="nav nav-pills">
			% for app in apps:
				<li><a href="${url("help.views.view", app=app.name, path="/")}">${app.nice_name}</a></li>
			% endfor
		</ul>
		</div>
	</div>
	<div class="container-fluid">
		${content|n}
	</div>

  <script>
    $(document).ready(function () {
      $("a").click(function (e) {
        var _link = $(this);
        if (_link.attr("href").indexOf("#") == 0) {
          e.preventDefault();
          $(".returnHome").remove();
          var _anchor = $("a[name='" + decodeURIComponent(_link.attr("href").substring(1)) + "']").last();
          $("html, body").animate({
            scrollTop:(_anchor.position().top - $(".navbar-fixed-top").height() - $(".subnav-fixed").height()) + "px"
          }, 300);
          createTopArrow(_anchor);
        }
      });

      if (window.location.hash != ""){
        var _anchor = $("a[name='" + decodeURIComponent(window.location.hash.substring(1)) + "']").last();
        window.setTimeout(function(){
          $("html, body").scrollTop(_anchor.position().top - $(".navbar-fixed-top").height() - $(".subnav-fixed").height());
          createTopArrow(_anchor);
        }, 10);
      }

      function createTopArrow(anchor){
        $("<i>").css("cursor", "pointer").css("margin-left", "10px").attr("class", "returnHome icon icon-arrow-up").click(function () {
          $(this).remove();
          $("html, body").animate({
            scrollTop:"0px"
          }, 300);
        }).appendTo(anchor.parent());
      }
    });
  </script>

${ commonfooter(messages) | n,unicode }
