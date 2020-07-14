// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.exception;

import com.cloudera.hue.querystore.common.entities.JdbiEntity;

public class DBUpdateFailedException extends IllegalStateException {
  private static final long serialVersionUID = -4594741804486420695L;
  private JdbiEntity entity;

  public DBUpdateFailedException(JdbiEntity entity) {
    this.entity = entity;
  }

  public DBUpdateFailedException(String message, JdbiEntity entity) {
    super(message);
    this.entity = entity;
  }

  public DBUpdateFailedException(String message, Throwable cause, JdbiEntity entity) {
    super(message, cause);
    this.entity = entity;
  }

  public DBUpdateFailedException(Throwable cause, JdbiEntity entity) {
    super(cause);
    this.entity = entity;
  }

  public JdbiEntity getEntity() {
    return entity;
  }
}
