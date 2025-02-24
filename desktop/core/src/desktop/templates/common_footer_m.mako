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
import sys
from django.http import HttpRequest
from django.template.defaultfilters import escape, escapejs

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _
%>



<script type="text/javascript">
  $(document).ready(function () {
    %if messages:
      %for message in messages:
        %if message.tags == 'error':
          huePubSub.publish('hue.global.error', {message: '${ escapejs(escape(message))}'});
        %elif message.tags == 'warning':
          huePubSub.publish('hue.global.warning', { message: '${ escapejs(escape(message)) }'});
        %else:
          huePubSub.publish('hue.global.info', { message: '${ escapejs(escape(message)) }'});
        %endif
      %endfor
    %endif
  });

  if (typeof nv != "undefined"){
    // hides all the nvd3 logs
    nv.log = function() {};
  }

</script>
  </body>
</html>
