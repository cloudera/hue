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
  from desktop.views import commonheader, commonfooter
  from django.utils.translation import ugettext as _
%>

<%namespace name="layout" file="../navigation-bar.mako" />
<%namespace name="utils" file="../utils.inc.mako" />

${ commonheader(_("Create Bundle"), "oozie", user, request) | n,unicode }
${ layout.menubar(section='bundles') }


<div class="container-fluid">
  <form class="form-horizontal" id="bundleForm" action="${ url('oozie:create_bundle') }" method="POST">
    ${ csrf_token(request) | n,unicode }
    <div class="row-fluid">
      <div class="span2">
        <div class="sidebar-nav">
          <ul class="nav nav-list">
            <li class="nav-header">${ _('Properties') }</li>
            <li class="active"><a href="#properties"><i class="fa fa-reorder"></i> ${ _('Edit properties') }</a></li>
          </ul>
        </div>
      </div>
      <div class="span10">
        <div class="card card-small">
          <h1 class="card-heading simple">${ _('Create Bundle') }</h1>
          <div class="alert alert-info"><h3>${ _('Bundle data') }</h3></div>
          <fieldset>
            ${ utils.render_field(bundle_form['name']) }
            ${ utils.render_field(bundle_form['description']) }
            ${ utils.render_field(bundle_form['kick_off_time']) }
            <div class="hide">
              ${ utils.render_field(bundle_form['is_shared']) }
            </hide>

            ${ bundle_form['schema_version'] | n,unicode }
            ${ bundle_form['parameters'] | n,unicode }
          </fieldset>
          <div class="form-actions">
            <input class="btn btn-primary" type="submit" value="${ _('Save') }" />
            <a class="btn" onclick="history.back()">${ _('Back') }</a>
          </div>
        </div>
      </div>
    </div>
  </form>
</div>

${ utils.decorate_datetime_fields(False) }

${ commonfooter(request, messages) | n,unicode }
