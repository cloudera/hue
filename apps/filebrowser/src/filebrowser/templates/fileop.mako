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
%>

<html>
<head><title>File Operation</title></head>
<body>
<h1>${form.op}</h1>
## Not sure if enctype breaks anything if used for things other than file upload.
<form action="" method="POST" enctype="multipart/form-data">
${form.as_p()|n}
<input type="submit" value="Submit" />
Go back to where you were: <a href="${urlencode(next)}">${next}</a>.
</form>
</body>
</html>
