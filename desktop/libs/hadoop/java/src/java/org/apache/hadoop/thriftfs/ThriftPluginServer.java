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

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.util.concurrent.TimeUnit;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configurable;
import org.apache.hadoop.conf.Configuration;
import org.apache.thrift.TProcessorFactory;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.transport.TServerSocket;
import org.apache.thrift.transport.TServerTransport;
import org.apache.thrift.transport.TTransportFactory;

/**
 * Thrift HDFS plug-in base class.
 */
public class ThriftPluginServer implements Configurable, Runnable {

  protected Configuration conf;
  private SanerThreadPoolServer server;

  protected int port;

  private InetSocketAddress address;

  private TProcessorFactory processorFactory;

  static final Log LOG = LogFactory.getLog(ThriftPluginServer.class);

  static final int SOCKET_READ_TIMEOUT = 2000; // 2sec

  static {
    Configuration.addDefaultResource("thriftfs-default.xml");
    Configuration.addDefaultResource("thriftfs-site.xml");
  }

  public ThriftPluginServer(InetSocketAddress address,
                            TProcessorFactory processorFactory) {
    //options = new TThreadPoolServer.Options();
    port = address.getPort();
    this.address = address;
    this.processorFactory = processorFactory;
  }

  /**
   * Start processing requests.
   * 
   * @throws IllegalStateException if the server has already been started.
   * @throws IOException on network errors.
   */
  public void start() throws IOException {
    String hostname = address.getAddress().getHostAddress();

    synchronized (this) {
      if (server != null) {
        throw new IllegalStateException("Thrift server already started");
      }
      LOG.info("Starting Thrift server");
      ServerSocket sock = new ServerSocket();
      sock.setReuseAddress(true);
      if (port == 0) {
        sock.bind(null);
        address = new InetSocketAddress(hostname, sock.getLocalPort());
        port = address.getPort();
      } else {
        sock.bind(address);
      }
      TServerTransport transport = new TServerSocket(sock, SOCKET_READ_TIMEOUT);
      SanerThreadPoolServer.Options options = new SanerThreadPoolServer.Options();
      options.minWorkerThreads = conf.getInt("dfs.thrift.threads.min", 5);
      options.maxWorkerThreads = conf.getInt("dfs.thrift.threads.max", 20);
      options.stopTimeoutVal = conf.getInt("dfs.thrift.timeout", 60);
      options.stopTimeoutUnit = TimeUnit.SECONDS;
      options.queueSize = conf.getInt("dfs.thrift.queue.size", 4*options.maxWorkerThreads);

      server = new SanerThreadPoolServer(
        processorFactory, transport,
        new TTransportFactory(), new TTransportFactory(),
        new TBinaryProtocol.Factory(), new TBinaryProtocol.Factory(), options);
    }

    Thread t = new Thread(this);
    t.start();
    LOG.info("Thrift server listening on " + hostname + ":" + port);
  }

  /** Stop processing requests. */
  public void stop() {
    synchronized (this) {
      if (server != null) {
        LOG.info("Stopping Thrift server");
        server.stop();
        LOG.info("Thrift stopped");
        server = null;
        port = -1;
      }
    }
  }

  public void close() {
    stop();
  }

  public void run() {
    server.serve();
  }

  public Configuration getConf() {
    return conf;
  }

  public void setConf(Configuration conf) {
    this.conf = conf;
  }

  public int getPort() {
    return port;
  }
}
