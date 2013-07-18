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
  },
  setCluster: function(cluster) {
    Router.set();
    app.cluster(cluster);
  },
  set: function() {
      Breadcrumbs.render();
  }
}

var Breadcrumbs = {
  _selector_root:'#hbase-breadcrumbs',
  //renders breadcrumbs automaticall
  render:function(mutators) {
    root = $(Breadcrumbs._selector_root).html('');
    crumbs = ['/hbase'].concat(document.URL.split('/').splice(4));
    biglink = "";
    for(i=0;i<crumbs.length;i++) {
      biglink += crumbs[i] + '/'
      function clean_url(url) {
        replacers = {'/': '', '#': '', '_': ' ', '^[a-z]': function(a) { return a.toUpperCase(); }};
        keys = Object.keys(replacers);
        for(q=0;q<keys.length;q++) {
          url = url.replace(new RegExp(keys[q],'g'), replacers[keys[q]]);
        }
        return url;
      }
      if(crumbs[i]!="")
        root.append('<li><a href="' + biglink + '">' + clean_url(crumbs[i]) + '</a></li><li><a href="' + biglink + '">/</a></li>');
    }
    return root.find('li:last-child').remove();
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