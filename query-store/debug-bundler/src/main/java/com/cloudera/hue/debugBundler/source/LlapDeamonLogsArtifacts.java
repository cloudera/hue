// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.source;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import com.cloudera.hue.debugBundler.framework.Artifact;
import com.cloudera.hue.debugBundler.framework.ArtifactDownloadException;
import com.cloudera.hue.debugBundler.framework.ArtifactSource;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.debugBundler.framework.Params.DagParams;
import com.cloudera.hue.debugBundler.framework.ZipStream;
import com.cloudera.hue.debugBundler.helpers.AMArtifactsHelper;
import com.google.inject.Inject;

public class LlapDeamonLogsArtifacts implements ArtifactSource {

  private final AMArtifactsHelper helper;

  @Inject
  public LlapDeamonLogsArtifacts(AMArtifactsHelper helper) {
    this.helper = helper;
  }

  @Override
  public boolean hasRequiredParams(Params params) {
    if (params.getEnableLogExtraction() && "LLAP".equals(params.getAppType())) {
      for (DagParams param : params.getDagParams()) {
        if (!param.getTaskLogs().isFinishedLogs()) {
          return false;
        }
      }
      return true;
    }
    return false;
  }

  @Override
  public List<Artifact> getArtifacts(Params params) {
    List<Artifact> artifacts = new ArrayList<>();
    for (DagParams param : params.getDagParams()) {
      artifacts.addAll(param.getTaskLogs().getLogArtifacts(helper, param.getDir("LLAP/LOGS")));
    }
    return artifacts;
  }

  @Override
  public void process(Params params, Artifact artifact, ZipStream zipStream) throws ArtifactDownloadException {
    try {
      zipStream.writeFile(artifact.getName(), (InputStream)artifact.getData());
    } catch (IOException e) {
      throw new ArtifactDownloadException(e);
    }
  }

}
