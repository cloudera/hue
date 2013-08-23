<%namespace name="shared" file="shared_components.mako" />

${shared.header("ZooKeeper Browser > Create Znode")}

<h2>Create New Znode :: ${path}</h2>
<hr /><br />

<form class="createZnodeForm" action="" method="POST">
<table align="center">
  ${form.as_table()|n}
<tr><td colspan="2" align="right">
  <button type="submit">Create</button>
</td></tr>
</table>
</form>

${shared.footer()}
