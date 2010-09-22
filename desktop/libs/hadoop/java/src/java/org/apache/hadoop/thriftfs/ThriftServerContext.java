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

import java.net.Socket;
import java.util.Random;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TSocket;

/**
 * Represents the context of a Thrift service
 */
public class ThriftServerContext {
  private final TTransport transport;
  private final String clientName;

  static final Log LOG = LogFactory.getLog(ThriftHandlerBase.class);

  private static Random random = new Random();

  public ThriftServerContext(TTransport transport) {
    this.transport = transport;
    this.clientName = assignClientName();
  }

  /**
   * Tries to get the client name for a given Thrift transport.
   * 
   * @param t the Thrift transport
   * @return The client name, if 'transport' was a socket, or
   *         "unknown-client:<random number>" otherwise.
   */
  private String assignClientName() {
    Socket sock = getTransportSocket();
    if (sock != null) {
      return sock.getInetAddress().getHostAddress() + ":" + sock.getPort();
    }
    return "unknown-client:" + random.nextLong();
  }

  public String getClientName() {
    return this.clientName;
  }

  /**
   * Tries to get the Socket out of a Thrift transport.
   *
   * @param t the Thrift transport
   * @return the socket, or null if the transport was non-socket type.
   */
  private Socket getTransportSocket() {
    if (TSocket.class.isAssignableFrom(transport.getClass())) {
      return ((TSocket)transport).getSocket();
    }
    return null;
  }
}
