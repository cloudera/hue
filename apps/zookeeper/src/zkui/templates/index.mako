<%namespace name="shared" file="shared_components.mako" />

${shared.header("ZooKeeper Browser")}

<h2>Overview</h2>

<br />

% for i, c in enumerate(overview):
  <h3> ${i+1}. <a href="${url('zkui.views.view', id=i)}">${c['nice_name']} Cluster Overview</a></h3><br />

  <table data-filters="HtmlTable">
  <thead>
    <tr>
      <th>Node</th>
      <th>Role</th>
      <th>Avg Latency</th>
      <th>Watch Count</th>
      <th>Version</th>
    </tr>
  </thead>
  % for host, stats in c['stats'].items():
    <tr>
      <td>${host}</td>
      <td>${stats.get('zk_server_state', '')}</td>
      <td>${stats.get('zk_avg_latency', '')}</td>
      <td>${stats.get('zk_watch_count', '')}</td>
      <td>${stats.get('zk_version', '')}</td>
    </tr>
  % endfor
  </table>

  <br /><br />
% endfor 

${shared.footer()}

