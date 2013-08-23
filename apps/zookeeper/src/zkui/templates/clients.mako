<%namespace name="shared" file="shared_components.mako" />

${shared.header("ZooKeeper Browser > Clients > %s:%s" % (host, port))}

<h1>${host}:${port} :: client connections</h1>
<br />

% if clients:
  <table data-filters="HtmlTable"> 
  <thead>
    <tr>
      <th>Host</th>
      <th>Port</th>
      <th>Interest Ops</th>
      <th>Queued</th>
      <th>Received</th>
      <th>Sent</th>
  </thead>
  % for client in clients:
    <tr>
      <td>${client.host}</td>
      <td>${client.port}</td>
      <td>${client.interest_ops}</td>
      <td>${client.queued}</td>
      <td>${client.recved}</td>
      <td>${client.sent}</td>
    </tr>
  % endfor
  </table>
% endif

${shared.footer()}

