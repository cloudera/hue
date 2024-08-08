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
  from desktop.webpack_utils import get_hue_bundles
  from webpack_loader.templatetags.webpack_loader import render_bundle
%>

% for bundle in get_hue_bundles('storageBrowser'):
    ${ render_bundle(bundle) | n,unicode }
% endfor

<StorageBrowserPage data-reactcomponent='StorageBrowserPage'></StorageBrowserPage>
