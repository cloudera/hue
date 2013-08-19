// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

var Router = {
  go: function(page) {
    if(!Views.render(page))
      return history.back();
    return page;
  },
  setTable: function(cluster, table) {
    Router.setCluster(cluster);
    app.pageTitle(cluster + ' / ' + table);
    app.views.tabledata.name(table);
    app.focusModel(app.views.tabledata);

    var bulkUploader = new qq.FileUploaderBasic({
      button: document.getElementById("bulk-upload-btn"),
      action: '/hbase/api/bulkUpload/"' + app.cluster() + '"/"' + app.views.tabledata.name() + '"',
      fileFieldLabel: 'hbase_file',
      multiple: false,
      onComplete: function (id, fileName, response) {
        if(response.response != null)
          $.jHueNotify.error($(response.response).find('.alert strong').text());
        else
          app.views.tabledata.reload();
      }
    });
  },
  setCluster: function(cluster) {
    app.cluster(cluster);
  }
}

var Views = {
  render:function(view) {
    page = $('.hbase-page#hbase-page-' + view);
    if(!page)
      return false;
    $('.hbase-page.active').removeClass('active');
    page.addClass('active');
    return page;
  },
  displayError:function(error) {
    console.log(error);
  }
}