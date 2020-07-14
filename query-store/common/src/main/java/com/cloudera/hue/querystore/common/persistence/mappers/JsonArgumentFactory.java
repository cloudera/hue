// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.persistence.mappers;

import java.lang.reflect.Type;
import java.sql.Types;
import java.util.Optional;

import org.jdbi.v3.core.argument.Argument;
import org.jdbi.v3.core.argument.ArgumentFactory;
import org.jdbi.v3.core.argument.NullArgument;
import org.jdbi.v3.core.config.ConfigRegistry;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;

public class JsonArgumentFactory implements ArgumentFactory {
  private final Class<?> clazz;
  private final ObjectWriter objectWriter;

  public JsonArgumentFactory(ObjectMapper mapper, Class<?> clazz) {
    this.clazz = clazz;
    this.objectWriter = mapper.writerFor(clazz);
  }

  @Override
  public Optional<Argument> build(Type type, Object value, ConfigRegistry config) {
    if (type != clazz) {
      return Optional.empty();
    }
    Argument arg = value == null
        ? new NullArgument(Types.VARCHAR)
        : (pos, stat, ctx) -> {
          try {
            stat.setString(pos, objectWriter.writeValueAsString(value));
          } catch (JsonProcessingException e) {
            throw new RuntimeException("Unable to convert to json string", e);
          }
        };
    return Optional.of(arg);
  }
}
