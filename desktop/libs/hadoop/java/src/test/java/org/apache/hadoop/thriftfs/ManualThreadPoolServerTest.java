/**
 * Licensed to Cloudera, Inc. under one
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

import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.List;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.thriftfs.api.HadoopServiceBase;
import org.apache.hadoop.thriftfs.api.MetricsContext;
import org.apache.hadoop.thriftfs.api.RequestContext;
import org.apache.hadoop.thriftfs.api.RuntimeInfo;
import org.apache.hadoop.thriftfs.api.ThreadStackTrace;
import org.apache.hadoop.thriftfs.api.VersionInfo;
import org.apache.thrift.TException;
import org.apache.thrift.TProcessor;
import org.apache.thrift.TProcessorFactory;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;

/**
 * Manually test driver for futzing with the SanerThreadPoolServer-based
 * ThriftPluginServer.
 *
 * Test with python "HadoopServiceBase-remote -h localhost:9876 getVersionInfo None"
 */
public class ManualThreadPoolServerTest {

  public static void main(String[] args)
        throws TTransportException, IOException {
    if (args.length != 3) {
      System.err.println("Arguments: minThreads maxThreads, queueSize");
      System.exit(1);
    }
    ThriftPluginServer s = new ThriftPluginServer(new InetSocketAddress(9876), new ProcessorFactory());
    Configuration conf = new Configuration();
    conf.set("dfs.thrift.threads.min", args[0]);
    conf.set("dfs.thrift.threads.max", args[1]);
    conf.set("dfs.thrift.queue.size", args[2]);
    s.setConf(conf);
    s.start();
  }

  static class ThriftHandler implements HadoopServiceBase.Iface {

    public ThriftHandler(ThriftServerContext serverContext) {
    }

    @Override
    public List<MetricsContext> getAllMetrics(RequestContext ctx)
        throws org.apache.hadoop.thriftfs.api.IOException, TException {
      return null;
    }

    @Override
    public MetricsContext getMetricsContext(RequestContext ctx,
        String contextName) throws org.apache.hadoop.thriftfs.api.IOException,
        TException {
      return null;
    }

    @Override
    public RuntimeInfo getRuntimeInfo(RequestContext ctx) throws TException {
      return null;
    }

    @Override
    public List<ThreadStackTrace> getThreadDump(RequestContext ctx)
        throws TException {
      return null;
    }

    @Override
    public VersionInfo getVersionInfo(RequestContext ctx) throws TException {
      try {
        Thread.sleep(10*1000);
      } catch (InterruptedException e) {
        // TODO Auto-generated catch block
        e.printStackTrace();
      }
      VersionInfo v = new VersionInfo();
      v.setBuildVersion("test");
      return v;
    }

  }

  static class ProcessorFactory extends TProcessorFactory {

    ProcessorFactory() {
      super(null);
    }

    @Override
    public TProcessor getProcessor(TTransport t) {
      ThriftServerContext context = new ThriftServerContext(t);
      ThriftHandler impl = new ThriftHandler(context);
      return new HadoopServiceBase.Processor(impl);
    }
  }

}
