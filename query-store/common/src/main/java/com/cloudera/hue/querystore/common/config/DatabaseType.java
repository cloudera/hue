package com.cloudera.hue.querystore.common.config;

public enum DatabaseType {
  POSTGRES,
  MYSQL,
  ORACLE;

  private static DatabaseType getDatabaseType(String driverClass) {
    if ("com.mysql.cj.jdbc.Driver".equals(driverClass)) {
      return DatabaseType.MYSQL;
    } else if ("oracle.jdbc.OracleDriver".equals(driverClass)) {
      return DatabaseType.ORACLE;
    }

    return DatabaseType.POSTGRES;
  }

  public static boolean isOracle(String driverClass) {
	  return (getDatabaseType(driverClass) == DatabaseType.ORACLE);
  }
}
