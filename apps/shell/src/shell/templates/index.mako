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
from django.utils.translation import ugettext as _
%>


${commonheader(_('Hue Shell'), "shell", user, "100px")}

<div class="subnav subnav-fixed">
    <div class="container-fluid">
        <ul class="nav nav-pills">
            % for shell in shells:
                % if shell["exists"]:
                    <li><a href="${url('shell.views.create')}?keyName=${shell["keyName"]}" class="${shell["keyName"]}">${shell["niceName"]}</a></li>
                % else:
                    <li><a href="#" class="disabled">${shell["niceName"]}</a></li>
                % endif
            % endfor
        </ul>
    </div>
</div>


<div class="container-fluid">
  % if shell_id:
    <style type="text/css" media="screen">
        body {
            background-color: #333;
        }

        .shell {
            background-color: #333;
            color: #EEE;
            font-family: monospace;
            font-size: 14px;
        }

        #shellOutput {
            padding: 0;
            width: 100%;
        }

        #shellInput {
            border: none;
            outline: none;
            margin: 0;
            margin-top: 0px;
            margin-bottom: 10px;
            padding: 0;
            padding-top: 8px;
            box-shadow: none;
            width: 400px;
            background-color: #333333;
            color: #EEE;
        }

        #shellInput:focus {
            box-shadow: none;
            border: 0;
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
                ${_('Please select one of the available shells from the toolbar above.')}
            % else:
                ${_('You do not have permission to access any shell or there is no configured shell.')}
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
            var temporaryCommand = "";

            return {
                recordCommand: function(command) {
                    if (command) {
                        previousCommands.push(command);
                        currentCommandIndex = previousCommands.length;
                        temporaryCommand = "";
                    }
                },
                getPreviousCommand: function() {
                    var command = "";
                    if (currentCommandIndex > 0){
                        currentCommandIndex--;
                        command = previousCommands[currentCommandIndex];
                    }
                    else {
                        if (previousCommands.length > 0){
                            command = previousCommands[0];
                        }
                    }
                    return command;
                },
                getNextCommand: function() {
                    var command = "";
                    if (currentCommandIndex < previousCommands.length - 1) {
                        currentCommandIndex++;
                        command = previousCommands[currentCommandIndex];
                    }
                    else {
                        currentCommandIndex = previousCommands.length;
                        command = temporaryCommand;
                    }
                    return command;
                },
                updateTemporaryCommand: function(partial){
                    temporaryCommand = partial;
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
                                focusShellInput();
                                $("html, body").animate({ scrollTop: $(document).height() }, "fast");
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
                var input = null;
                var key = e.keyCode ? e.keyCode : e.which
                if (key == 13){
                    shell.send($(this).val());
                    history.recordCommand($(this).val());
                    input = ""
                } else if (key == 38){
                    input = history.getPreviousCommand();
                    e.preventDefault();
                } else if (key == 40){
                    input = history.getNextCommand();
                    e.preventDefault();
                }
                setShellInput(input);
            });

            $("#shellInput").keyup(function(e){
                var key = e.keyCode ? e.keyCode : e.which
                if ((key > 46 && key < 91) || (key > 95 && key < 112) || (key > 185)) {
                    history.updateTemporaryCommand($(this).val());
                }
            });

            $(document).keypress(function(e){
                focusShellInput();
            });
        }

        function focusShellInput() {
            if (!$("#shellInput").is(":focus")) {
                $("#shellInput").focus();
            }
        }
    });
</script>
</div>

${commonfooter(messages)}
