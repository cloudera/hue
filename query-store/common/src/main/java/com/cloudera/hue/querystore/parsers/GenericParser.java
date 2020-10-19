// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.parsers;

public interface GenericParser<T, S> {
  T parse(S parseInput);
}
