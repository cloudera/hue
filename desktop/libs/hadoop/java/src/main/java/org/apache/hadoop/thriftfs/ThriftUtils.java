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

import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hdfs.DFSConfigKeys;
import org.apache.hadoop.hdfs.protocol.DatanodeID;
import org.apache.hadoop.hdfs.protocol.LocatedBlock;
import org.apache.hadoop.hdfs.security.token.delegation.DelegationTokenIdentifier;
import org.apache.hadoop.hdfs.server.namenode.NameNode;
import org.apache.hadoop.io.DataOutputBuffer;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.security.Credentials;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.security.token.Token;
import org.apache.hadoop.security.token.delegation.AbstractDelegationTokenIdentifier;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.thriftfs.api.Block;
import org.apache.hadoop.thriftfs.api.Constants;
import org.apache.hadoop.thriftfs.api.ContentSummary;
import org.apache.hadoop.thriftfs.api.DatanodeInfo;
import org.apache.hadoop.thriftfs.api.DatanodeState;
import org.apache.hadoop.thriftfs.api.IOException;
import org.apache.hadoop.thriftfs.api.Namenode;
import org.apache.hadoop.thriftfs.api.ThriftDelegationToken;
import org.apache.hadoop.util.StringUtils;
import org.apache.thrift.TException;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.protocol.TProtocol;
import org.apache.thrift.transport.TSocket;
import org.apache.thrift.transport.TTransport;


public class ThriftUtils {

  static final Log LOG = LogFactory.getLog(ThriftUtils.class);

  public static final String HUE_USER_NAME_KEY = "hue.kerberos.principal.shortname";
  public static final String HUE_USER_NAME_DEFAULT = "hue";

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
      Map<DatanodeID, Integer> thriftPorts) throws java.io.IOException {
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
                     b.getGenerationStamp(), nodes, block.getStartOffset(), block.getBlockToken().encodeToUrlString());
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
   * An invocation proxy that authorizes all calls into the Thrift interface.
   * This proxy intercepts all method calls on the handler interface, and verifies
   * that the remote UGI is either (a) the hue user, or (b) another HDFS daemon.
   */
  public static class SecurityCheckingProxy<T> implements InvocationHandler {
    private final T wrapped;
    private final Configuration conf;

    @SuppressWarnings("unchecked")
    public static <T> T create(Configuration conf, T wrapped, Class<T> iface) {
      return (T)java.lang.reflect.Proxy.newProxyInstance(
        iface.getClassLoader(),
        new Class[] { iface },
        new SecurityCheckingProxy<T>(wrapped, conf));
    }

    private SecurityCheckingProxy(T wrapped, Configuration conf) {
      this.wrapped = wrapped;
      this.conf = conf;
    }

    public Object invoke(Object proxy, Method m, Object[] args)
      throws Throwable
    {
      Object result;
      try {
        if (LOG.isDebugEnabled()) {
          LOG.debug("Call " + wrapped.getClass() + "." + m.getName()
                    + "(" + StringUtils.joinObjects(", ", Arrays.asList(args)) + ")");
        }
        authorizeCall(m);

	    return m.invoke(wrapped, args);
      } catch (InvocationTargetException e) {
	    throw e.getTargetException();
      }
    }

    private void authorizeCall(Method m) throws IOException, TException {
      // TODO: this should use the AccessControlList functionality,
      // ideally.
      try {
        UserGroupInformation caller = UserGroupInformation.getCurrentUser();

        if (!conf.get(HUE_USER_NAME_KEY, HUE_USER_NAME_DEFAULT).equals(
              caller.getShortUserName()) &&
            !UserGroupInformation.getLoginUser().getShortUserName().equals(
              caller.getShortUserName())) {

          String errMsg = "Unauthorized access for user " + caller.getUserName();
          // If we can throw our thrift IOException type, do so, so it goes back
          // to the client correctly.
          if (Arrays.asList(m.getExceptionTypes()).contains(IOException.class)) {
            throw ThriftUtils.toThrift(new Exception(errMsg));
          } else {
            // Otherwise we have to just throw the more generic exception, which
            // won't make it back to the client
            throw new TException(errMsg);
          }
        }
      } catch (java.io.IOException ioe) {
        throw new TException(ioe);
      }
    }
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
    if (UserGroupInformation.isSecurityEnabled()) {
      t = new HadoopThriftAuthBridge.Client()
        .createClientTransport(
          conf.get(DFSConfigKeys.DFS_NAMENODE_USER_NAME_KEY),
          addr.getHostName(),
          "KERBEROS", t);
    }

    t.open();
    TProtocol p = new TBinaryProtocol(t);
    return new Namenode.Client(p);
  }

  public static ThriftDelegationToken toThrift(Token<? extends AbstractDelegationTokenIdentifier> delegationToken,
      InetSocketAddress address) throws java.io.IOException {
    String serviceAddress = InetAddress.getByName(address.getHostName()).getHostAddress() + ":"
        + address.getPort();
    delegationToken.setService(new Text(serviceAddress));

    DataOutputBuffer out = new DataOutputBuffer();
    Credentials ts = new Credentials();
    ts.addToken(new Text(serviceAddress), delegationToken);
    ts.writeTokenStorageToStream(out);

    byte[] tokenData = new byte[out.getLength()];
    System.arraycopy(out.getData(), 0, tokenData, 0, tokenData.length);
    return new ThriftDelegationToken(ByteBuffer.wrap(tokenData));
  }
}
