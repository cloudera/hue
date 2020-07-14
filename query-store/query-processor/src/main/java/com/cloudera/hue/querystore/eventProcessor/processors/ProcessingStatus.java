// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors;

import lombok.Getter;

@Getter
public class ProcessingStatus {
  private final Status status;
  private final Throwable error;

  private ProcessingStatus(Status status, Throwable error) {
    this.status = status;
    this.error = error;
  }

  public ProcessingStatus(Throwable error) {
    this(Status.ERROR, error);
  }

  public Status getStatus() {
    return status;
  }

  public Throwable getError() {
    return error;
  }

  public static enum Status {
    SUCCESS, ERROR, SKIP, FINISH
  }

  public static ProcessingStatus SUCCESS = new ProcessingStatus(Status.SUCCESS, null);
  public static ProcessingStatus SKIP = new ProcessingStatus(Status.SKIP, null);
  public static ProcessingStatus FINISH = new ProcessingStatus(Status.FINISH, null);
}
