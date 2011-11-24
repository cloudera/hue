<%namespace name="shared" file="shared_components.mako" />

${shared.header("Hue Shell", True, shells)}
<div>
	The Shell app requires a Unix user account for every user of Hue on the remote webserver.
	Please ask your admin to create a user account for you on the remote webserver as
	described in the Shell documentation.
</div>
${shared.footer()}
