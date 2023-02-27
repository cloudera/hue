// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.config;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import javax.validation.constraints.NotNull;

import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;

import lombok.AllArgsConstructor;
import lombok.Getter;

@JsonInclude(JsonInclude.Include.NON_EMPTY)
public class DasConfiguration {
  private final Map<String, Object> properties = new HashMap<>();

  @Getter
  @AllArgsConstructor
  public static class ConfVar<T> {
    @NotNull
    private final String name;

    @NotNull
    private final T defaultValue;
  }

  @JsonAnyGetter
  public Map<String, Object> getProperties() {
    return properties;
  }

  @JsonAnySetter
  public void set(String key, Object value) {
    properties.put(key, value);
  }

  public Optional<Object> get(String key) {
    return Optional.ofNullable(properties.get(key));
  }

  public String getString(String key, String defaultValue) {
    Object value = properties.get(key);
    if (value == null) {
      return defaultValue;
    } else {
      return value.toString();
    }
  }

  public boolean getBool(String key, boolean defaultValue) {
    Object value = properties.get(key);
    if (value == null) {
      return defaultValue;
    } else if (value instanceof Boolean) {
      return ((Boolean) value).booleanValue();
    } else {
      return Boolean.parseBoolean(value.toString());
    }
  }

  public long getLong(String key, long defaultValue) {
    Object value = properties.get(key);
    if (value == null) {
      return defaultValue;
    } else if (value instanceof Number) {
      return ((Number) value).longValue();
    } else {
      return Long.parseLong(value.toString());
    }
  }

  public int getInt(String key, int defaultValue) {
    Object value = properties.get(key);
    if (value == null) {
      return defaultValue;
    } else if (value instanceof Number) {
      return ((Number) value).intValue();
    } else {
      return Integer.parseInt(value.toString());
    }
  }

  @SuppressWarnings("unchecked")
  public <T extends Enum<?>> T getEnum(String key, T def) {
    Object value = properties.get(key);
    if (value == null) {
      return def;
    } else if (value.getClass() == def.getClass()) {
      return (T)value;
    } else {
      return (T)Enum.valueOf(def.getClass(), value.toString());
    }
  }

  public <T> T getConf(ConfVar<T> conf) {
    T def = conf.defaultValue;
    Object value = null;
    if (def instanceof String) {
      value = getString(conf.name, (String)def);
    } else if (def instanceof Boolean) {
      value = getBool(conf.name, (Boolean)def);
    } else if (def instanceof Long) {
      value = getLong(conf.name, (Long)def);
    } else if (def instanceof Integer) {
      value = getInt(conf.name, (Integer)def);
    } else if (def instanceof Enum<?>) {
      value = getEnum(conf.name, (Enum<?>)def);
    } else {
      throw new RuntimeException("Unknown type of ConfVar: " + def.getClass().getName());
    }
    @SuppressWarnings("unchecked")
    T v = (T) value;
    return v;
  }

  public <T> void setConf(ConfVar<T> conf, T value) {
    properties.put(conf.name, value);
  }
}
