package com.cloudera.hue.dbproxy;

import py4j.GatewayServer;

public class DBProxy {
  public static void main(String[] args) {
    DBProxy proxy = new DBProxy();
    GatewayServer server = new GatewayServer(proxy);
    System.out.println("port: " + server.getPort());
    server.start();
  }
}
