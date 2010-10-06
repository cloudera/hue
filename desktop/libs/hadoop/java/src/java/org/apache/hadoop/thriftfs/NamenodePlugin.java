/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
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

import java.io.FileNotFoundException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.security.PrivilegedAction;
import java.security.PrivilegedExceptionAction;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configurable;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.hdfs.protocol.DatanodeID;
import org.apache.hadoop.hdfs.protocol.DirectoryListing;
import org.apache.hadoop.hdfs.protocol.FSConstants;
import org.apache.hadoop.hdfs.protocol.HdfsFileStatus;
import org.apache.hadoop.hdfs.protocol.LocatedBlock;
import org.apache.hadoop.hdfs.protocol.LocatedBlocks;
import org.apache.hadoop.hdfs.protocol.FSConstants.SafeModeAction;
import org.apache.hadoop.hdfs.security.token.delegation.DelegationTokenIdentifier;
import org.apache.hadoop.hdfs.server.namenode.NameNode;
import org.apache.hadoop.io.DataOutputBuffer;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.security.Credentials;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.security.token.Token;
import org.apache.hadoop.thriftfs.api.Block;
import org.apache.hadoop.thriftfs.api.Constants;
import org.apache.hadoop.thriftfs.api.ContentSummary;
import org.apache.hadoop.thriftfs.api.IOException;
import org.apache.hadoop.thriftfs.api.Namenode;
import org.apache.hadoop.thriftfs.api.RequestContext;
import org.apache.hadoop.thriftfs.api.Stat;
import org.apache.hadoop.thriftfs.api.ThriftDelegationToken;
import org.apache.thrift.TException;
import org.apache.thrift.TProcessor;
import org.apache.thrift.TProcessorFactory;
import org.apache.thrift.transport.TTransport;

public class NamenodePlugin extends org.apache.hadoop.hdfs.server.namenode.NamenodePlugin implements
    Configurable {

  /** Name of the configuration property of the Thrift server address */
  public static final String THRIFT_ADDRESS_PROPERTY = "dfs.thrift.address";

  /**
   * Default address and port this server will bind to, in case nothing is found
   * in the configuration object.
   */
  public static final String DEFAULT_THRIFT_ADDRESS = "0.0.0.0:10090";

  private NameNode namenode;

  private static Map<DatanodeID, Integer> thriftPorts = Collections.synchronizedMap(new HashMap<DatanodeID, Integer>());

  static final Log LOG = LogFactory.getLog(NamenodePlugin.class);

  private Configuration conf;
  private ThriftPluginServer thriftServer;

  /** Java server-side implementation of the 'Namenode' Thrift interface. */
  class ThriftHandler extends ThriftHandlerBase implements Namenode.Iface {

    public ThriftHandler(ThriftServerContext context) {
      super(context);
    }

    public void chmod(RequestContext ctx, final String path, final short mode) throws IOException {
      LOG.debug("chmod(" + path + ", " + mode + "): Entering");
      assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
        public Void run() throws java.io.IOException {
          namenode.setPermission(path, new FsPermission(mode));
          return null;
        }
      });
    }

    public void chown(RequestContext ctx, final String path, final String owner, final String group)
        throws IOException {
      LOG.debug("chown(" + path + "," + owner + "," + group + "): Entering");
      assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
        public Void run() throws java.io.IOException {
          // XXX Looks like namenode.setOwner() does not complain about
          // this...
          if (owner == null && group == null) {
            throw new IllegalArgumentException("Both 'owner' and 'group' are null");
          }
          namenode.setOwner(path, owner, group);
          return null;
        }
      });
    }

    public List<Long> df(RequestContext ctx) {
      LOG.debug("Entering df()");
      return assumeUserContextAndExecute(ctx, new PrivilegedAction<List<Long>>() {
        public List<Long> run() {
          long[] stats = namenode.getStats();
          List<Long> ret = new ArrayList<Long>();
          // capacityTotal
          ret.add(stats[0]);
          // capacityUsed
          ret.add(stats[1]);
          // capacityRemaining
          ret.add(stats[2]);
          LOG.debug("df(): Returning " + ret);
          return ret;
        }
      });
    }

    public void enterSafeMode(RequestContext ctx) throws IOException {
      LOG.debug("enterSafeMode(): Entering");
      assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
        public Void run() throws java.io.IOException {
          namenode.setSafeMode(SafeModeAction.SAFEMODE_ENTER);
          return null;
        }
      });
    }

    public List<Block> getBlocks(RequestContext ctx, final String path, final long offset,
        final long length) throws IOException {
      LOG.debug("getBlocks(" + path + "," + offset + "," + length + "): Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<List<Block>>() {
        public List<Block> run() throws java.io.IOException {
          List<Block> ret = new ArrayList<Block>();
          LocatedBlocks blocks = namenode.getBlockLocations(path, offset, length);
          if (blocks != null) {
            // blocks may be null if offset is past the end of the file
            for (LocatedBlock b : blocks.getLocatedBlocks()) {
              ret.add(ThriftUtils.toThrift(b, path, thriftPorts));
            }
          }
          LOG.debug("getBlocks(" + path + "," + offset + "," + length + "): Returning " + ret);
          return ret;
        }
      });
    }

    public long getPreferredBlockSize(RequestContext ctx, final String path) throws IOException {
      LOG.debug("getPreferredBlockSize(" + path + "): Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Long>() {
        public Long run() throws java.io.IOException {
          long ret = namenode.getPreferredBlockSize(path);
          LOG.debug("getPreferredBlockSize(" + path + "): Returning " + ret);
          return ret;
        }
      });
    }

    public boolean isInSafeMode(RequestContext ctx) throws IOException {
      LOG.debug("isInSafeMode(): Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Boolean>() {
        public Boolean run() throws java.io.IOException {
          boolean ret = namenode.setSafeMode(SafeModeAction.SAFEMODE_GET);
          LOG.debug("isInSafeMode(): Returning " + ret);
          return ret;
        }
      });
    }

    public void leaveSafeMode(RequestContext ctx) throws IOException {
      LOG.debug("leaveSafeMode(): Entering");
      assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
        public Void run() throws java.io.IOException {
          namenode.setSafeMode(SafeModeAction.SAFEMODE_LEAVE);
          return null;
        }
      });
    }

    public List<Stat> ls(RequestContext ctx, final String path) throws IOException {
      LOG.debug("ls(" + path + "):Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<List<Stat>>() {
        public List<Stat> run() throws java.io.IOException {
          List<Stat> ret = new ArrayList<Stat>();
          byte[] lastReturnedName = HdfsFileStatus.EMPTY_NAME;
          DirectoryListing listing;
          do {
            listing = namenode.getListing(path, lastReturnedName);
            if (listing == null) {
              throw new FileNotFoundException("Not found: " + path);
            }
            for (HdfsFileStatus f : listing.getPartialListing()) {
              ret.add(fileStatusToStat(f, path));
            }
            lastReturnedName = listing.getLastName();
          } while (listing.hasMore());
          LOG.debug("ls(" + path + "): Returning " + ret);
          return ret;
        }
      });
    }

    public boolean mkdirhier(RequestContext ctx, final String path, final short perms)
        throws IOException {
      LOG.debug("mkdirhier(" + path + ", " + perms + "): Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Boolean>() {
        public Boolean run() throws java.io.IOException {
          boolean ret = namenode.mkdirs(path, new FsPermission(perms));
          LOG.debug("mkdirhier(" + path + ", " + perms + "): Returning " + ret);
          return ret;
        }
      });
    }

    public void refreshNodes(RequestContext ctx) throws IOException {
      LOG.debug("refreshNodes(): Entering");
      assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
        public Void run() throws java.io.IOException {
          namenode.refreshNodes();
          return null;
        }
      });
    }

    public boolean rename(RequestContext ctx, final String path, final String newPath)
        throws IOException {
      LOG.debug("rename(" + path + ", " + newPath + "): Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Boolean>() {
        public Boolean run() throws java.io.IOException {
          boolean ret = namenode.rename(path, newPath);
          LOG.debug("rename(" + path + ", " + newPath + "): Returning " + ret);
          return ret;
        }
      });
    }

    public void reportBadBlocks(RequestContext ctx, final List<Block> blocks) throws IOException {
      LOG.debug("reportBadBlocks(" + blocks + "): Entering");
      assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
        public Void run() throws java.io.IOException {
          int n = blocks.size();
          LocatedBlock[] lb = new LocatedBlock[n];
          for (int i = 0; i < n; ++i) {
            lb[i] = ThriftUtils.fromThrift(blocks.get(i));
          }
          namenode.reportBadBlocks(lb);
          return null;
        }
      });
    }

    public void setQuota(RequestContext ctx, final String path, long namespaceQuota,
        long diskspaceQuota) throws IOException {
      LOG.debug("setQuota(" + path + "," + namespaceQuota + "," + diskspaceQuota + "): Entering");
      if (namespaceQuota == Constants.QUOTA_DONT_SET) {
        namespaceQuota = FSConstants.QUOTA_DONT_SET;
      }
      if (namespaceQuota == Constants.QUOTA_RESET) {
        namespaceQuota = FSConstants.QUOTA_RESET;
      }
      if (diskspaceQuota == Constants.QUOTA_DONT_SET) {
        diskspaceQuota = FSConstants.QUOTA_DONT_SET;
      }
      if (diskspaceQuota == Constants.QUOTA_RESET) {
        diskspaceQuota = FSConstants.QUOTA_RESET;
      }
      final long finalNamespaceQuota = namespaceQuota;
      final long finalDiskspaceQuota = diskspaceQuota;
      assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
        public Void run() throws java.io.IOException {
          LOG.debug("setQuota(" + path + "," + finalNamespaceQuota + "," + finalDiskspaceQuota
              + "): Quota values translated");
          namenode.setQuota(path, finalNamespaceQuota, finalDiskspaceQuota);
          return null;
        }
      });
    }

    public boolean setReplication(RequestContext ctx, final String path, final short repl)
        throws IOException {
      LOG.debug("setReplication(" + path + "," + repl + "): Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Boolean>() {
        public Boolean run() throws java.io.IOException {
          return namenode.setReplication(path, repl);
        }
      });
    }

    public Stat stat(RequestContext ctx, final String path) throws IOException {
      LOG.debug("stat(" + path + "): Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Stat>() {
        public Stat run() throws java.io.IOException {
          Stat ret = fileStatusToStat(namenode.getFileInfo(path), path);
          LOG.debug("stat(" + path + "): Returning " + ret);
          return ret;
        }
      });
    }

    public ContentSummary getContentSummary(RequestContext ctx, final String path)
        throws IOException {
      LOG.debug("getContentSummary(" + path + "): Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<ContentSummary>() {
        public ContentSummary run() throws java.io.IOException {
          ContentSummary cs = getContentSummary(path);
          LOG.debug("getContentSummary(" + path + "): Returning " + cs);
          return cs;
        }
      });
    }

    public List<ContentSummary> multiGetContentSummary(RequestContext ctx, final List<String> paths)
        throws IOException {
      LOG.debug("multiGetContentSummary(" + paths + "): Entering");
      return assumeUserContextAndExecute(ctx,
          new PrivilegedExceptionAction<List<ContentSummary>>() {
            public List<ContentSummary> run() throws java.io.IOException {
              List<ContentSummary> ret = new ArrayList<ContentSummary>();
              for (String path : paths) {
                ret.add(getContentSummary(path));
              }
              LOG.debug("multiGetContentSummary(" + paths + "): Returning " + ret);
              return ret;
            }
          });
    }

    private ContentSummary getContentSummary(String path) throws java.io.IOException {
      return ThriftUtils.toThrift(namenode.getContentSummary(path), path);
    }

    public boolean unlink(RequestContext ctx, final String path, final boolean recursive)
        throws IOException {
      LOG.debug("unlink(" + path + "," + recursive + "): Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Boolean>() {
        public Boolean run() throws java.io.IOException, TException {
          boolean ret = namenode.delete(path, recursive);
          LOG.debug("unlink(" + path + "," + recursive + "): Returning " + ret);
          return ret;
        }
      });
    }

    public void utime(RequestContext ctx, final String path, final long atime, final long mtime)
        throws IOException {
      LOG.debug("utime(" + path + "," + atime + "," + mtime + "): Entering");
      assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
        public Void run() throws java.io.IOException {
          if (mtime == -1 && atime == -1) {
            LOG.debug("utime(" + path + "," + atime + "," + mtime
                + "): Setting mtime and atime to now");
            long now = System.currentTimeMillis();
            namenode.setTimes(path, now, now);
          } else {
            namenode.setTimes(path, mtime, atime);
          }
          return null;
        }
      });
    }

    private Stat fileStatusToStat(HdfsFileStatus f, String parentPath) throws java.io.IOException {
      if (f == null) {
        throw new FileNotFoundException();
      }

      Stat st = new Stat();
      st.path = f.getFullPath(new Path(parentPath)).toString();
      st.isDir = f.isDir();
      st.atime = f.getAccessTime();
      st.mtime = f.getModificationTime();
      st.perms = f.getPermission().toShort();
      st.owner = f.getOwner();
      st.group = f.getGroup();
      if (!st.isDir) {
        st.length = f.getLen();
        st.blockSize = f.getBlockSize();
        st.replication = f.getReplication();
      }
      return st;
    }

    public void datanodeDown(String name, String storage, int thriftPort) {
      DatanodeID dnId = new DatanodeID(name, storage, -1, -1);
      LOG.info("Datanode " + dnId + ": Thrift port " + thriftPort + " closed");
      thriftPorts.remove(dnId);
    }

    public void datanodeUp(String name, String storage, int thriftPort) {
      DatanodeID dnId = new DatanodeID(name, storage, -1, -1);
      LOG.info("Datanode " + dnId + ": " + "Thrift port " + thriftPort + " open");
      thriftPorts.put(dnId, thriftPort);
    }

    @Override
    public ThriftDelegationToken getDelegationToken(RequestContext ctx, final String renewer) throws IOException,
        TException {
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<ThriftDelegationToken>() {
        public ThriftDelegationToken run() throws java.io.IOException {
          Token<DelegationTokenIdentifier> delegationToken = namenode.getDelegationToken(new Text(renewer));
          return ThriftUtils.toThrift(delegationToken, namenode.getNameNodeAddress());
        }
      });
    }
  }

  public NamenodePlugin() {
  }

  @Override
  public void start(Object service) {
    this.namenode = (NameNode) service;
    try {
      InetSocketAddress address = NetUtils.createSocketAddr(conf.get(THRIFT_ADDRESS_PROPERTY,
          DEFAULT_THRIFT_ADDRESS));

      this.thriftServer = new ThriftPluginServer(address, new ProcessorFactory());
      thriftServer.setConf(conf);
      thriftServer.start();
      // The port may have been 0, so we update it.
      conf.set(THRIFT_ADDRESS_PROPERTY, address.getHostName() + ":" + thriftServer.getPort());
    } catch (Exception e) {
      throw new RuntimeException("Cannot start Thrift namenode plug-in", e);
    }
  }

  @Override
  public void stop() {
    if (thriftServer != null) {
      thriftServer.stop();
    }
  }

  @Override
  public void close() {
    if (thriftServer != null) {
      thriftServer.close();
    }
  }

  public Configuration getConf() {
    return conf;
  }

  public void setConf(Configuration conf) {
    this.conf = conf;
  }

  class ProcessorFactory extends TProcessorFactory {

    ProcessorFactory() {
      super(null);
    }

    @Override
    public TProcessor getProcessor(TTransport t) {
      ThriftServerContext context = new ThriftServerContext(t);
      Namenode.Iface impl =
        ThriftUtils.SecurityCheckingProxy.create(
          conf,
          new ThriftHandler(context),
          Namenode.Iface.class);
      return new Namenode.Processor(impl);
    }
  }
}
