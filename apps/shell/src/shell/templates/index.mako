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

% if shells:
	${commonheader("Hue Shell", "shell", "100px")}
% else:
	${commonheader("Hue Shell", "shell")}
% endif


% if shells:
<div class="menubar">
	<div class="menubar-inner">
		<div class="container-fluid">
			<ul class="nav">
			% if len(shells) == 1:
				% if shells[0]["exists"]:
					<li><a href="${url('shell.views.create')}?keyName=${shells[0]["keyName"]}" class="${shells[0]["keyName"]}">${shells[0]["niceName"]}</a></li>
				% else: 
					<li><a href="#" class="disabled">${shells[0]["niceName"]}</a></li>
				% endif
			% else:
				% if shells[0]["exists"]:
					<li><a href="${url('shell.views.create')}?keyName=${shells[0]["keyName"]}" class="${shells[0]["keyName"]}">${shells[0]["niceName"]}</a></li>
				% else:
					<li><a href="#" class="disabled">${shells[0]["niceName"]}</a></li>
				% endif
				% for item in shells[1:-1]:
					% if item["exists"]:
						<li><a href="${url('shell.views.create')}?keyName=${item["keyName"]}" class="${item["keyName"]}">${item["niceName"]}</a></li>
					% else:
						<li><a href="#" class="disabled">${item["niceName"]}</a></li>
					% endif
				% endfor
				% if shells[-1]["exists"]:
					<li><a href="${url('shell.views.create')}?keyName=${shells[-1]["keyName"]}" class="${shells[-1]["keyName"]}">${shells[-1]["niceName"]}</a></li>
				% else:
					<li><a href="#" class="disabled">${shells[-1]["niceName"]}</a></li>
				% endif
			% endif
			</ul>
		</div>
	</div>
</div>
% endif


<div class="container-fluid">

  % if shell_id:
	<style type="text/css" media="screen">
		body {
			background-color: #333;
		}
		.shell {
			background-color:#333;
			color:#EEE;
			font-family: monospace;
			font-size: 14px;
		}
		#shellOutput {
			/*position:absolute;
			left:0;
			top:-20px;*/
			padding:0;
			width:100%;
		}
		#shellInput {
			border:0;
			margin:0;
			margin-top:10px;
			margin-bottom:10px;
			padding:0;
			box-shadow:none;
			

		}
		#shellInput:focus {
			box-shadow:none;
			border:0;
		}
		#shellContent {

		}
	</style>
	<div id="shellOutput" class="shell">
		<span id="shellContent"></span>
		<input type="text" id="shellInput" class="shell" />
	</div>
	<span id="shell_id" class="hidden">${shell_id}</span>
  % else:
	<div>
		<h3>Please select one of the available shells from the toolbar above.</h3>
	</div>
  % endif


<script type="text/javascript" charset="utf-8">
	$(document).ready(function(){
		var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
		for (var i=0;i<hashes.length;i++){
			if (hashes[i].indexOf("keyName")>-1){
				$("."+hashes[i].split("=")[1]).addClass("selected");
			}
		}
		
		var hueInstanceID = function() {
			var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
			var lastIndex = chars.length - 1;
			var stringLength = 128;
			var randomString = "";
			for (var i = 0; i < stringLength; i++) {
				var randomIndex = Math.floor(Math.random()*lastIndex);
				randomString += chars.substring(randomIndex, randomIndex+1);
			}
			return randomString;
		}();
		
		if ($("#shell_id").length){
		
			var shell = {};
			shell.id = $("#shell_id").text();
			shell.get = function(offset){
				var _shell = this;
				$.ajax({
					type: "POST",
					url: "/shell/retrieve_output",
					data: {
						numPairs: 1,
						offset1: offset,
						shellId1: _shell.id
					},
					beforeSend: function(xhr){ 
						xhr.setRequestHeader("X-Request", "JSON");
						xhr.setRequestHeader("Hue-Instance-ID", hueInstanceID);
					},
					success: function(data, status, xhr){
						if (status == "success"){
							if (data.periodicResponse){
								shell.get(offset);
							}
							else {
								var _out = data[_shell.id].output;
								_out = _out.replace(/>/g, '&gt;');
								_out = _out.replace(/</g, '&lt;');
								_out = _out.replace(/\n/g, '<br />');
								$("#shellContent").html($("#shellContent").html()+_out);
								if (_out.indexOf("Disconnected!")>-1){
									window.setTimeout(function(){
										$.ajax({
											type: "POST",
											url: "/shell/kill_shell",
											data: {
												shellId: _shell.id
											},
											beforeSend: function(xhr){ 
												xhr.setRequestHeader("X-Request", "JSON");
											},
											success: function(data, status, xhr){
												location.href = "/shell/";
											}
										});
									},500);
								}
								$("html").animate({ scrollTop: $(document).height() }, "fast");
								_shell.get(data[_shell.id].nextOffset);
							}
						}
					}
				});
			};
			shell.send = function(command){
				var _shell = this;
				$.ajax({
					type: "POST",
					url: "/shell/process_command",
					data: {
						lineToSend: command,
						shellId: _shell.id
					},
					beforeSend: function(xhr){ 
						xhr.setRequestHeader("X-Request", "JSON");
					},
					success: function(data, status, xhr){
						if (status == "success"){
							if (command == "quit"){
								window.setTimeout(function(){
									$.ajax({
										type: "POST",
										url: "/shell/kill_shell",
										data: {
											shellId: _shell.id
										},
										beforeSend: function(xhr){ 
											xhr.setRequestHeader("X-Request", "JSON");
										},
										success: function(data, status, xhr){
											location.href = "/shell/";
										}
									});
								},500);
							}
						}
					}
				});
			};
		
			shell.get(0);
		
			$("#shellInput").val("");
			$("#shellInput").focus();
		
			$("#shellInput").blur(function(){
				window.setTimeout(function(){
					$("#shellInput").focus();
				}, 50);
			});
			$("#shellInput").keydown(function(e){
				if ((e.keyCode ? e.keyCode : e.which) == 13){
					shell.send($(this).val());
					$(this).val("");
				}
			});
		
		}
				
		
	});
</script>
</div>
${commonfooter()}
