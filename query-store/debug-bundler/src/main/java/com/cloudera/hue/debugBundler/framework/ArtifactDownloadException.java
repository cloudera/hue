// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

public class ArtifactDownloadException extends Exception {

  private static final long serialVersionUID = -3632196021073193293L;

  public ArtifactDownloadException(String message, Throwable cause) {
    super(message, cause);
  }

  public ArtifactDownloadException(String message) {
    super(message);
  }

  public ArtifactDownloadException(Throwable cause) {
    super(cause);
  }
}
