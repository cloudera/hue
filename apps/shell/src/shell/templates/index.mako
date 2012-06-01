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
<div class="subnav subnav-fixed">
    <div class="container-fluid">
        <ul class="nav nav-pills">
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
    <span id="shell_id" class="hide">${shell_id}</span>
  % else:
    <div>
        <h3>
            % if shells:
                Please select one of the available shells from the toolbar above.
            % else:
                You don't have permission to access any shell or there is no configured shell.
            % endif
        </h3>
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

        var history = (function() {
            var previousCommands = [];
            var currentCommandIndex = 0;
            // Save the initial input ("enter" key not pressed yet before navigating in the history)
            var temporaryInput = null;

            return {
                recordCommand: function(command) {
                    if (command) {
                        if (previousCommands[previousCommands.length - 1] != command) {
                            previousCommands.push(command);
                            currentCommandIndex = previousCommands.length;
                            temporaryInput = null;
                        }
                    }
                },
                getPreviousCommand: function(input) {
                    if (currentCommandIndex == previousCommands.length) {
                        temporaryInput = input;
                    }

                    var command = null;
                    if (currentCommandIndex > 0) {
                        currentCommandIndex--;
                        command = previousCommands[currentCommandIndex];
                    }
                    return command;
                },
                getNextCommand: function() {
                    var command = null;
                    if (currentCommandIndex < previousCommands.length - 1) {
                        currentCommandIndex++;
                        command = previousCommands[currentCommandIndex];
                    } else {
                        command = temporaryInput;
                        currentCommandIndex = previousCommands.length;
                    }
                    return command;
                }
            };
        })();

        function setShellInput(command) {
            if (command != null) {
                $("#shellInput").val(command);
            }
        };

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
								var output = data[_shell.id].output;
								output = output.replace(/&/g, '&amp;')
								               .replace(/</g, '&lt;')
								               .replace(/>/g, '&gt;')
								               .replace(/"/g, '&quot;')
								               .replace(/\n/g, '<br/>');
								$("#shellContent").append(output);
								if (output.indexOf("Disconnected!")>-1){
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
								$('body').animate({scrollTop: $(document).height()}, 'slow');
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

            $("#shellInput").keydown(function(e){
                $(this).width($(document).width()-100-$(this).position().left);

                var input = null;
                var key = e.keyCode ? e.keyCode : e.which

                if (key == 13){
                    shell.send($(this).val());
                    history.recordCommand($(this).val());
                    input = ""
                } else if (key == 38){
                    input = history.getPreviousCommand($(this).val());
                    e.preventDefault();
                } else if (key == 40){
                    input = history.getNextCommand();
                }

                setShellInput(input);
            });

            $(document).keypress(function(e){
                if (! $("#shellInput").is(":focus")) {
                    $("#shellInput").focus();
                }
            });
        }
	});
</script>
</div>

${commonfooter()}
