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

import java.net.InetSocketAddress;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hdfs.protocol.DatanodeID;
import org.apache.hadoop.hdfs.protocol.LocatedBlock;
import org.apache.hadoop.hdfs.server.namenode.NameNode;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.thriftfs.api.Block;
import org.apache.hadoop.thriftfs.api.Constants;
import org.apache.hadoop.thriftfs.api.ContentSummary;
import org.apache.hadoop.thriftfs.api.DatanodeInfo;
import org.apache.hadoop.thriftfs.api.DatanodeState;
import org.apache.hadoop.thriftfs.api.IOException;
import org.apache.hadoop.thriftfs.api.Namenode;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;
public class ThriftUtils {
  
  static final Log LOG = LogFactory.getLog(ThriftUtils.class);

  public static LocatedBlock fromThrift(Block block) {
    if (block == null) {
      return null;
    }

    org.apache.hadoop.hdfs.protocol.Block b = new org.apache.hadoop.hdfs.protocol.Block(
        block.blockId, block.numBytes, block.genStamp);

    int n = block.nodes.size();
    org.apache.hadoop.hdfs.protocol.DatanodeInfo[] nodes =
        new org.apache.hadoop.hdfs.protocol.DatanodeInfo[n];
    for (int i = 0; i < n; ++i) {
      nodes[i] = fromThrift(block.nodes.get(0));
    }

    LocatedBlock lb = new LocatedBlock(b, nodes, block.startOffset);
    return lb;
  }

  public static Block toThrift(LocatedBlock block, String path,
      Map<DatanodeID, Integer> thriftPorts) {
    if (block == null) {
      return new Block();
    }

    List<DatanodeInfo> nodes = new ArrayList<DatanodeInfo>();
    for (org.apache.hadoop.hdfs.protocol.DatanodeInfo n: block.getLocations()) {
      DatanodeInfo node = toThrift(n, thriftPorts); 
      if (node.getThriftPort() != Constants.UNKNOWN_THRIFT_PORT) {
        nodes.add(node);
      }
    }

    org.apache.hadoop.hdfs.protocol.Block b = block.getBlock();
    return new Block(b.getBlockId(), path, b.getNumBytes(),
                     b.getGenerationStamp(), block.getStartOffset(), nodes);
  }

  public static ContentSummary toThrift(org.apache.hadoop.fs.ContentSummary cs, String path) {
    ContentSummary tcs = new ContentSummary();
    tcs.fileCount = cs.getFileCount();
    tcs.directoryCount = cs.getDirectoryCount();
    tcs.quota = cs.getQuota();
    tcs.spaceConsumed = cs.getSpaceConsumed();
    tcs.spaceQuota = cs.getSpaceQuota();
    tcs.path = path;
    return tcs;
  }

  public static org.apache.hadoop.hdfs.protocol.DatanodeInfo fromThrift(
      DatanodeInfo node) {
    if (node == null) {
      return null;
    }

    org.apache.hadoop.hdfs.protocol.DatanodeInfo ret =
        new org.apache.hadoop.hdfs.protocol.DatanodeInfo();
    ret.name = node.name;
    ret.storageID = node.storageID;
    ret.setCapacity(node.capacity);
    ret.setHostName(node.host);
    ret.setXceiverCount(node.xceiverCount);
    ret.setRemaining(node.remaining);
    if (node.state == DatanodeState.DECOMMISSIONED) {
      ret.setDecommissioned();
    }
    return ret;
  }

  public static DatanodeInfo toThrift(
      org.apache.hadoop.hdfs.protocol.DatanodeInfo node,
      Map<DatanodeID, Integer> thriftPorts) {
    if (node == null) {
      return new DatanodeInfo();
    }

    DatanodeInfo ret = new DatanodeInfo();
    ret.name = node.getName();
    ret.storageID = node.storageID;
    ret.host = node.getHost();
    Integer p = thriftPorts.get(node);
    if (p == null) {
      LOG.warn("Unknown Thrift port for datanode " + node.name);
      ret.thriftPort = Constants.UNKNOWN_THRIFT_PORT;
    } else {
      ret.thriftPort = p.intValue();
    }

    ret.capacity = node.getCapacity();
    ret.dfsUsed = node.getDfsUsed();
    ret.remaining = node.getRemaining();
    ret.xceiverCount = node.getXceiverCount();
    ret.state = node.isDecommissioned() ? DatanodeState.DECOMMISSIONED :
        node.isDecommissionInProgress() ? DatanodeState.DECOMMISSION_INPROGRESS :
        DatanodeState.NORMAL_STATE;
    ret.httpPort = node.getInfoPort();

    long timestamp = node.getLastUpdate();
    long currentTime = System.currentTimeMillis();
    ret.millisSinceUpdate = currentTime - timestamp;

    return ret;
  }

  public static IOException toThrift(Throwable t) {
    if (t == null) {
      return new IOException();
    }

    IOException ret = new IOException();
    ret.clazz = t.getClass().getName();
    ret.msg = t.getMessage();
    ret.stack = "";
    for (StackTraceElement frame : t.getStackTrace()) {
      ret.stack += frame.toString() + "\n";
    }
    return ret;
  }

  /**
   * Creates a Thrift name node client.
   * 
   * @param conf the HDFS instance
   * @return a Thrift name node client.
   */
  public static Namenode.Client createNamenodeClient(Configuration conf)
      throws Exception {
    String s = conf.get(NamenodePlugin.THRIFT_ADDRESS_PROPERTY, NamenodePlugin.DEFAULT_THRIFT_ADDRESS);
    // TODO(todd) use fs.default.name here if set to 0.0.0.0 - but share this with the code in
    // SecondaryNameNode that does the same
    InetSocketAddress addr = NetUtils.createSocketAddr(s);

    // If the NN thrift server is listening on the wildcard address (0.0.0.0),
    // use the external IP from the NN configuration, but with the port listed
    // in the thrift config.
    if (addr.getAddress().isAnyLocalAddress()) {
      InetSocketAddress nnAddr = NameNode.getAddress(conf);
      addr = new InetSocketAddress(nnAddr.getAddress(), addr.getPort());
    }

    TTransport t = new TSocket(addr.getHostName(), addr.getPort());
    t.open();
    TProtocol p = new TBinaryProtocol(t);
    return new Namenode.Client(p);
  }
}
