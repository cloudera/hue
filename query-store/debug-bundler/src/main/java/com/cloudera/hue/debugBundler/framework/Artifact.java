// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

/**
 * Interface representing an Artifact which should be downloaded.
 */
public interface Artifact {
  /**
   * Name used by ArtifactStreamer as the path of the file in the archive. Use '/' as separator
   * in the path. This should be unique across all sources.
   *
   * @return Name of the artifact.
   */
  String getName();

  /**
   * Get data represented by this resource.
   * @return Resource data as an Object.
   *
   * @throws ArtifactDownloadException
   */
  Object getData() throws ArtifactDownloadException;

  /**
   * A context object which artifact can use to store some context info.
   *
   * @return The context object for this artifact.
   */
  Object getContext();
}
