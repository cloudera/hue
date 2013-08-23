<%namespace name="shared" file="shared_components.mako" />

${shared.header("ZooKeeper Browser > Edit Znode > %s" % path)}

<h2>Edit Znode Data :: ${path}</h2>
<hr /><br />

<form class="editZnodeForm" action="" method="POST">
<table align="center">
  ${form.as_table()|n}
<tr><td colspan="2" align="right">
  <button type="submit">Save</button>
</td></tr>
</table>
</form>

${shared.footer()}
