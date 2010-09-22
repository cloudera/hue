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

import java.util.ArrayList;
import java.util.List;

import org.apache.commons.logging.impl.Log4JLogger;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.hdfs.MiniDFSCluster;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.thriftfs.api.Block;
import org.apache.hadoop.thriftfs.api.Constants;
import org.apache.hadoop.thriftfs.api.ContentSummary;
import org.apache.hadoop.thriftfs.api.IOException;
import org.apache.hadoop.thriftfs.api.Namenode;
import org.apache.hadoop.thriftfs.api.RequestContext;
import org.apache.hadoop.thriftfs.api.Stat;
import org.apache.log4j.Level;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import static org.junit.Assert.*;

/**
 * Unit tests for the name node Thrift interface
 */
public class TestNamenodePlugin {

  private static MiniDFSCluster cluster;
  private static Namenode.Client namenode;
  private static RequestContext ctx;
  private static RequestContext unprivilegedCtx;
  private static FileSystem fs;

  private static final short REPLICATION = 3;

  private static final String testFile = "/test-file";
  private static Path testFilePath = new Path(testFile);
  private final short PERMS = (short) 0644;

  // Raise verbosity level of Thrift classes.
  static {
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
    unprivilegedCtx = Helper.createRequestContext(false);
  }

  @AfterClass
  public static void tearDown() throws Exception {
    cluster.shutdown();
  }
  
  @After
  public void cleanup() throws Exception {
    fs.delete(testFilePath, false);
  }

  @Test
  public void testChmod() throws Exception {
    assertFalse(fs.exists(testFilePath));
    Helper.createFile(fs, testFile, REPLICATION, PERMS, 1024, 0);
    assertTrue(fs.exists(testFilePath));
    assertEquals(PERMS,
        fs.getFileStatus(testFilePath).getPermission().toShort());

    namenode.chmod(ctx, testFile, (short) 0600);
    assertEquals((short) 0600,
        fs.getFileStatus(testFilePath).getPermission().toShort());
  }

  @Test
  public void testChown() throws Exception {
    Helper.createFile(fs, testFile, REPLICATION, PERMS, 1024, 0);
    assertTrue(fs.exists(testFilePath));
    FileStatus st = fs.getFileStatus(testFilePath);
    assertEquals(Helper.TEST_USER, st.getOwner());
    assertEquals(Helper.TEST_GROUP, st.getGroup());

    namenode.chown(ctx, testFile, "foo", null);
    st = fs.getFileStatus(testFilePath);
    assertEquals("foo", st.getOwner());
    assertEquals(Helper.TEST_GROUP, st.getGroup());

    namenode.chown(ctx, testFile, null, "foo-group");
    st = fs.getFileStatus(testFilePath);
    assertEquals("foo", st.getOwner());
    assertEquals("foo-group", st.getGroup());

    try {
      namenode.chown(ctx, testFile, null, null);
      fail("chmod() needs non-null owner or group");
    } catch (IOException e) {
    }
  }

  @Test
  public void testDf() throws Exception {
    List<Long> st = namenode.df(ctx);
    assertNotNull(st);
    assertEquals(3, st.size());
    for (long val : st) {
      assertTrue(val > 0);
    }
  }

  @Test
  public void testGetPreferredBlockSize() throws Exception {
    long bs = 1024;
    Helper.createFile(fs, testFile, REPLICATION, PERMS, bs, 0);
    assertTrue(fs.exists(testFilePath));
    assertEquals(bs, namenode.getPreferredBlockSize(ctx, testFile));

    bs /= 2;
    assertTrue(namenode.unlink(ctx, testFile, false));
    Helper.createFile(fs, testFile, REPLICATION, PERMS, bs, 0);
    assertTrue(fs.exists(testFilePath));
    assertEquals(bs, namenode.getPreferredBlockSize(ctx, testFile));
  }

  @Test
  public void testLs() throws Exception {
    List<Stat> dir = namenode.ls(ctx, "/");
    assertEquals(0, dir.size());

    assertTrue(namenode.mkdirhier(ctx, "/foo", (short) 0755));
    dir = namenode.ls(ctx, "/");
    assertEquals(1, dir.size());
    assertEquals(true, dir.get(0).isDir);

    Helper.createFile(fs, testFile, REPLICATION, PERMS, 1024, 0);
    assertTrue(fs.exists(testFilePath));
    dir = namenode.ls(ctx, "/");
    assertEquals(2, dir.size());
    assertTrue(dir.get(0).isDir != dir.get(1).isDir);
    assertTrue(namenode.unlink(ctx, "/foo", true));
  }

  @Test
  public void testMkdirhier() throws Exception {
    String foo = "/foo";
    short perms = (short) 0755;
    Path fooPath = new Path(foo);
    assertFalse(fs.exists(fooPath));

    assertTrue(namenode.mkdirhier(ctx, foo, perms));
    assertTrue(fs.exists(fooPath));
    assertTrue(namenode.mkdirhier(ctx, foo, perms));
    assertTrue(namenode.unlink(ctx, foo, true));

    String bar = "/bar/baz";
    Path barPath = new Path(bar);
    assertFalse(fs.exists(barPath));
    assertTrue(namenode.mkdirhier(ctx, bar, perms));
    assertTrue(fs.exists(barPath));
    assertTrue(namenode.mkdirhier(ctx, bar, perms));
    assertTrue(namenode.unlink(ctx, bar, true));
  }

  @Test
  public void testRefreshNodes() throws Exception {
    // XXX This does not test much...
    namenode.refreshNodes(ctx);
  }

  @Test
  public void testRename() throws Exception {
    String foo = "/foo";
    short perms = (short) 0755;
    Path fooPath = new Path(foo);
    assertTrue(namenode.mkdirhier(ctx, foo, perms));
    assertTrue(fs.exists(fooPath));

    assertFalse(namenode.rename(ctx, foo, foo));
    String bar = "/bar";
    Path barPath = new Path(bar);
    assertTrue(namenode.rename(ctx, foo, bar));
    assertTrue(fs.exists(barPath));
    assertFalse(fs.exists(fooPath));

    assertFalse(fs.exists(fooPath));
    assertFalse(namenode.rename(ctx, bar, "/foo/baz"));
    assertTrue(namenode.unlink(ctx, bar, true));

    assertFalse(fs.exists(testFilePath));
    Helper.createFile(fs, testFile, REPLICATION, PERMS, 1024, 0);
    assertTrue(fs.exists(testFilePath));

    assertTrue(namenode.mkdirhier(ctx, "/foo/baz", PERMS));
    String newTestFile = "/foo/baz" + testFile;
    Path newTestFilePath = new Path(newTestFile);
    assertFalse(fs.exists(newTestFilePath));
    assertTrue(namenode.rename(ctx, testFile, newTestFile));
    assertTrue(fs.exists(newTestFilePath));
    assertFalse(fs.exists(testFilePath));

    assertTrue(namenode.mkdirhier(ctx, foo, perms));
    assertTrue(fs.exists(fooPath));
    assertTrue(fs.getFileStatus(fooPath).isDir());
    assertTrue(namenode.rename(ctx, newTestFile, foo));
    // XXX Bug or feature?
    assertTrue(fs.getFileStatus(fooPath).isDir());

    assertTrue(namenode.unlink(ctx, foo, true));
  }

  @Test
  public void testReportBadBlocks() throws Exception {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < 100; ++i) {
      sb.append("Blah blah blah");
    }
    String data = sb.toString();
    FSDataOutputStream out = fs.create(testFilePath, true, 512, REPLICATION,
        512);
    out.writeBytes(data);
    out.close();

    // Block here are Thrift blocks
    List<Block> blocks = namenode.getBlocks(ctx, testFile, 0, data.length());
    assertTrue(blocks.size() > 0);
    assertEquals(REPLICATION, blocks.get(0).nodes.size());

    List<Block> badBlocks = new ArrayList<Block>();
    Block b = blocks.get(0);
    assertEquals(REPLICATION, b.nodes.size());
    b.nodes.remove(0);
    badBlocks.add(b);
    namenode.reportBadBlocks(ctx, badBlocks);

    blocks = namenode.getBlocks(ctx, testFile, 0, data.length());
    assertTrue(blocks.size() > 0);
    assertTrue(blocks.get(0).nodes.size() < REPLICATION);
  }

  @Test
  public void testSafeMode() throws Exception {
    assertFalse(namenode.isInSafeMode(ctx));
    Helper.createFile(fs, testFile, REPLICATION, PERMS, 1024, 0);
    assertTrue(fs.exists(testFilePath));
    assertTrue(namenode.unlink(ctx, testFile, false));

    namenode.enterSafeMode(ctx);
    assertTrue(namenode.isInSafeMode(ctx));
    try {
      Helper.createFile(fs, testFile, REPLICATION, PERMS, 1024, 0);
      fail("create() must fail when cluster is in safe mode");
    } catch (Throwable t) {
    }

    namenode.leaveSafeMode(ctx);
    assertFalse(namenode.isInSafeMode(ctx));
  }

  @Test
  public void testSetQuota() throws Exception {
    try {
      namenode.setQuota(ctx, "/not-there", 1, Constants.QUOTA_DONT_SET);
      fail("cannot setQuota() on non-existing directories");
    } catch (IOException e) {}

    Helper.createFile(fs, testFile, REPLICATION, PERMS, 1024, 0);
    assertTrue(fs.exists(testFilePath));
    try {
      namenode.setQuota(ctx, testFile, 1, Constants.QUOTA_DONT_SET);
      fail("cannot setQuota() on files");
    } catch (IOException e) {}

    short perms = (short) 0755;
    namenode.mkdirhier(ctx, "/foo", perms);
    namenode.setQuota(ctx, "/foo", 2, Constants.QUOTA_DONT_SET);

    namenode.mkdirhier(ctx, "/foo/one", perms);
    try {
      namenode.mkdirhier(ctx, "/foo/two", perms);
      fail("namespaceQuota not set");
    } catch (IOException e) {}

    namenode.setQuota(ctx, "/foo", 3, Constants.QUOTA_DONT_SET);
    assertTrue(namenode.mkdirhier(ctx, "/foo/two", perms));
    assertTrue(namenode.unlink(ctx, "/foo", true));
  }

  @Test
  public void testSetReplication() throws Exception {
    short repl = (short) (REPLICATION - 1);
    Helper.createFile(fs, testFile, repl, PERMS, 1024, 0);
    assertTrue(fs.exists(testFilePath));
    FileStatus st = fs.getFileStatus(testFilePath);
    assertEquals(repl, st.getReplication());

    assertTrue(namenode.setReplication(ctx, testFile, REPLICATION));
    st = fs.getFileStatus(testFilePath);
    assertEquals(REPLICATION, st.getReplication());
  }

  @Test
  public void testStat() throws Exception {
    Stat st = namenode.stat(ctx, "/");
    assertEquals("/", st.path);
    assertTrue(st.isDir);
    long now = System.currentTimeMillis();
    Thread.sleep(10);
    assertTrue(st.mtime < now);
    assertTrue(st.atime < now);

    long then = now;
    assertFalse(fs.exists(testFilePath));
    Helper.createFile(fs, testFile, REPLICATION, PERMS, 1024, 0);
    assertTrue(fs.exists(testFilePath));

    st = namenode.stat(ctx, testFile);
    assertEquals(testFile, st.path);
    assertFalse(st.isDir);
    now = System.currentTimeMillis();
    Thread.sleep(10);
    assertTrue(st.atime > then);
    assertTrue(st.mtime > then);
    assertTrue(now > st.atime);
    assertTrue(now > st.mtime);
    assertEquals(1024, st.blockSize);
    assertEquals(REPLICATION, st.replication);
    assertEquals(0, st.length);

    try {
      st = namenode.stat(ctx, "/not-there");
      fail("No exception thrown for statting a non-existent file. " +
           "Instead, got: " + String.valueOf(st));
    } catch (IOException fne) {
      assertEquals("java.io.FileNotFoundException", fne.clazz);
    }
  }

  @Test
  public void testContentSummary() throws Exception {
    ContentSummary cs = namenode.getContentSummary(ctx, "/");
    assertEquals(1, cs.directoryCount);
    assertEquals(0, cs.fileCount);
  }

  @Test
  public void testUnlink() throws Exception {
    assertFalse(namenode.unlink(ctx, "/", true));

    assertFalse(fs.exists(testFilePath));
    assertFalse(namenode.unlink(ctx, testFile, false));

    Helper.createFile(fs, testFile, REPLICATION, PERMS, 1024, 0);
    assertTrue(fs.exists(testFilePath));
    assertTrue(namenode.unlink(ctx, testFile, false));

    assertTrue(namenode.mkdirhier(ctx, "/foo", (short) 0755));
    assertTrue(namenode.unlink(ctx, "/foo", false));

    assertTrue(namenode.mkdirhier(ctx, "/foo", (short) 0755));
    Path newTestFile = new Path("/foo/test-file");
    Helper.createFile(fs, "/foo/test-file", REPLICATION, PERMS, 1024, 0);
    assertTrue(fs.exists(newTestFile));
    try {
      namenode.unlink(ctx, "/foo", false);
      fail("unlink(path, recursive=false) must fail for non-empty paths");
    } catch (IOException e) {
    }
    assertTrue(namenode.unlink(ctx, "/foo", true));
  }

  @Test
  public void testUtime() throws Exception {
    long tstamp = System.currentTimeMillis();
    Helper.createFile(fs, testFile, REPLICATION, PERMS, 1024, 0);
    assertTrue(fs.exists(testFilePath));

    FileStatus st = fs.getFileStatus(testFilePath);
    assertTrue(st.getAccessTime() >= tstamp);
    assertTrue(st.getModificationTime() >= tstamp);

    Thread.sleep(10);
    tstamp = System.currentTimeMillis();
    namenode.utime(ctx, testFile, -1, tstamp);
    st = fs.getFileStatus(testFilePath);
    assertTrue(st.getAccessTime() < tstamp);
    assertTrue(st.getModificationTime() == tstamp);

    Thread.sleep(10);
    tstamp = System.currentTimeMillis();
    namenode.utime(ctx, testFile, tstamp, -1);
    st = fs.getFileStatus(testFilePath);
    assertTrue(st.getAccessTime() == tstamp);
    assertTrue(st.getModificationTime() < tstamp);

    long prev = tstamp;
    namenode.utime(ctx, testFile, -1, -1);
    Thread.sleep(10);
    tstamp = System.currentTimeMillis();
    st = fs.getFileStatus(testFilePath);
    assertTrue(st.getModificationTime() < tstamp);
    assertTrue(st.getModificationTime() >= prev);
    assertTrue(st.getAccessTime() < tstamp);
    assertTrue(st.getAccessTime() >= prev);
    assertTrue(st.getAccessTime() == st.getModificationTime());
  }

  /**
   * Ensure that RPCs can spoof as different users using RequestContexts
   */
  @Test
  public void testRequestContext() throws Exception {
    Path byCurrentPath = new Path("/test-by-current");
    Path byOtherPath = new Path("/test-by-other");

    assertFalse(fs.exists(byCurrentPath));
    assertFalse(fs.exists(byOtherPath));

    // Dir made by 'ctx' should be owned by the current user
    namenode.mkdirhier(ctx, "/test-by-current", (short)0755);
    assertEquals(UserGroupInformation.getCurrentUser().getUserName(),
                 fs.getFileStatus(byCurrentPath).getOwner());

    // With a null context (eg clients that don't support this), should be
    // the current user
    assertTrue(fs.delete(byCurrentPath, true));
    namenode.mkdirhier(null, "/test-by-current", (short)0755);
    assertEquals(UserGroupInformation.getCurrentUser().getUserName(),
                 fs.getFileStatus(byCurrentPath).getOwner());


    // Dir made by unprivelegedCtx should be owned by the test user
    namenode.mkdirhier(unprivilegedCtx, "/test-by-other", (short)0755);
    assertEquals(Helper.TEST_USER, fs.getFileStatus(byOtherPath).getOwner());
  }
}
