// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

import java.util.List;

public interface ArtifactSource {
  boolean hasRequiredParams(Params params);
  List<Artifact> getArtifacts(Params params) throws ArtifactDownloadException;
  void process(Params params, Artifact artifact, ZipStream zipStream) throws ArtifactDownloadException;
}
