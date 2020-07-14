// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.exception;

/**
 * Thrown when user tries to access some resource of which he/she doesn't have the permission to.
 */
public class NotPermissibleException extends Exception {
  private static final long serialVersionUID = -978492319187996609L;

  public NotPermissibleException() {
  }

  public NotPermissibleException(String message) {
    super(message);
  }

  public NotPermissibleException(String message, Throwable cause) {
    super(message, cause);
  }

  public NotPermissibleException(Throwable cause) {
    super(cause);
  }

  public NotPermissibleException(String message, Throwable cause, boolean enableSuppression, boolean writableStackTrace) {
    super(message, cause, enableSuppression, writableStackTrace);
  }
}
