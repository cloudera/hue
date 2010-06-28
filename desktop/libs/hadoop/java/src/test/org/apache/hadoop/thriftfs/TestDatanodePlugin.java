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

import java.util.List;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.commons.logging.impl.Log4JLogger;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.hdfs.MiniDFSCluster;
import org.apache.hadoop.thriftfs.api.Block;
import org.apache.hadoop.thriftfs.api.BlockData;
import org.apache.hadoop.thriftfs.api.Datanode;
import org.apache.hadoop.thriftfs.api.DatanodeInfo;
import org.apache.hadoop.thriftfs.api.Namenode;
import org.apache.hadoop.thriftfs.api.RequestContext;
import org.apache.log4j.Level;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Unit tests for the datanode Thrift interface
 */
public class TestDatanodePlugin  {
  private static MiniDFSCluster cluster;
  private static FileSystem fs;
  private static Namenode.Client namenode;
  private Datanode.Client datanode;
  private static RequestContext ctx;

  private static final String testFile = "/test-file";
  private static Path testFilePath = new Path(testFile);
  private static final short REPLICATION = 3;
  private final int BUFFER_SIZE = 4096;
  private final int BLOCK_SIZE = 8192;

  private static final Log LOG = LogFactory.getLog(TestDatanodePlugin.class);

  // Raise verbosity level of Thrift classes.
  static {
    ((Log4JLogger) DatanodePlugin.LOG).getLogger().setLevel(Level.ALL);
    ((Log4JLogger) NamenodePlugin.LOG).getLogger().setLevel(Level.ALL);
    ((Log4JLogger) ThriftPluginServer.LOG).getLogger().setLevel(Level.ALL);
    ((Log4JLogger) ThriftUtils.LOG).getLogger().setLevel(Level.ALL);
  }

  @BeforeClass
  public static void setUp() throws Exception {
    cluster = Helper.createCluster(REPLICATION);
    fs = cluster.getFileSystem();
    Configuration conf = Helper.createConf();
    namenode = ThriftUtils.createNamenodeClient(conf);
    ctx = Helper.createRequestContext(true);
  }

  @AfterClass
  public static void tearDown() throws Exception {
    fs.delete(testFilePath, false);
    cluster.shutdown();
  }
  
  @Test
  public void testRead() throws Exception {
    createFile(32);
    List<Block> blocks = namenode.getBlocks(ctx, testFile, 0, 32);
    assertEquals(1, blocks.size());

    Block b = blocks.get(0);
    LOG.debug("Got block: " + b);
    assertEquals(REPLICATION, b.nodes.size());
    DatanodeInfo node = b.nodes.get(0);
    datanode = Helper.createDatanodeClient(node);

    BlockData blockData = datanode.readBlock(ctx, b, 0, 32);
    LOG.debug("Read block: " + blockData);
    assertEquals("0000 - Thirty-two bytes in a row",
        new String(blockData.data));

    createFile(BLOCK_SIZE + 32);
    blocks = namenode.getBlocks(ctx, testFile, 0, BLOCK_SIZE + 32);
    assertEquals(2, blocks.size());

    b = blocks.get(0);
    assertEquals(REPLICATION, b.nodes.size());
    node = b.nodes.get(0);
    datanode = Helper.createDatanodeClient(node);

    blockData = datanode.readBlock(ctx, b, 0, BLOCK_SIZE);
    assertEquals(BLOCK_SIZE, blockData.length);
    String data = new String(blockData.data);
    assertTrue(data.startsWith("0000 - Thirty-two bytes in a row"));
    assertTrue(data.endsWith("0255 - Thirty-two bytes in a row"));

    blockData = datanode.readBlock(ctx, b, 32, 32);
    assertEquals(32, blockData.length);
    assertEquals("0001 - Thirty-two bytes in a row",
        new String(blockData.data));

    b = blocks.get(1);
    blockData = datanode.readBlock(ctx, b, 0, 32);
    assertEquals(32, blockData.length);
    assertEquals("0256 - Thirty-two bytes in a row",
        new String(blockData.data));
  }

  private void createFile(int length) throws Exception {
    LOG.debug("Creating " + testFilePath);
    FSDataOutputStream out = fs.create(testFilePath, true, BUFFER_SIZE,
        REPLICATION, BLOCK_SIZE);
    out.write(testData(length));
    LOG.debug("Closing " + testFilePath);
    out.close();

    assertTrue(fs.exists(testFilePath));
    FileStatus st = fs.getFileStatus(testFilePath);
    assertEquals(length, st.getLen());
  }

  private byte[] testData(int length) {
    assertTrue("Invalid data length", length % 32 == 0);

    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < length / 32; ++i) {
      sb.append(String.format("%04d - Thirty-two bytes in a row", i));
    }
    return sb.toString().getBytes();
  }
}
