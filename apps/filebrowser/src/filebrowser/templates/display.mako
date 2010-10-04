## -*- coding: utf-8 -*-
## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
  import datetime
  from django.template.defaultfilters import urlencode, escape, stringformat, date, filesizeformat, time
  from filebrowser.views import truncate
%>
<%
  path_enc = urlencode(path)
  dirname_enc = urlencode(view['dirname'])
  base_url = url('filebrowser.views.view', path=path_enc)
%>
<html>
<head><title>${truncate(filename)} :: File Viewer</title></head>
<body>
  <div class="toolbar">
    <div class="fv-path draggable" data-filters="FitText">${path}</div>

    <div class="fv-actions" data-filters="ArtButtonBar">
      % if view['mode'] == "binary":
        <a class="fv-viewText" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16}" href="${base_url}?offset=${view['offset']}&length=${view['length']}&mode=text&compression=${view['compression']}">View As Text</a>
      % endif

      % if view['mode'] == "text":
        <a class="fv-viewBinary" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16}" href="${base_url}?offset=${view['offset']}&length=${view['length']}&mode=binary&compression=${view['compression']}">View As Binary</a>
      % endif

      % if view['compression'] != "gzip" and path.endswith('.gz'):
        <a class="fv-viewGzip" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16}" href="${base_url}?offset=0&length=2000&mode=${view['mode']}&compression=gzip">Preview As Gzip</a>
      % endif

      % if view['compression'] and view['compression'] != "none":
        <a class="fv-viewGzip" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16}" href="${base_url}?offset=0&length=2000&mode=${view['mode']}&compression=none">Stop preview</a>
      % endif

      % if editable and view['compression'] == "none":
        <a class="fv-editFile" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16}" href="${url('filebrowser.views.edit', path=path_enc)}" target="FileEditor">Edit File</a>
      % endif
       <a class="fv-download" data-filters="ArtButton" target="_blank" data-icon-styles="{'width': 16, 'height': 16}" href="${url('filebrowser.views.download', path=path_enc)}">Download</a>
       <a class="fv-viewLocation" data-filters="ArtButton" data-icon-styles="{'width': 16, 'height': 16}" href="${url('filebrowser.views.view', path=dirname_enc)}" target="FileBrowser">View File Location</a>
       <a class="ccs-refresh large" data-filters="ArtButton">Refresh</a>
    </div>
  </div>
  <div class="fv-navhead">
    % if not view['compression'] or view['compression'] == "none":
      <div class="fv-navStatus">
        <form data-filters="SubmitOnChange" class="fv-changeBytesForm" action="${url('filebrowser.views.view', path=path_enc)}" method="GET">
          <span class="fv-bold">Viewing Bytes:</span><a class="fv-editBytes ccs-inline" title="Enter Bytes"></a>
          <input name="begin" value="${view['offset'] + 1}"/>
          -
          <input value="${view['end']}" name="end"/> of
          <span class="fv-bold totalBytes">${stats['size']}</span>
          <span class="fv-stepInfo">(${view['length']} B block size)</span>
          % if view['mode']:
            <input type="hidden" name="mode" value="${view['mode']}"/><br/>
          % endif
        </form>
      </div>
      <div class="fv-navigation">
        <%
          base_url = url('filebrowser.views.view', path=path_enc)
          if view['offset'] == 0:
              first = "style='visibility:hidden'"
              prev = "style='visibility:hidden'"
          else:
              first = "href='%s?offset=0&length=%d&compression=none' title='1 - %d'" %(base_url, view['length'], min(view['length'], stats['size']))
              prev =  "href='%s?offset=%d&length=%d&compression=none' title='%d - %d'" %(base_url, max(0, view['offset']-view['length']), view['length'], max(0, view['offset']-view['length']) + 1, min(max(0, view['offset'] - view['length']) + view['length'], stats['size']))
          if view['offset'] + view['length'] >= stats['size']:
              next = "style='visibility:hidden'"
              last = "style='visibility:hidden'"
          else:
              next = "href='%s?offset=%d&length=%d&compression=none' title='%d - %d'" %(base_url, view['offset'] + view['length'], view['length'], view['offset'] + view['length'] + 1, view['offset'] + (2 * view['length']))
              last =  "href='%s?offset=%d&length=%d&compression=none' title='%d - %d'" %(base_url, stats['size']-(stats['size'] % view['length']), view['length'], stats['size']-(stats['size'] % view['length']) + 1, stats['size'])
        %>
        ###DEFINE REL
        <a class="ccs-inline fv-firstBlock" data-filters="PointyTip" ${first}>First Block</a>
        <a class="ccs-inline fv-prevBlock" data-filters="PointyTip" ${prev}>Previous Block</a>
        <a class="ccs-inline fv-nextBlock" data-filters="PointyTip" ${next}>Next Block</a>
        <a class="ccs-inline fv-lastBlock" data-filters="PointyTip" ${last}>Last Block</a>
      </div>
    % endif
  </div>
  <div class="resizable" data-filters="SplitView" data-split-offset-y="36">
    <div class="left_col jframe_padded">
      <dl class="fv-fileInfo">
        <dt>Last Modified</dt>
        <dd>${date(datetime.datetime.fromtimestamp(stats['mtime']))} ${time(datetime.datetime.fromtimestamp(stats['mtime']))}</dd>
        <dt>User</dt>
        <dd>${stats['user']}<dd>
        <dt>Group</dt>
        <dd>${stats['group']}</dd>
        <dt>Size</dt>
        <dd>${stats['size']|filesizeformat}<dd>
        ## Could convert this to "rw-rw-r--" form.
        <dt>Mode</dt>
        <dd>${stringformat(stats['mode'], "o")}</dd>
        ## Could increase accuracy here depending on how long ago this was
      </dl>
    </div>
    <div class="right_col">
    %if 'contents' in view:
      % if view['masked_binary_data']:
      <div class="fv-binaryWarning">Warning: some binary data has been masked out with '&#xfffd'.</div>
      % endif
    % endif
      <div class="jframe_padded">
      % if 'contents' in view:
             <div><pre><code>${view['contents']|escape}</code></pre></div>
      % else:
        <table>
          % for offset, words, masked in view['xxd']:
            <tr>
              <td><tt>${stringformat(offset, "07x")}:&nbsp;</tt></td>
            <td>
              <tt>
                % for word in words:
                  % for byte in word:
                    ${stringformat(byte, "02x")}
                  % endfor
                % endfor
              </tt>
            </td>
            <td>
              <tt>
                &nbsp;&nbsp;${masked}
              </tt>
            </td>
            </tr>
          % endfor
        </table>
      % endif
      </div>
    </div>
  </div>
</body>
</html>

