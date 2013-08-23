<%namespace name="shared" file="shared_components.mako" />

${shared.header("ZooKeeper Browser > Tree > %s > %s" % (cluster['nice_name'], path))}

<h1>${cluster['nice_name'].lower()} :: ${path}</h1>
<br />

<table data-filters="HtmlTable">
  <thead>
  <th colspan="2">Children</th>
  </thead>
  % for child in children:
    <tr><td width="100%">
      <a href="${url('zkui.views.tree', id=cluster['id'], \
          path=("%s/%s" % (path, child)).replace('//', '/'))}">
      ${child}</a>
    </td><td>
      <a title="Delete ${child}" class="delete frame_tip confirm_and_post" alt="Are you sure you want to delete ${child}?" href="${url('zkui.views.delete', id=cluster['id'], \
          path=("%s/%s" % (path, child)).replace('//', '/'))}">Delete</a>
    </td></tr>
  % endfor
</table>
<br />
<span style="float: right">
  ${shared.info_button(url('zkui.views.create', id=cluster['id'], path=path), 'Create New')}
</span>

<div style="clear: both"></div>

<h2>data :: base64 :: length :: ${znode.get('dataLength', 0)}</h2>
<br />

<textarea name="data64" style="width: 100%;" rows="5" readonly="readonly">${znode.get('data64', '')}</textarea>
<div style="clear: both"></div>
<span style="float: right">
  ${shared.info_button(url('zkui.views.edit_as_base64', id=cluster['id'], path=path), 'Edit as Base64')}
  ${shared.info_button(url('zkui.views.edit_as_text', id=cluster['id'], path=path), 'Edit as Text')}
</span>
<div style="clear: both"></div>
<br />

<h2>stat information</h2>
<br />

<table data-filters="HtmlTable">
  <thead><tr><th>Key</th>
    <th width="80%">Value</th></tr></thead>
  % for key in ('pzxid', 'ctime', 'aversion', 'mzxid', \
      'ephemeralOwner', 'version', 'mtime', 'cversion', 'czxid'):
    <tr><td>${key}</td><td>${znode[key]}</td></tr> 
  % endfor
</table>

<br />
<a target="_blank" href="http://hadoop.apache.org/zookeeper/docs/current/zookeeperProgrammers.html#sc_zkStatStructure">Details on stat information.</a>

${shared.footer()}

