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
${'<%'}!
#declare imports here, for example:
#import datetime
${'%>'}

${'<%'}!
import datetime
from django.template.defaultfilters import urlencode, escape
${'%>'}
${'<%'}def name="header(title='${app_name}', toolbar=True)">
  <!DOCTYPE html>
  <html>
    <head>
      <title>${'$'}{title}</title>
    </head>
    <body>
      ${'%'} if toolbar:
      <div class="toolbar">
        <a href="${'$'}{url('${app_name}.views.index')}"><img src="/${app_name}/static/art/${app_name}.png" class="${app_name}_icon"/></a>
      </div>
      ${'%'} endif
${'<'}/%def>

${'<%'}def name="footer()">
    </body>
  </html>
${'<'}/%def>