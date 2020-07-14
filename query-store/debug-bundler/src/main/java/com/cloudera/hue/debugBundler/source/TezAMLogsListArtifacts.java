// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.source;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.cloudera.hue.debugBundler.framework.Artifact;
import com.cloudera.hue.debugBundler.framework.ArtifactDownloadException;
import com.cloudera.hue.debugBundler.framework.ArtifactSource;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.debugBundler.framework.Params.DagParams;
import com.cloudera.hue.debugBundler.framework.ZipStream;
import com.cloudera.hue.debugBundler.helpers.AMArtifactsHelper;
import com.google.inject.Inject;

public class TezAMLogsListArtifacts implements ArtifactSource {

  private final AMArtifactsHelper helper;

  @Inject
  public TezAMLogsListArtifacts(AMArtifactsHelper helper) {
    this.helper = helper;
  }

  @Override
  public boolean hasRequiredParams(Params params) {
    if (params.getEnableLogExtraction()) {
      for (DagParams param : params.getDagParams()) {
        if (!param.getAmLogs().isFinishedContainers()) {
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
      artifacts.addAll(param.getAmLogs().getLogListArtifacts(helper, param.getDir("TEZ_AM/LOGS"), param));
    }
    return artifacts;
  }

  @Override
  public void process(Params params, Artifact artifact, ZipStream zipStream) throws ArtifactDownloadException {
    try {
      updateParams(params, artifact, (InputStream)artifact.getData());
    } catch (IOException e) {
      throw new ArtifactDownloadException(e);
    }
  }

  public void updateParams(Params params, Artifact artifact, InputStream stream) throws IOException {
    List<Params.ContainerLogsInfo> logsInfoList = helper.parseContainerLogs(stream);
    if (logsInfoList != null) {
      DagParams param = (DagParams)artifact.getContext();
      for (Params.ContainerLogsInfo logsInfo : logsInfoList) {
        filterLogs(logsInfo.containerLogInfo, param.getDagId());
        param.getAmLogs().addLog(logsInfo.nodeId, logsInfo.containerId, logsInfo.logAggregationType,
            logsInfo.containerLogInfo);
      }
      // This is not correct, but we have no way to tell all the logs have downloaded
      param.getAmLogs().finishLogs();
    }
  }

  private static Pattern dagPattern = Pattern.compile("dag_\\d+_\\d+_\\d+");
  private void filterLogs(List<Params.ContainerLogInfo> logs, String dagId) {
    Iterator<Params.ContainerLogInfo> iter = logs.iterator();
    while (iter.hasNext()) {
      Matcher matcher = dagPattern.matcher(iter.next().fileName);
      if (matcher.find() && !matcher.group().equals(dagId)) {
        iter.remove();
      }
    }
  }
}
