// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.util;

import lombok.Getter;

/**
 * Holder to store two values;
 */
@Getter
public class Pair<T, S> {
  private final T first;
  private final S second;

  public Pair(T first, S second) {
    this.first = first;
    this.second = second;
  }
}
