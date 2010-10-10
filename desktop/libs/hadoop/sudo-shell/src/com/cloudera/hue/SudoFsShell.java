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
package com.cloudera.hue;

import org.apache.hadoop.fs.FsShell;
import org.apache.hadoop.security.UserGroupInformation;
import java.security.PrivilegedExceptionAction;

/**
 * Tool that allows a user with proxyuser privileges to act on behalf
 * of another user on HDFS. Hue currently uses this tool in order to
 * upload files using the "-put" shell command on behalf of the logged-in
 * user.
 */
public class SudoFsShell {
  private static void usage() {
    System.err.println("usage: SudoFsShell <username> <shell args ...>");
  }

  public static void main(String []args) throws Exception {
    if (args.length < 1) {
      usage();
      System.exit(1);
    }

    String username = args[0];
    final String shellArgs[] = new String[args.length - 1];
    System.arraycopy(args, 1, shellArgs, 0, args.length - 1);

    UserGroupInformation sudoUgi;
    if (UserGroupInformation.isSecurityEnabled()) {
      sudoUgi = UserGroupInformation.createProxyUser(
        username, UserGroupInformation.getCurrentUser());
    } else {
      sudoUgi = UserGroupInformation.createRemoteUser(username);
    }

    sudoUgi.doAs(new PrivilegedExceptionAction<Void>() {
        public Void run() throws Exception {
          FsShell.main(shellArgs);
          return null;
        }
      });
  }
}
