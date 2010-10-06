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

import java.io.EOFException;
import java.nio.ByteBuffer;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.security.PrivilegedExceptionAction;
import java.util.zip.CRC32;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configurable;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.hdfs.DFSClient;
import org.apache.hadoop.hdfs.security.token.block.BlockTokenIdentifier;
import org.apache.hadoop.hdfs.server.datanode.DataNode;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.security.token.Token;
import org.apache.hadoop.thriftfs.api.Block;
import org.apache.hadoop.thriftfs.api.BlockData;
import org.apache.hadoop.thriftfs.api.Datanode;
import org.apache.hadoop.thriftfs.api.IOException;
import org.apache.hadoop.thriftfs.api.Namenode;
import org.apache.hadoop.thriftfs.api.RequestContext;
import org.apache.thrift.TException;
import org.apache.thrift.TProcessor;
import org.apache.thrift.TProcessorFactory;
import org.apache.thrift.transport.TTransport;

public class DatanodePlugin
  extends org.apache.hadoop.hdfs.server.datanode.DatanodePlugin
  implements Configurable {


  /** Name of the configuration property of the Thrift server address */
  public static final String THRIFT_ADDRESS_PROPERTY =
      "dfs.thrift.datanode.address";
  /**
   * Default address and port this server will bind to, in case nothing is found
   * in the configuration object.
   */
  public static final String DEFAULT_THRIFT_ADDRESS = "0.0.0.0:0";

  private DataNode datanode;
  private Thread registerThread;
  private volatile boolean register;

  static final Log LOG = LogFactory.getLog(DatanodePlugin.class);

  private ThriftPluginServer thriftServer;

  private Configuration conf;

  public DatanodePlugin() {
  }


  class ThriftHandler extends ThriftHandlerBase implements Datanode.Iface {

    private int bufferSize;
    private CRC32 summer;

    public ThriftHandler(ThriftServerContext context) {
      super(context);
      this.bufferSize = conf.getInt("io.file.buffer.size", 4096);
      this.summer = new CRC32();
    }

    public BlockData readBlock(RequestContext ctx, final Block block, final long offset,
        final int length) throws IOException, TException {
      LOG.debug("readBlock(" + block.blockId + "," + offset + "," + length + "): Entering");
      return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<BlockData>() {
        public BlockData run() throws IOException {

          BlockData ret = new BlockData();
          DFSClient.BlockReader reader = null;
          try {
            Token<BlockTokenIdentifier> token = new Token<BlockTokenIdentifier>();
            token.decodeFromUrlString(block.token);
            reader = DFSClient.BlockReader.newBlockReader(getSocket(), block.path, block.blockId,
                token, block.genStamp, offset, length, bufferSize, true, serverContext
                    .getClientName());
            byte[] buf = new byte[length];
            int n = reader.read(buf, 0, length);
            if (n == -1) {
              throw new EOFException("EOF reading " + length + " bytes at offset " + offset
                  + " from " + block);
            }
            LOG.debug("readBlock(" + block.blockId + ", " + offset + ", " + length + "): Read " + n
                + " bytes");

            if (n == length) {
              // If we read exactly the same number of bytes that was asked for,
              // we can simply return the buffer directly
              ret.data = ByteBuffer.wrap(buf);
            } else {
              assert n < length;
              // If we read fewer bytes than they asked for, we need to write
              // back a smaller byte array. With the appropriate thrift hook
              // we could avoid this copy, too.
              byte[] data = new byte[n];
              System.arraycopy(buf, 0, ret.data, 0, n);
              ret.data = ByteBuffer.wrap(data);
            }
            ret.length = n;

            summer.update(ret.data.array());
            ret.crc = (int) summer.getValue();
            summer.reset();
            LOG.debug("readBlock(" + block.blockId + ", " + offset + ", " + length + "): CRC32: "
                + ret.crc);
          } catch (Throwable t) {
            LOG.warn("readBlock(" + block.blockId + ", " + offset + ", " + length + "): Failed", t);
            throw ThriftUtils.toThrift(t);
          } finally {
            if (reader != null) {
              try {
                reader.close();
              } catch (Throwable t) {
                LOG.warn("readBlock(" + block.blockId + ", " + offset + ", " + length
                    + "): Cannot close block reader", t);
              }
            }
          }
          return ret;
        }
      });
    }

    private Socket getSocket() throws java.io.IOException {
      InetSocketAddress addr = datanode.getSelfAddr();
      return new Socket(addr.getAddress(), addr.getPort());
    }
  }

  public void setConf(Configuration conf) {
    this.conf = conf;
  }

  public Configuration getConf() {
    return conf;
  }


  @Override
  public void start(Object service) {
    this.datanode = (DataNode)service;
    try {
      InetSocketAddress address = NetUtils.createSocketAddr(
        conf.get(THRIFT_ADDRESS_PROPERTY, DEFAULT_THRIFT_ADDRESS));

      thriftServer = new ThriftPluginServer(
        address, new ProcessorFactory());
      thriftServer.setConf(conf);
      thriftServer.start();
    } catch (Exception e) {
      throw new RuntimeException("Could not start Thrift Datanode Plugin", e);
    }
  }

  @Override
  public void initialRegistrationComplete() {
    registerWithNameNode();
  }

  @Override
  public void reregistrationComplete() {
    registerWithNameNode();
  }

  private void registerWithNameNode() {
    register = true;
    registerThread = new Thread(new Runnable() {
        public void run() {
          Namenode.Client namenode = null;
          String name = datanode.dnRegistration.getName();
          String storageId = datanode.dnRegistration.getStorageID();

          while (register) {
            try {
              if (namenode == null) {
                namenode = ThriftUtils.createNamenodeClient(conf);
              }
              namenode.datanodeUp(name, storageId, thriftServer.getPort());
              register = false;
              LOG.info("Datanode " + name + " registered Thrift port " +
                       thriftServer.getPort());
            } catch (Throwable t) {
              LOG.info("Datanode registration failed", t);
              try {
                Thread.sleep(1000);
              } catch (InterruptedException e) {}
            }
          }
        }
      });
    registerThread.start();
  }

  @Override
  public void stop() {
    register = false;
    try {
      registerThread.join();
    } catch (Throwable t) {}

    try {
      Namenode.Client namenode = ThriftUtils.createNamenodeClient(conf);
      namenode.datanodeDown(datanode.dnRegistration.getName(),
                            datanode.dnRegistration.getStorageID(),
                            thriftServer.getPort());
    } catch (Throwable t) {}

    thriftServer.stop();
  }

  @Override
  public void close() {
    stop();
  }

  class ProcessorFactory extends TProcessorFactory {

    ProcessorFactory() {
      super(null);
    }

    @Override
    public TProcessor getProcessor(TTransport t) {
      ThriftServerContext context = new ThriftServerContext(t);

      Datanode.Iface impl =
        ThriftUtils.SecurityCheckingProxy.create(
          conf,
          new ThriftHandler(context),
          Datanode.Iface.class);
      return new Datanode.Processor(impl);
    }
  }
}
