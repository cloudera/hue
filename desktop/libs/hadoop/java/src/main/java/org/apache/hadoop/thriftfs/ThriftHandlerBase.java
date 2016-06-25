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

import java.security.PrivilegedAction;
import java.security.PrivilegedExceptionAction;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.util.VersionInfo;

import org.apache.hadoop.thriftfs.api.HadoopServiceBase;
import org.apache.hadoop.thriftfs.api.IOException;
import org.apache.hadoop.thriftfs.api.MetricsContext;
import org.apache.hadoop.thriftfs.api.MetricsRecord;
import org.apache.hadoop.thriftfs.api.RequestContext;
import org.apache.hadoop.thriftfs.api.RuntimeInfo;
import org.apache.hadoop.thriftfs.api.StackTraceElement;
import org.apache.hadoop.thriftfs.api.ThreadStackTrace;

/**
 * Base class to provide some utility functions for thrift plugin handlers
 */
public abstract class ThriftHandlerBase implements HadoopServiceBase.Iface {
  protected final ThriftServerContext serverContext;
  static final Log LOG = LogFactory.getLog(ThriftHandlerBase.class);

  public ThriftHandlerBase(ThriftServerContext serverContext) {
    this.serverContext = serverContext;
  }

  /**
   * Return the version info of this server
   */
  public org.apache.hadoop.thriftfs.api.VersionInfo getVersionInfo(
    RequestContext ctx) {
    org.apache.hadoop.thriftfs.api.VersionInfo vi =
      new org.apache.hadoop.thriftfs.api.VersionInfo();
    vi.version = VersionInfo.getVersion();
    vi.revision = VersionInfo.getRevision();
    vi.compileDate = VersionInfo.getDate();
    vi.compilingUser = VersionInfo.getUser();
    vi.url = VersionInfo.getUrl();
    vi.buildVersion = VersionInfo.getBuildVersion();
    return vi;
  }

  /**
   * Return lots of status info about this server
   */
  public RuntimeInfo getRuntimeInfo(RequestContext ctx) {
    RuntimeInfo ri = new RuntimeInfo();
    ri.totalMemory = Runtime.getRuntime().totalMemory();
    ri.freeMemory = Runtime.getRuntime().freeMemory();
    ri.maxMemory = Runtime.getRuntime().maxMemory();

    return ri;
  }

  public List<MetricsContext> getAllMetrics(RequestContext reqCtx) {
    throw new UnsupportedOperationException();
  }

  public MetricsContext getMetricsContext(RequestContext context, String name) {
    throw new UnsupportedOperationException();
  }

  /**
   * Return a list of threads that currently exist with their stack traces
   */
  public List<ThreadStackTrace> getThreadDump(RequestContext ctx) {
    List<ThreadStackTrace> dump = new ArrayList<ThreadStackTrace>();

    Map<Thread, java.lang.StackTraceElement[]> traces = Thread.getAllStackTraces();
    for (Map.Entry<Thread, java.lang.StackTraceElement[]> entry : traces.entrySet()) {
      final Thread t = entry.getKey();
      final java.lang.StackTraceElement[] frames = entry.getValue();

      ThreadStackTrace tst = new ThreadStackTrace();
      tst.threadName = t.getName();
      tst.threadStringRepresentation = String.valueOf(t);
      tst.isDaemon = t.isDaemon();
      tst.stackTrace = new ArrayList<StackTraceElement>();
      for (java.lang.StackTraceElement ste : frames) {
        StackTraceElement tFrame = new StackTraceElement();
        tFrame.className = ste.getClassName();
        tFrame.fileName = ste.getFileName();
        tFrame.lineNumber = ste.getLineNumber();
        tFrame.methodName = ste.getMethodName();
        tFrame.isNativeMethod = ste.isNativeMethod();
        tFrame.stringRepresentation = String.valueOf(ste);
        tst.stackTrace.add(tFrame);
      }
      dump.add(tst);
    }
    return dump;
  }

  /**
   * The methods below should be called by all RPCs with the request context
   * passed in, whenever said RPCs are accessing Hadoop-internal methods. These
   * assume the authentication role of the requester.
   *
   * Most of the time you can just wrap the entire contents of the method with
   * these methods. If, however, your RPC needs to throw an exception not of
   * type IOException, then you may need to wrap only the portions which
   * actually touch Hadoop, and then throw your own exception(s) based on the
   * result of these calls.
   */
  protected <T> T assumeUserContextAndExecute(RequestContext ctx, PrivilegedExceptionAction<T> action) throws IOException {
    try {
      return UserGroupInformation.createProxyUser(
        ctx.confOptions.get("effective_user"),
        UserGroupInformation.getCurrentUser()).doAs(action);
    } catch (Throwable e) {
      throw ThriftUtils.toThrift(e);
    }
  }

  protected <T> T assumeUserContextAndExecute(RequestContext ctx, PrivilegedAction<T> action) {
    try {
      return UserGroupInformation.createProxyUser(ctx.confOptions.get("effective_user"),
          UserGroupInformation.getCurrentUser()).doAs(action);
    } catch (java.io.IOException e) {
      // This should only be thrown in the event getLoginUser() fails.
      throw new Error(e);
    }
  }

}
