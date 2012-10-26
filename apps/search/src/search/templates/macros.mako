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
from django.utils.translation import ugettext as _
from itertools import izip
%>



<%def name="pairwise(iterable)">
  ##"s -> (s0,s1), (s2,s3), (s4, s5), ..."
  <%
    a = iter(iterable)
    return izip(a, a)
  %>
</%def>


<%def name="tweet_result(result)">
<tr>
    <td style="word-wrap: break-word;">
        ## TODO on hover username popover
        <div id="${ 'user-%s' % result.get('id', '') }" class="hide">
            ${ result.get('user_screen_name', '') } @${ result.get('user_name', '') }

            Description: ${ result.get('user_description', '') }
            Location: ${ result.get('user_location', '') }

            User tweets #: ${ result.get('user_statuses_count', '') }
            User followers #: ${ result.get('user_followers_count', '') }
        </div>

        <a rel="nofollow" href="https://twitter.com/${ result.get('user_screen_name', '') }"><b>${ result.get('user_name', '') }</b></a> @${ result.get('user_name', '') }
        <p>${ result.get('text', '') }</p>
        <p>
        % if result.get('features'):
            <ul>
            % for feature in result.get('features', ''):
                <li>${ feature }</li>
            % endfor
            </ul>
        % endif


        </p>
        <div style="color: #46a546;">
            Retweet: ${ result.get('retweet_count', '') }
            Location: ${ result.get('user_location', 'Unknown') or 'Unknown' }
            Date ${ result.get('created_at', '') }
        </div>
    </td>
</tr>
</%def>
