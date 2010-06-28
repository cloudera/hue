// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
package com.cloudera.beeswax;

import java.io.CharArrayWriter;
import java.io.IOException;
import java.io.OutputStream;
import java.io.Writer;

import java.util.Enumeration;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.apache.log4j.Appender;
import org.apache.log4j.ConsoleAppender;
import org.apache.log4j.Layout;
import org.apache.log4j.Logger;
import org.apache.log4j.PatternLayout;


/**
 * A LogContext keeps the log for a "context", which is a logical unit of work.
 * Multiple threads may belong to the same context (but one thread may only belong
 * to one context at any time). And their logs are all kept here.
 */
public class LogContext {
  /** This Logger's name is added to an exclusion list in LogDivertAppender */
  private static Logger LOG = Logger.getLogger(LogContext.class.getName());

  /** The default layout of the logs we keep */
  private static final String DEFAULT_LAYOUT_PATTERN = "%d{yy/MM/dd HH:mm:ss} %p %c{2}: %m%n";

  /** A static map to lookup context by context name */
  private static ConcurrentHashMap<String, LogContext> lcByName;

  /** A static map to lookup context by thread name */
  private static ConcurrentHashMap<String, LogContext> lcByThread;

  private static boolean lcIsInitialized = false;

  /** Where we keep the log */
  private CharArrayWriter logStore;

  /** Name of the context */
  private String name;

  /** Creation time */
  private long createTime;

  /**
   * The LogContextOutputStream helps translate a LogContext to an OutputStream.
   */
  private static class LogContextOutputStream extends OutputStream {
    private Writer logStore;

    /**
     * Create a LogContextOutputStream backed by the given Writer.
     */
    public LogContextOutputStream(Writer logStore) {
      super();
      this.logStore = logStore;
    }

    @Override
    public void write(byte[] b) throws IOException {
      synchronized (this.logStore) {
        this.logStore.write(new String(b));
      }
    }

    @Override
    public void write(byte[] b, int off, int len) throws IOException {
      synchronized (this.logStore) {
        this.logStore.write(new String(b, off, len));
      }
    }

    @Override
    public void write(int b) throws IOException {
      byte[] buf = { (byte) b };
      this.write(buf);
    }
  }


  /**
   * Initialize the capturing of log messages
   */
  public static void initLogCapture() {
    if (lcIsInitialized)
      return;

    // Init static members here
    lcByName = new ConcurrentHashMap<String, LogContext>();
    lcByThread = new ConcurrentHashMap<String, LogContext>();

    // There should be a ConsoleAppender. Copy its Layout.
    Logger root = Logger.getRootLogger();
    Layout layout = null;

    Enumeration<?> appenders = root.getAllAppenders();
    while (appenders.hasMoreElements()) {
      Appender ap = (Appender) appenders.nextElement();
      if (ap.getClass().equals(ConsoleAppender.class)) {
        layout = ap.getLayout();
        break;
      }
    }

    if (layout == null) {
      layout = new PatternLayout(DEFAULT_LAYOUT_PATTERN);
      LOG.info("Cannot find a Layout from a ConsoleAppender. Using default Layout pattern.");
    }

    // Register another Appender (with the same layout) that talks to us.
    Appender ap = new LogDivertAppender(layout);
    root.addAppender(ap);
    lcIsInitialized = true;
  }


  /**
   * Create a LogContext with the given name.
   */
  private LogContext(String name) {
    this.name = name;
    this.logStore = new CharArrayWriter();
    this.createTime = System.currentTimeMillis();
  }

  /**
   * Associate the current thread with this LogContext
   */
  public void registerCurrentThread() {
    String tname = Thread.currentThread().getName();

    // The thread didn't unregister with a previous LogContext. Not a big deal since
    // we automatically unregister for the thread.
    LogContext currLc = lcByThread.get(tname);
    if (currLc != null) {
      LOG.debug("Thread " + tname + " neglected to unregister with a previous LogContext.");
      LogContext.unregisterCurrentThread();
    }

    lcByThread.put(tname, this);
  }

  /**
   * Associate the current thread with the named LogContext, creating one if necessary.
   * @param context  The name of the context
   * @return  The associated LogContext
   */
  public static LogContext registerCurrentThread(String context) {
    final boolean NEW_IF_ABSENT = true;
    LogContext lc = LogContext.getByName(context, NEW_IF_ABSENT);
    lc.registerCurrentThread();
    return lc;
  }

  /**
   * Unregister the current thread with whatever LogContext it has.
   */
  public static boolean unregisterCurrentThread() {
    String tname = Thread.currentThread().getName();
    LogContext lc = lcByThread.remove(tname);
    if (lc == null) {
      LOG.debug("Failed to unregister thread " + tname + ": not currently registered");
      return false;
    }
    return true;
  }

  /**
   * Retrieve a context with the given name.
   * @param newIfAbsent  Create a new one if not found.
   * @return  The named LogContext or null.
   */
  public static LogContext getByName(String name, boolean newIfAbsent) {
    LogContext lc = lcByName.get(name);
    if (lc == null && newIfAbsent) {
      lc = new LogContext(name);
      LogContext curr = lcByName.putIfAbsent(name, lc);
      if (curr != null)
        return curr;
    }
    return lc;
  }

  /**
   * Retrieve a context associated with a thread name
   */
  public static LogContext getByThread(String name) {
    return lcByThread.get(name);
  }

  /**
   * Destroy a context of the given name.
   * This assumes that no other thread are registered with this LogContext.
   * @return  Whether the LogContext is found and destroyed.
   */
  public static boolean destroyContext(String name) {
    LogContext lc = lcByName.remove(name);
    LOG.debug("Removed LogContext '" + name + "'");
    return lc != null;
  }

  /**
   * GC old LogContext.
   */
  public static void garbageCollect(long timeout) {
    long now = System.currentTimeMillis();
    for (Map.Entry<String, LogContext> entry : lcByName.entrySet()) {
      if (entry.getValue().createTime + timeout < now) {
        destroyContext(entry.getKey());
      }
    }
  }

  /**
   * Store the given log message
   */
  public void writeLog(String logMessage) {
    synchronized (this.logStore) {
      this.logStore.write(logMessage, 0, logMessage.length());
    }
  }

  /**
   * Retrieve the log stored
   */
  public String readLog() {
    synchronized (this.logStore) {
      return this.logStore.toString();
    }
  }

  /**
   * Reset the log stored
   */
  public void resetLog() {
    synchronized (this.logStore) {
      this.logStore.reset();
    }
  }

  /**
   * Get an OutputStream that writes to this LogContext.
   */
  public OutputStream getOutputStream() {
    return new LogContextOutputStream(this.logStore);
  }

  public String getName() {
    return name;
  }

  /**
   * Dump all log stored in all contexts into the return string (for debugging).
   */
  public static String dumpAllLogs() {
    StringBuffer buf = new StringBuffer(4096);
    for (Map.Entry<String, LogContext> entry : lcByName.entrySet()) {
      buf.append("--------------------- " + entry.getKey() + " ----------------------");
      buf.append(entry.getValue().readLog());
    }
    return buf.toString();
  }

}
