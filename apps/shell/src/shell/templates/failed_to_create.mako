<%namespace name="shared" file="shared_components.mako" />

${shared.header("Hue Shell", False)}

## use double hashes for a mako template comment

## this id in the div below ("index") is stripped by Hue.JFrame
## and passed along as the "view" argument in its onLoad event

## the class 'jframe_padded' will give the contents of your window a standard padding
<div id="index" class="view jframe_padded">
Failed to create a shell of the given type. The possible reasons for this are:
1. The system is out of PTYs.
2. The system cannot create more subprocesses.
3. You do not have permission to create shells of this type.
4. There is no shell with that name.
5. There is no Unix user account for you.
</div>
${shared.footer()}
