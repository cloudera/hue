<%namespace name="shared" file="shared_components.mako" />

${shared.header("Hue Shell", False)}

## use double hashes for a mako template comment

## this id in the div below ("index") is stripped by Hue.JFrame
## and passed along as the "view" argument in its onLoad event

## the class 'jframe_padded' will give the contents of your window a standard padding
<div id="index" class="view jframe_padded">
The webserver currently running Hue does not support the Shell app. Please contact your
administrator.
</div>
${shared.footer()}
