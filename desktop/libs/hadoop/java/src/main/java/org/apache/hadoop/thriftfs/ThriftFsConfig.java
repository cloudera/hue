/*
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

/**
 * Thrift FS config constants
 */
public class ThriftFsConfig {
  /** Datanode thrift plugin <host>:<port> */
  public static final String DFS_THRIFT_DATANODE_ADDR_KEY = "dfs.thrift.datanode.address";

  /** Namenode thrift plugin <host>:<port> */
  public static final String DFS_THRIFT_ADDR_KEY = "dfs.thrift.address";

  /** Min number of threads for thrift server */
  public static final String DFS_THRIFT_THREADS_MIN_KEY = "dfs.thrift.threads.min";

  /** Max number of threads for thrift server */
  public static final String DFS_THRIFT_THREADS_MAX_KEY = "dfs.thrift.threads.max";

  /** Timeout (in seconds) for thrift server threads */
  public static final String DFS_THRIFT_TIMEOUT_KEY = "dfs.thrift.timeout";

  /** Read timeout (in milliseconds) for thrift socket */
  public static final String DFS_THRIFT_SOCKET_TIMEOUT_KEY = "dfs.thrift.socket.timeout";

  /** Queue size for thrift server */
  public static final String DFS_THRIFT_QUEUE_SIZE_KEY = "dfs.thrift.queue.size";
}
