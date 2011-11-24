<%namespace name="shared" file="shared_components.mako" />

${shared.header("Hue Shell", True, shells)}
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

${shared.footer()}
