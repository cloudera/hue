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
package com.cloudera.jobsub;

import org.apache.hadoop.security.UnixUserGroupInformation;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/**
 * Overrides the 'whoami' and 'groups' calls that Hadoop does with
 * environment variables, specifying the username and group.
 */
public aspect UgiFixer {
  private static final Log LOG = LogFactory.getLog(UgiFixer.class);
  private static final String USER_VAR = "HUE_JOBSUB_USER";
  private static final String DEFAULT_USER = "default_jobsub_user";
  
  // TODO(philip): Full-on group support would mean
  // dealing with comma-delimited values here.
  private static final String GROUPS_VAR = "HUE_JOBSUB_GROUPS";
  private static final String DEFAULT_GROUP = "default_jobsub_group";

  UgiFixer() {
    LOG.info("Hue UGI fixer aspect loaded.");
  }

  pointcut getUserName():
        call(String UnixUserGroupInformation.getUnixUserName());

  pointcut getUnixGroups():
        call(String[] UnixUserGroupInformation.getUnixGroups());

  String around(): getUserName() {
    String user = System.getenv(USER_VAR);
    return user == null ? DEFAULT_USER : user;
  }

  String[] around(): getUnixGroups() {
    String group = System.getenv(GROUPS_VAR);
    if (group == null) {
      return new String[] { DEFAULT_GROUP };
    } else {
      return group.split(",");
    }
  }
}
