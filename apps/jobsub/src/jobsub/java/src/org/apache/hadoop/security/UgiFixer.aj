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
package org.apache.hadoop.security;

import java.security.Principal;
import java.util.HashMap;
import java.util.Map;

import javax.security.auth.Subject;
import javax.security.auth.callback.CallbackHandler;
import javax.security.auth.login.AppConfigurationEntry;
import javax.security.auth.login.AppConfigurationEntry.LoginModuleControlFlag;
import javax.security.auth.login.LoginException;
import javax.security.auth.login.Configuration;
import javax.security.auth.spi.LoginModule;

import org.apache.hadoop.security.User;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/**
 * Overrides the HadoopConfiguration.getAppConfigurationEntry to return the
 * user that Jobsub is running this job as.
 */
public aspect UgiFixer {
  private static final Log LOG = LogFactory.getLog(UgiFixer.class);

  static {
    LOG.info("Hue UGI fixer aspect loaded.");
  }

  private static final String USER_VAR = "HUE_JOBSUB_USER";
  private static final String DEFAULT_USER = "default_jobsub_user";

  private static final AppConfigurationEntry JOBSUB_LOGIN =
    new AppConfigurationEntry(JobsubLoginModule.class.getName(),
                              LoginModuleControlFlag.REQUIRED,
                              new HashMap<String,String>());

  private static final AppConfigurationEntry[] JOBSUB_CONF =
    new AppConfigurationEntry[]{ JOBSUB_LOGIN };

  public static class JobsubLoginModule implements LoginModule {
    private Subject subject;

    public boolean abort() throws LoginException {
      return true;
    }

    public boolean commit() throws LoginException {
      if (!subject.getPrincipals(User.class).isEmpty()) {
        return true;
      }
      String user = System.getenv(USER_VAR);
      subject.getPrincipals().add(new User(user == null ? DEFAULT_USER : user));
      return true;
    }

    public void initialize(Subject subject, CallbackHandler callbackHandler,
                           Map<String, ?> sharedState, Map<String, ?> options) {
      this.subject = subject;
    }

    public boolean login() throws LoginException {
      return true;
    }

    public boolean logout() throws LoginException {
      return true;
    }
  }

  pointcut getAppConfigurationEntry(String appName):
    execution(AppConfigurationEntry[] Configuration.getAppConfigurationEntry(String)) && args(appName) && within(UserGroupInformation);

  AppConfigurationEntry[] around(String appName):
    getAppConfigurationEntry(appName) {
      if (!appName.equals("hadoop-simple")) {
        LOG.warn("getAppConfigurationEntry() called for auth method other than simple: " + appName);
        return proceed(appName);
      } else {
        return JOBSUB_CONF;
      }
    }
}
