// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.util;

import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;

import javax.inject.Inject;

import org.apache.hive.jdbc.HiveConnection;
import org.apache.hive.jdbc.HiveStatement;

import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.config.DasConfiguration.ConfVar;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class HiveExecutor {
  private static final ConfVar<String> HIVE_JDBC_URL =
      new ConfVar<>("hue.query-processor.hive-jdbc-url", "");

  public interface ResultCallback<R> {
    R apply(ResultSet resultSet) throws SQLException;
  }

  private static final String DRIVER_NAME = "org.apache.hive.jdbc.HiveDriver";
  private final DasConfiguration dasConfig;

  @Inject
  public HiveExecutor(DasConfiguration dasConfig) {
    this.dasConfig = dasConfig;
    try {
      Class.forName(DRIVER_NAME);
    } catch (ClassNotFoundException e) {
      throw new RuntimeException("Cannot load driver class: " + DRIVER_NAME);
    }
  }

  public <R> R executeQuery(String sql, String username, ResultCallback<R> fn) throws SQLException {
    String jdbcUrl = dasConfig.getConf(HIVE_JDBC_URL);
    try (HiveConnection connection = (HiveConnection) DriverManager.getConnection(jdbcUrl, username, null);
        HiveStatement statement = (HiveStatement) connection.createStatement(
            ResultSet.TYPE_SCROLL_INSENSITIVE, ResultSet.CONCUR_READ_ONLY)) {
      log.info("Executing sql: " + sql);
      if (statement.execute(sql)) {
        try (ResultSet rs = statement.getResultSet()) {
          return fn.apply(rs);
        }
      } else {
        return null;
      }
    }
  }
}
