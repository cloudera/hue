// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.persistence.mappers;

import java.io.IOException;
import java.sql.ResultSet;
import java.sql.SQLException;

import org.jdbi.v3.core.mapper.ColumnMapper;
import org.jdbi.v3.core.statement.StatementContext;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectReader;

public class JsonColumnMapper<T> implements ColumnMapper<T> {
  private final ObjectReader objectReader;

  public JsonColumnMapper(ObjectMapper objectMapper, Class<T> clazz) {
    this.objectReader = objectMapper.readerFor(clazz);
  }

  @Override
  public T map(ResultSet rs, int columnNumber, StatementContext ctx) throws SQLException {
    String data = rs.getString(columnNumber);
    if (data == null) {
      return null;
    }
    try {
      return objectReader.readValue(data);
    } catch (IOException e) {
      throw new SQLException("Error reading json value from database", e);
    }
  }
}
