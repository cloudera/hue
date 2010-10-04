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
import java.net.InetSocketAddress;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configurable;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.hdfs.protocol.DatanodeID;
import org.apache.hadoop.hdfs.protocol.FSConstants;
import org.apache.hadoop.hdfs.protocol.LocatedBlock;
import org.apache.hadoop.hdfs.protocol.LocatedBlocks;
import org.apache.hadoop.hdfs.protocol.FSConstants.SafeModeAction;
import org.apache.hadoop.hdfs.server.namenode.DatanodeDescriptor;
import org.apache.hadoop.hdfs.server.namenode.FSNamesystem;
import org.apache.hadoop.hdfs.server.namenode.NameNode;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.thriftfs.api.Block;
import org.apache.hadoop.thriftfs.api.Constants;
import org.apache.hadoop.thriftfs.api.ContentSummary;
import org.apache.hadoop.thriftfs.api.DatanodeInfo;
import org.apache.hadoop.thriftfs.api.DFSHealthReport;
import org.apache.hadoop.thriftfs.api.IOException;
import org.apache.hadoop.thriftfs.api.Namenode;
import org.apache.hadoop.thriftfs.api.RequestContext;
import org.apache.hadoop.thriftfs.api.Stat;
import org.apache.hadoop.thriftfs.api.UpgradeStatusReport;
import org.apache.hadoop.util.ServicePlugin;
import org.apache.thrift.TException;
import org.apache.thrift.TProcessor;
import org.apache.thrift.TProcessorFactory;
import org.apache.thrift.transport.TTransport;

public class NamenodePlugin
  extends org.apache.hadoop.hdfs.server.namenode.NamenodePlugin
  implements Configurable {

  /** Name of the configuration property of the Thrift server address */
  public static final String THRIFT_ADDRESS_PROPERTY = "dfs.thrift.address";

  /**
   * Default address and port this server will bind to, in case nothing is found
   * in the configuration object.
   */
  public static final String DEFAULT_THRIFT_ADDRESS = "0.0.0.0:10090";

  private NameNode namenode;

  private static Map<DatanodeID, Integer> thriftPorts =
      new HashMap<DatanodeID, Integer>();

  static final Log LOG = LogFactory.getLog(NamenodePlugin.class);

  private Configuration conf;
  private ThriftPluginServer thriftServer;


  /** Java server-side implementation of the 'Namenode' Thrift interface. */
  class ThriftHandler extends ThriftHandlerBase implements Namenode.Iface {

    public ThriftHandler(ThriftServerContext context) {
      super(context);
    }

    public void chmod(RequestContext ctx, String path, short mode) throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("chmod(" + path + ", " + mode + "): Entering");
      try {
        namenode.setPermission(path, new FsPermission(mode));
      } catch (Throwable t) {
        LOG.info("chmod(" + path + ", " + mode + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public void chown(RequestContext ctx, String path, String owner, String group)
        throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("chown(" + path + "," + owner + "," + group + "): Entering");
      try {
        // XXX Looks like namenode.setOwner() does not complain about this...
        if (owner == null && group == null) {
          throw new IllegalArgumentException(
              "Both 'owner' and 'group' are null");
        }
        namenode.setOwner(path, owner, group);
      } catch (Throwable t) {
        LOG.info("chown(" + path + "," + owner + "," + group + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public List<Long> df(RequestContext ctx) throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("Entering df()");
      try {
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
      } catch (Throwable t) {
        LOG.info("df(): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public void enterSafeMode(RequestContext ctx) throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("enterSafeMode(): Entering");
      try {
        namenode.setSafeMode(SafeModeAction.SAFEMODE_ENTER);
      } catch (Throwable t) {
        LOG.info("enterSafeMode(): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public List<Block> getBlocks(RequestContext ctx, String path, long offset, long length)
        throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("getBlocks(" + path + "," + offset + "," + length
          + "): Entering");
      List<Block> ret = new ArrayList<Block>();
      try {
        LocatedBlocks blocks = namenode.getBlockLocations(path, offset, length);
        if (blocks != null) {
          // blocks may be null if offset is past the end of the file
          for (LocatedBlock b : blocks.getLocatedBlocks()) {
            ret.add(ThriftUtils.toThrift(b, path, thriftPorts));
          }
        }
        LOG.debug("getBlocks(" + path + "," + offset + "," + length
            + "): Returning " + ret);
        return ret;
      } catch (Throwable t) {
        LOG.info("getBlocks(" + path + "," + offset + "," + length
            + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public DFSHealthReport getHealthReport(RequestContext ctx) throws IOException {
      // Health report can only be run by the superuser,
      // but is always available.  Therefore, we ignore ctx.
      assumeSuperuserContext();

      DFSHealthReport hr = new DFSHealthReport();
      try {
        long[] fsnStats = namenode.getStats();
        hr.bytesTotal = fsnStats[0];
        hr.bytesRemaining = fsnStats[2];
        hr.bytesUsed = fsnStats[1];
        hr.bytesNonDfs = hr.bytesTotal - hr.bytesRemaining - hr.bytesUsed;

        ArrayList<DatanodeDescriptor> live = new ArrayList<DatanodeDescriptor>();
        ArrayList<DatanodeDescriptor> dead = new ArrayList<DatanodeDescriptor>();

        namenode.getNamesystem().DFSNodesStatus(live, dead);

        hr.numLiveDataNodes = live.size();
        hr.numDeadDataNodes = dead.size();

        org.apache.hadoop.hdfs.server.common.UpgradeStatusReport usr =
          namenode.distributedUpgradeProgress(FSConstants.UpgradeAction.DETAILED_STATUS);
        if (usr != null) {
          hr.upgradeStatus = new UpgradeStatusReport();
          hr.upgradeStatus.version = usr.getVersion();
          hr.upgradeStatus.percentComplete = usr.getUpgradeStatus();
          hr.upgradeStatus.finalized = usr.isFinalized();
          hr.upgradeStatus.statusText = usr.getStatusText(true);
        }

        hr.httpPort = namenode.getHttpAddress().getPort();
      } catch (java.io.IOException ioe) {
        LOG.info("getHealthReport() failed", ioe);
        throw ThriftUtils.toThrift(ioe);
      }
      return hr;
    }

    public List<DatanodeInfo> getDatanodeReport(
      RequestContext ctx, org.apache.hadoop.thriftfs.api.DatanodeReportType type)
        throws IOException, TException
    {
      // Datanode report can only be run by the superuser, therefore, we ignore 
      // ctx.
      assumeSuperuserContext();

      LOG.debug("getDatanodeReport(" + type + "): Entering");
      List<DatanodeInfo> ret = new ArrayList<DatanodeInfo>();
      try {
        FSConstants.DatanodeReportType rt;
        switch (type) {
        case ALL_DATANODES:
          rt = FSConstants.DatanodeReportType.ALL;
          break;
        case DEAD_DATANODES:
          rt = FSConstants.DatanodeReportType.DEAD;
          break;
        case LIVE_DATANODES:
          rt = FSConstants.DatanodeReportType.LIVE;
          break;
        default:
          throw new IllegalArgumentException("Invalid report type " + type);
        }
        for (org.apache.hadoop.hdfs.protocol.DatanodeInfo node : namenode
            .getDatanodeReport(rt)) {
          ret.add(ThriftUtils.toThrift(node, thriftPorts));
        }
        LOG.debug("getDatanodeReport(" + type + "): Returning " + ret);
        return ret;
      } catch (Throwable t) {
        LOG.info("getDatanodeReport(" + type + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public long getPreferredBlockSize(RequestContext ctx, String path) throws IOException,
        TException {
      assumeUserContext(ctx);
      LOG.debug("getPreferredBlockSize(" + path + "): Entering");
      try {
        long ret = namenode.getPreferredBlockSize(path);
        LOG.debug("getPreferredBlockSize(" + path + "): Returning " + ret);
        return ret;
      } catch (Throwable t) {
        LOG.info("getPreferredBlockSize(" + path + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public boolean isInSafeMode(RequestContext ctx) throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("isInSafeMode(): Entering");
      try {
        boolean ret = namenode.setSafeMode(SafeModeAction.SAFEMODE_GET);
        LOG.debug("isInSafeMode(): Returning " + ret);
        return ret;
      } catch (Throwable t) {
        LOG.info("isInSafeMode(): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public void leaveSafeMode(RequestContext ctx) throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("leaveSafeMode(): Entering");
      try {
        namenode.setSafeMode(SafeModeAction.SAFEMODE_LEAVE);
      } catch (Throwable t) {
        LOG.info("leaveSafeMode(): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public List<Stat> ls(RequestContext ctx, String path) throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("ls(" + path + "):Entering");
      List<Stat> ret = new ArrayList<Stat>();
      try {
        FileStatus[] listing = namenode.getListing(path);
        if (listing == null) {
          throw new FileNotFoundException("Not found: " + path);
        }
        for (FileStatus f : listing) {
          ret.add(fileStatusToStat(f));
        }
        LOG.debug("ls(" + path + "): Returning " + ret);
        return ret;
      } catch (Throwable t) {
        LOG.info("ls(" + path + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public boolean mkdirhier(RequestContext ctx, String path, short perms) throws IOException,
        TException {
      assumeUserContext(ctx);
      LOG.debug("mkdirhier(" + path + ", " + perms + "): Entering");
      try {
        boolean ret = namenode.mkdirs(path, new FsPermission(perms));
        LOG.debug("mkdirhier(" + path + ", " + perms + "): Returning " + ret);
        return ret;
      } catch (Throwable t) {
        LOG.info("mkdirhier(" + path + ", " + perms + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public void refreshNodes(RequestContext ctx) throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("refreshNodes(): Entering");
      try {
        namenode.refreshNodes();
      } catch (Throwable t) {
        LOG.info("refreshNodes(): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public boolean rename(RequestContext ctx, String path, String newPath) throws IOException,
        TException {
      assumeUserContext(ctx);
      LOG.debug("rename(" + path + ", " + newPath + "): Entering");
      try {
        boolean ret = namenode.rename(path, newPath);
        LOG.debug("rename(" + path + ", " + newPath + "): Returning " + ret);
        return ret;
      } catch (Throwable t) {
        LOG.info("rename(" + path + ", " + newPath + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public void reportBadBlocks(RequestContext ctx, List<Block> blocks) throws IOException,
        TException {
      assumeUserContext(ctx);
      LOG.debug("reportBadBlocks(" + blocks + "): Entering");
      int n = blocks.size();
      LocatedBlock[] lb = new LocatedBlock[n];
      for (int i = 0; i < n; ++i) {
        lb[i] = ThriftUtils.fromThrift(blocks.get(i));
      }
      try {
        namenode.reportBadBlocks(lb);
      } catch (Throwable t) {
        LOG.info("reportBadBlocks(" + blocks + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public void setQuota(RequestContext ctx, String path, long namespaceQuota, long diskspaceQuota)
        throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("setQuota(" + path + "," + namespaceQuota + ","
          + diskspaceQuota + "): Entering");
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
      LOG.debug("setQuota(" + path + "," + namespaceQuota + ","
          + diskspaceQuota + "): Quota values translated");
      try {
        namenode.setQuota(path, namespaceQuota, diskspaceQuota);
      } catch (Throwable t) {
        LOG.info("setQuota(" + path + "," + namespaceQuota + ","
            + diskspaceQuota + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public boolean setReplication(RequestContext ctx, String path, short repl) throws IOException,
        TException {
      assumeUserContext(ctx);
      LOG.debug("setReplication(" + path + "," + repl + "): Entering");
      try {
        return namenode.setReplication(path, repl);
      } catch (Throwable t) {
        LOG.info("setReplication(" + path + "," + repl + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public Stat stat(RequestContext ctx, String path) throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("stat(" + path + "): Entering");
      try {
        Stat ret = fileStatusToStat(namenode.getFileInfo(path));
        LOG.debug("stat(" + path + "): Returning " + ret);
        return ret;
      } catch (Throwable t) {
        LOG.info("stat(" + path + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public ContentSummary getContentSummary(RequestContext ctx, String path)
      throws IOException, TException {
      assumeUserContext(ctx);
      LOG.debug("getContentSummary(" + path + "): Entering");
      try {
        ContentSummary cs = getContentSummary(path);
        LOG.debug("getContentSummary(" + path + "): Returning " + cs);
        return cs;
      } catch (Throwable t) {
        LOG.info("getContentSummary(" + path + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public List<ContentSummary> multiGetContentSummary(RequestContext ctx, List<String> paths)
        throws IOException, TException {
        assumeUserContext(ctx);
        LOG.debug("multiGetContentSummary(" + paths + "): Entering");
        List<ContentSummary> ret = new ArrayList<ContentSummary>();
        try {
            for (String path : paths) {
                ret.add(getContentSummary(path));
            }
        } catch (Throwable t) {
            LOG.info("multiGetContentSummary(" + paths + "): Failed", t);
            throw ThriftUtils.toThrift(t);
        }
        LOG.debug("multiGetContentSummary(" + paths + "): Returning " + ret);
        return ret;
    }

    private ContentSummary getContentSummary(String path) throws java.io.IOException {
        try {
            return ThriftUtils.toThrift(namenode.getContentSummary(path), path);
        } catch (java.io.IOException e) {
            LOG.error(e);
            throw e;
        }
    }

    public boolean unlink(RequestContext ctx, String path, boolean recursive) throws IOException,
        TException {
      assumeUserContext(ctx);
      LOG.debug("unlink(" + path + "," + recursive + "): Entering");
      try {
        boolean ret = namenode.delete(path, recursive);
        LOG.debug("unlink(" + path + "," + recursive + "): Returning " + ret);
        return ret;
      } catch (Throwable t) {
        LOG.info("unlink(" + path + "," + recursive + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    public void utime(RequestContext ctx, String path, long atime, long mtime) throws IOException,
        TException {
      assumeUserContext(ctx);
      LOG.debug("utime(" + path + "," + atime + "," + mtime + "): Entering");
      if (mtime == -1 && atime == -1) {
        LOG.debug("utime(" + path + "," + atime + "," + mtime
            + "): Setting mtime and atime to now");
        mtime = atime = System.currentTimeMillis();
      }
      try {
        namenode.setTimes(path, mtime, atime);
      } catch (Throwable t) {
        LOG.info("utime(" + path + "," + atime + "," + mtime + "): Failed", t);
        throw ThriftUtils.toThrift(t);
      }
    }

    private Stat fileStatusToStat(FileStatus f) throws java.io.IOException {
      if (f == null) {
        throw new FileNotFoundException();
      }

      Stat st = new Stat();
      st.path = f.getPath().toString();
      st.isDir = f.isDir();
      st.atime = f.getAccessTime();
      st.mtime = f.getModificationTime();
      st.perms = f.getPermission().toShort();
      st.owner = f.getOwner();
      st.group = f.getGroup();
      if (! st.isDir) {
        st.length = f.getLen();
        st.blockSize = f.getBlockSize();
        st.replication = f.getReplication();
      }
      return st;
    }
    public void datanodeDown(String name, String storage, int thriftPort) throws TException {
      DatanodeID dnId = new DatanodeID(name, storage, -1, -1);
      LOG.info("Datanode " + dnId + ": Thrift port "
               + thriftPort + " closed");
      thriftPorts.remove(dnId);
    }

    public void datanodeUp(String name, String storage, int thriftPort) throws TException {
      DatanodeID dnId = new DatanodeID(name, storage, -1, -1);
      LOG.info("Datanode " + dnId + ": " +
               "Thrift port " + thriftPort + " open");
      thriftPorts.put(dnId, thriftPort);
    }
  }

  public NamenodePlugin() {
  }

  @Override
  public void start(Object service) {
    this.namenode = (NameNode)service;
    try {
      InetSocketAddress address = NetUtils.createSocketAddr(
        conf.get(THRIFT_ADDRESS_PROPERTY, DEFAULT_THRIFT_ADDRESS));

      this.thriftServer = new ThriftPluginServer(address, new ProcessorFactory());
      thriftServer.setConf(conf);
      thriftServer.start();
      // The port may have been 0, so we update it.
      conf.set(THRIFT_ADDRESS_PROPERTY, address.getHostName() + ":" + 
          thriftServer.getPort());
    } catch (java.io.IOException ioe) {
      throw new RuntimeException("Cannot start Thrift namenode plug-in", ioe);
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
      ThriftHandler impl = new ThriftHandler(context);
      return new Namenode.Processor(impl);
    }
  }
}
