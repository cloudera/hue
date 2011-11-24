<%namespace name="shared" file="shared_components.mako" />

${shared.header("Hue Shell", True, shells)}
<div>
	Failed to create a shell of the given type. The possible reasons for this are:
	<ol>
		<li>The system is out of PTYs.</li>
		<li>The system cannot create more subprocesses.</li>
		<li>You do not have permission to create shells of this type.</li>
		<li>There is no shell with that name.</li>
		<li>There is no Unix user account for you.</li>
	</ol>
</div>
${shared.footer()}
