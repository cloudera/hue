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

import java.io.IOException;
import java.net.Socket;
import java.security.PrivilegedAction;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.MissingOptionException;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionGroup;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.cli.PosixParser;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.hive.conf.HiveConf;
import org.apache.hadoop.hive.metastore.HiveMetaStore.HMSHandler;
import org.apache.hadoop.hive.metastore.api.MetaException;
import org.apache.hadoop.hive.metastore.api.ThriftHiveMetastore;
import org.apache.hadoop.hive.metastore.api.ThriftHiveMetastore.Iface;
import org.apache.hadoop.hive.ql.Driver;
import org.apache.hadoop.security.SaslRpcServer;
import org.apache.hadoop.security.SecurityUtil;
import org.apache.hadoop.security.SaslRpcServer.AuthMethod;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.log4j.Logger;
import org.apache.thrift.TProcessor;
import org.apache.thrift.protocol.TBinaryProtocol;
import org.apache.thrift.server.TServer;
import org.apache.thrift.server.TThreadPoolServer;
import org.apache.thrift.transport.TSaslServerTransport;
import org.apache.thrift.transport.TServerSocket;
import org.apache.thrift.transport.TServerTransport;
import org.apache.thrift.transport.TTransport;
import org.apache.thrift.transport.TTransportException;
import org.apache.thrift.transport.TTransportFactory;

import com.cloudera.beeswax.api.BeeswaxService;
import com.cloudera.beeswax.api.BeeswaxService.Processor;
import com.facebook.fb303.FacebookService;

public class Server {

  private static final Logger LOG = Logger.getLogger(Server.class.getName());
  private static final int USHRT_MAX = 65535;
  // Refresh ticket every 8 hours
  private static final int DEFAULT_KRB_REFRESH_INTERVAL = (8 * 60 * 60 * 1000);

  private static int mport = -1;
  private static int bport = -1;
  /** Host and port that desktop runs on */
  private static String dtHost = "";
  private static int dtPort = -1;
  private static boolean dtHttps = false;
  private static long qlifetime = BeeswaxServiceImpl.RUNNING_QUERY_LIFETIME;
  private static boolean useKerberos = false;
  private static String principalConf;
  private static String keytabFile;
  private static Integer refreshInterval = DEFAULT_KRB_REFRESH_INTERVAL;
  private static String kerberosName;
  private static UserGroupInformation bwUgi;

  public static class KbrSaslTransportFactory extends TTransportFactory {
    UserGroupInformation ugi;
    TSaslServerTransport.Factory saslFactory;

    public KbrSaslTransportFactory(TSaslServerTransport.Factory saslFactory, UserGroupInformation ugi) {
      this.saslFactory = saslFactory;
      this.ugi = ugi;
    }

    @Override
    public TTransport getTransport(final TTransport base) {
      return ugi.doAs(new PrivilegedAction<TTransport>() {
        public TTransport run() {
          return saslFactory.getTransport(base);
        }
      });
    }
  }

  /**
   * Parse command line options.
   *
   * -b <port> specifies the port for beeswax to use.
   * -m <port>, if given, starts the metastore at this port.
   */
  private static void parseArgs(String[] args) throws ParseException {
    Options options = new Options();
    OptionGroup dtOptions = new OptionGroup();
    dtOptions.setRequired(true);

    Option metastoreOpt = new Option("m", "metastore", true, "port to use for metastore");
    metastoreOpt.setRequired(false);
    options.addOption(metastoreOpt);

    Option queryLifetimeOpt = new Option("l", "query-lifetime", true,
        "query lifetime");
    queryLifetimeOpt.setRequired(false);
    options.addOption(queryLifetimeOpt);

    Option beeswaxOpt = new Option("b", "beeswax", true, "port to use for beeswax");
    beeswaxOpt.setRequired(true);
    options.addOption(beeswaxOpt);

    Option dtHostOpt = new Option("h", "desktop-host", true, "host running desktop");
    dtHostOpt.setRequired(false);
    options.addOption(dtHostOpt);

    Option dtHttpsOpt = new Option("s", "desktop-https", true, "desktop is running https");
    options.addOption(dtHttpsOpt);

    Option dtPortOpt = new Option("p", "desktop-port", true, "port used by desktop");
    dtPortOpt.setRequired(false);
    dtOptions.addOption(dtPortOpt);

    Option noDesktopOpt = new Option("n", "no-desktop", false, "no desktop used");
    dtOptions.addOption(noDesktopOpt);

    Option kPrincipalOpt = new Option("c", "principalConf", true, "Principal configuration");
    options.addOption(kPrincipalOpt);

    Option kTabOpt = new Option("k", "keytab", true, "keytab file");
    options.addOption(kTabOpt);

    Option kRefreshOpt = new Option("r", "refresh", true, "kerberos ticket refresh interval in minutes");
    options.addOption(kRefreshOpt);

    options.addOptionGroup(dtOptions); // make "n" and "p" mutually exclusive
    PosixParser parser = new PosixParser();
    CommandLine cmd = parser.parse(options, args);

    if (!cmd.getArgList().isEmpty()) {
      throw new ParseException("Unexpected extra arguments: " + cmd.getArgList());
    }

    for (Option opt : cmd.getOptions()) {
      if (opt.getOpt().equals("m")) {
        mport = parsePort(opt);
      } else if (opt.getOpt().equals("b")) {
        bport = parsePort(opt);
      } else if (opt.getOpt().equals("h")) {
        dtHost = opt.getValue();
      } else if (opt.getOpt().equals("p")) {
        dtPort = parsePort(opt);
      } else if (opt.getOpt().equals("s")) {
        dtHttps = true;
      } else if (opt.getOpt().equals("l")) {
        qlifetime = Long.valueOf(opt.getValue());
      } else if (opt.getOpt().equals("k")) {
        keytabFile = opt.getValue();
        useKerberos = true;
      } else if (opt.getOpt().equals("c")) {
        principalConf = opt.getValue();
      } else if (opt.getOpt().equals("r")) {
        refreshInterval = Integer.valueOf(opt.getValue()) * 1000 * 60; // minutes
      }

    }
  }

  private static int parsePort(Option opt) throws ParseException {
    int port = Integer.valueOf(opt.getValue());
    if (port < 0 || port > USHRT_MAX)
      throw new ParseException("Port number must be a number in [0, " + USHRT_MAX + "]");
    return port;
  }

  public static void main(String[] args)
        throws TTransportException, MetaException, ParseException {
    parseArgs(args);
    if (useKerberos) {
      doKerberosAuth();
    }
    createDirectoriesAsNecessary();

    // Start metastore if specified
    if (mport != -1) {
      LOG.info("Starting metastore at port " + mport);
      Thread t = new Thread(new Runnable() {
        @Override
        public void run() {
          try {
            serveMeta(mport);
          } catch (TTransportException e) {
            e.printStackTrace();
          } catch (MetaException e) {
            e.printStackTrace();
          }
        }
      }, "MetaServerThread");
      t.setDaemon(true);
      t.start();
    }

    // Serve beeswax out of the main thread.
    LOG.info("Starting beeswaxd at port " + bport);
    serveBeeswax(bport);
  }

  /**
   * Hive won't work unless /tmp and /user/hive/warehouse are usable,
   * so we create them for the user.
   */
  private static void createDirectoriesAsNecessary() {
    try {
      LOG.debug("Classpath: " + System.getProperty("java.class.path"));
      HiveConf conf = new HiveConf(Driver.class);
      FileSystem fs = FileSystem.get(conf);
      Path tmpDir = new Path("/tmp");
      Path metaDir = new Path(conf
          .get(HiveConf.ConfVars.METASTOREWAREHOUSE.varname));
      for (Path dir : new Path[] { tmpDir, metaDir }) {
        if (!fs.exists(dir)) {
          if (fs.mkdirs(dir)) {
            fs.setPermission(dir, new FsPermission((short) 0777));
            LOG.info("Created " + dir + " with world-writable permissions.");
          } else {
            LOG.error("Could not create " + dir);
          }
        }
      }
    } catch (IOException e) {
      HiveConf conf = new HiveConf(Driver.class);
      LOG.error("Error while trying to check/create /tmp and warehouse directory " + conf
          .get(HiveConf.ConfVars.METASTOREWAREHOUSE.varname), e);
    }
  }

  /**
   * Start the Beeswax server.
   */
  private static void serveBeeswax(int port) throws TTransportException {
    TServerTransport serverTransport = new TServerSocket(port);
    BeeswaxService.Iface impl = new BeeswaxServiceImpl(dtHost, dtPort, dtHttps,
        qlifetime);
    Processor processor = new BeeswaxService.Processor(impl);
    TTransportFactory transFactory;

    if (useKerberos) {
      final String names[] = SaslRpcServer.splitKerberosName(kerberosName);
      if (names.length < 2) {
        throw new IllegalArgumentException(
            "Kerberos principal should have at least 2 parts: " + kerberosName);
      }

      TSaslServerTransport.Factory saslFactory =
          new TSaslServerTransport.Factory(AuthMethod.KERBEROS.getMechanismName(),
              names[0], names[1] , // two parts of kerberos principal
              SaslRpcServer.SASL_PROPS,
              new SaslRpcServer.SaslGssCallbackHandler());
      transFactory = new KbrSaslTransportFactory(saslFactory, bwUgi);
    } else {
      transFactory = new TTransportFactory();
    }

    TThreadPoolServer.Args args = new TThreadPoolServer.Args(serverTransport)
        .processor(processor)
        .protocolFactory(new TBinaryProtocol.Factory())
        .transportFactory(transFactory);
    TServer server = new TThreadPoolServer(args);

    if (dtPort != -1) {
      LOG.info("Starting beeswax server on port " + port + ", talking back to Desktop at "
                + dtHost + ":" + dtPort);
    } else {
      LOG.info("Starting beeswax server on port " + port);
    }
    server.serve();
  }

  /**
   * Authenticate using kerberos if configured
   */
  private static void doKerberosAuth() throws IllegalArgumentException {
    if (keytabFile == null || keytabFile.isEmpty()) {
      throw new IllegalArgumentException("No keytab specified");
    }
    if (principalConf == null || principalConf.isEmpty()) {
      throw new IllegalArgumentException("No principal specified");
    }

    // Login from the keytab
    try {
      kerberosName = SecurityUtil.getServerPrincipal(principalConf, "0.0.0.0");
      UserGroupInformation.loginUserFromKeytab(kerberosName, keytabFile);
      LOG.info("Logged in using Kerberos ticket for '" + kerberosName +
               "' from " + keytabFile);
      bwUgi = UserGroupInformation.getCurrentUser();
      // Start a thread to periodically refresh kerberos ticket
      Thread t = new Thread(new Runnable() {
        @Override
        public void run() {
          while (true) {
            try {
              Thread.sleep(refreshInterval);
            } catch (InterruptedException e) {
              return;
            }
            try {
              LOG.info("Refreshed Kerberos ticket for '" + kerberosName +
                       "' from " + keytabFile);
              UserGroupInformation.getLoginUser().reloginFromKeytab();
            } catch (IOException eIO) {
              LOG.error("Error refreshing Kerberos ticket", eIO);
            }
          }
        }
      }, "KerberosRefresher");
      t.start();
    } catch (IOException e) {
      throw new IllegalArgumentException(
          "Couldn't setup Kerberos authentication", e);
    }
  }

  /**
   * Start the thrift metastore server.
   *
   * Mostly borrowed from org.apache.hadoop.hive.metastore.HiveMetaStore.
   */
  public static void serveMeta(int port) throws MetaException, TTransportException {
    // Verify that we're supposed to run an internal metastore.
    HiveConf conf = new HiveConf(Driver.class);
    if (!conf.getBoolean("hive.metastore.local", true)) {
      String msg = "hive.metastore.local is set to false. The Beeswax internal metastore " +
                   "is not supposed to run.";
      LOG.fatal(msg);
      System.exit(1);
    }

    TServerTransport serverTransport = new TServerSocket(port);
    Iface handler = new HMSHandler("new db based metaserver");
    FacebookService.Processor processor = new ThriftHiveMetastore.Processor(handler);

    TThreadPoolServer.Args args = new TThreadPoolServer.Args(serverTransport)
        .processor(processor)
        .protocolFactory(new TBinaryProtocol.Factory())
        .transportFactory(new TTransportFactory());
    TServer server = new TThreadPoolServer(args);

    HMSHandler.LOG.info("Started the new metaserver on port [" + port + "]...");
    HMSHandler.LOG.info("minWorkerThreads = " + args.minWorkerThreads);
    HMSHandler.LOG.info("maxWorkerThreads = " + args.maxWorkerThreads);
    server.serve();
  }
}
