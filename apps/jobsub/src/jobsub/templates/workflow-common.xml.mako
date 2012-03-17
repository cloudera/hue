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
##
##
## no spaces in this method please; we're declaring a CSS class, and ART uses this value for stuff, and it splits on spaces, and 
## multiple spaces and line breaks cause issues
<%!
import posixpath
%> 

<%def name="filelink(path)">${path + '#' + posixpath.basename(path)}</%def>

## Please keep the indentation. The generated XML looks better that way.
<%def name="configuration(properties)">
        %if properties:
            <configuration>
                %for p in properties:
                <property>
                    <name>${p['name']}</name>
                    <value>${p['value']}</value>
                </property>
                %endfor
            </configuration>
        %endif
</%def>

## Please keep the indentation. The generated XML looks better that way.
<%def name="distributed_cache(files, archives)">
    %for f in files:
        %if len(f) != 0:
            <file>${f + '#' + posixpath.basename(f)}</file>
        %endif
    %endfor
    %for a in archives:
        %if len(a) != 0:
            <archive>${a}</archive>
        %endif
    %endfor
</%def>
