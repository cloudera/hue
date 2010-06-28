/**
 * Licensed to the Apache Software Foundation (ASF) under one
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
import java.net.InetSocketAddress;
import java.net.URI;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import javax.security.auth.login.LoginException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.hdfs.DistributedFileSystem;
import org.apache.hadoop.hdfs.MiniDFSCluster;
import org.apache.hadoop.hdfs.protocol.FSConstants.DatanodeReportType;
import org.apache.hadoop.hdfs.protocol.FSConstants.SafeModeAction;
import org.apache.hadoop.security.UnixUserGroupInformation;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.thriftfs.api.Datanode;
import org.apache.hadoop.thriftfs.api.DatanodeInfo;
import org.apache.hadoop.thriftfs.api.RequestContext;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;

/**
 * Helper class to create Thrift clients.
 */
public class Helper {

  public static final String NAMENODE_ADDRESS_PROPERTY =
    org.apache.hadoop.thriftfs.NamenodePlugin.THRIFT_ADDRESS_PROPERTY;

  public static final String DATANODE_ADDRESS_PROPERTY =
    org.apache.hadoop.thriftfs.DatanodePlugin.THRIFT_ADDRESS_PROPERTY;

  public static final String TEST_USER="hadoop";
  public static final String TEST_GROUP="supergroup";

  /** Create a configuration object for the unit tests. */
  public static Configuration createConf() {
    Configuration conf = new Configuration();
    conf.set(NAMENODE_ADDRESS_PROPERTY, "127.0.0.1:9090");
    conf.set(DATANODE_ADDRESS_PROPERTY, "127.0.0.1:0");
    conf.set("slave.host.name", "127.0.0.1");
    conf.setStrings("dfs.namenode.plugins", NamenodePlugin.class.getName());
    conf.setStrings("dfs.datanode.plugins", DatanodePlugin.class.getName());
    conf.setBoolean("dfs.permissions", true);
    conf.setBoolean("dfs.support.append", true);

    return conf;
  }

  public static RequestContext createRequestContext(boolean superuser) {
    RequestContext ctx = new RequestContext();
    Configuration conf = new Configuration();

    UnixUserGroupInformation ugi;
    if (superuser) {
      try {
        ugi = UnixUserGroupInformation.login();
      } catch (LoginException le) {
        // we need to be able to determine the superuser for these
        // tests to work
        throw new RuntimeException(le);
      }
    } else {
      ugi = new UnixUserGroupInformation(
        TEST_USER, new String[] { TEST_GROUP });
    }

    UnixUserGroupInformation.saveToConf(
      conf, UnixUserGroupInformation.UGI_PROPERTY_NAME, ugi);

    ctx.confOptions = new HashMap<String, String>();
    for (Map.Entry<String, String> entry : conf) {
      ctx.confOptions.put(entry.getKey(), entry.getValue());
    }
    return ctx;
  }

  /** Create a DFS cluster. */
  public static MiniDFSCluster createCluster(short replication)
      throws IOException {
    Configuration conf = Helper.createConf();
    MiniDFSCluster cluster = new MiniDFSCluster(conf, replication, true, null);
    cluster.waitActive();
    return cluster;
  }

  /**
   * Creates a Thrift data node client.
   * 
   * @param addr address of the data node
   * @return a Thrift data node client.
   */
  public static Datanode.Client createDatanodeClient(DatanodeInfo node)
      throws Exception {
    InetSocketAddress addr = new InetSocketAddress(node.host, node.thriftPort);
    TTransport t = new TSocket(addr.getHostName(), addr.getPort());
    t.open();
    TProtocol p = new TBinaryProtocol(t);
    return new Datanode.Client(p);
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

  public static void main(String[] args) throws Exception {
    if (args.length != 4) {
      System.err.println("Usage: " + Helper.class.getSimpleName()
          + " <file name> <repl> <block size> <length>");
      System.exit(1);
    }

    Configuration.addDefaultResource("core-site.xml");
    Configuration.addDefaultResource("hdfs-site.xml");
    Configuration conf = new Configuration();

    DistributedFileSystem dfs = new DistributedFileSystem();
    dfs.initialize(new URI(conf.get("fs.default.name")), conf);

    for (;;) {
      if (!dfs.setSafeMode(SafeModeAction.SAFEMODE_GET)) {
        org.apache.hadoop.hdfs.protocol.DatanodeInfo[] nodes =
          dfs.getClient().namenode.getDatanodeReport(DatanodeReportType.LIVE);
        if (nodes.length > 0) {
          break;
        }
      }
      Thread.sleep(100);
    }

    createFile(dfs, args[0], Short.parseShort(args[1]),
        (short)0644, Long.parseLong(args[2]), Integer.parseInt(args[3]));
  }
}
