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
<%namespace name="common" file="workflow-common.xml.mako" />
<%!
try:
    import json
except ImportError:
    import simplejson as json
%>
<%
    java = design.get_root_action()
    properties = json.loads(java.job_properties)
    files = json.loads(java.files)
    archives = json.loads(java.archives)
%>
<workflow-app xmlns="uri:oozie:workflow:0.2" name="${design.name}">
    <start to="root-node"/>
    <action name="root-node">
        <java>
            ## Do not hardcode the jobtracker/resourcemanager address.
            ## We want to be flexible where to submit it to.
            <job-tracker>${'${'}jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>

            ${common.configuration(properties)}

            <main-class>${java.main_class}</main-class>
            %for arg in java.args.split():
            <arg>${arg}</arg>
            %endfor

            %if len(java.java_opts):
            <java-opts>${java.java_opts}</java-opts>
            %endif

            ${common.distributed_cache(files, archives)}
        </java>
        <ok to="end"/>
        <error to="fail"/>
    </action>
    <kill name="fail">
        <message>Java failed, error message[${'${'}wf:errorMessage(wf:lastErrorNode())}]</message>
    </kill>
    <end name="end"/>
</workflow-app>
