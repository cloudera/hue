/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.hadoop.thriftfs;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.thriftfs.api.RequestContext;

/**
 * Helper class to create Thrift clients.
 */
public class Helper {

  public static final String TEST_USER="hadoop";
  public static final String TEST_GROUP="supergroup";

  /** Create a configuration object for the unit tests. */
  public static Configuration createConf() {
    Configuration conf = new Configuration();
    conf.set(ThriftFsConfig.DFS_THRIFT_ADDR_KEY, "127.0.0.1:10090");
    conf.set(ThriftFsConfig.DFS_THRIFT_DATANODE_ADDR_KEY, "127.0.0.1:0");
    conf.set("slave.host.name", "127.0.0.1");
    conf.setBoolean("dfs.permissions", true);
    conf.setBoolean("dfs.support.append", true);

    return conf;
  }

  public static RequestContext createRequestContext(boolean superuser) throws IOException {
    RequestContext ctx = new RequestContext();
    Configuration conf = new Configuration();

    UserGroupInformation ugi;
    if (superuser) {
      ugi = UserGroupInformation.getCurrentUser();
    } else {
      ugi = UserGroupInformation.createUserForTesting(TEST_USER, new String[] { TEST_GROUP });
    }

    ctx.confOptions = new HashMap<String, String>();
    for (Map.Entry<String, String> entry : conf) {
      ctx.confOptions.put(entry.getKey(), entry.getValue());
    }
    List<String> groupList = new ArrayList<String>();
    for (String group : ugi.getGroupNames())
      groupList.add(group);
    ctx.confOptions.put("effective_user", ugi.getUserName());
    return ctx;
  }

  /** Create a file on the default file system. */
  public static void createFile(FileSystem fs, String path, short repl,
      short perms, long blockSize, int length) throws Exception {

    Path p = new Path(path);
    FSDataOutputStream out = fs.create(p, true, 4096, repl, blockSize);
    byte[] buf = new byte[length];
    new Random(System.currentTimeMillis()).nextBytes(buf);
    out.write(buf, 0, length);
    out.close();
    fs.setPermission(p, new FsPermission(perms));
    fs.setOwner(p, TEST_USER, TEST_GROUP);
  }
}
