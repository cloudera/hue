// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.Collection;

import lombok.Value;

/**
 * Object to hold the page information returned after quering the backend datastore.
 */
@Value
public class PageData<T> {
  private Collection<T> entities;
  private int offset;
  private int limit;
  private long count;
}
