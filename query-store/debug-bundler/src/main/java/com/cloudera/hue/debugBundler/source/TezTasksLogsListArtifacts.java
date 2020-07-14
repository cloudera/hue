// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.source;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import com.cloudera.hue.debugBundler.framework.Artifact;
import com.cloudera.hue.debugBundler.framework.ArtifactDownloadException;
import com.cloudera.hue.debugBundler.framework.ArtifactSource;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.debugBundler.framework.Params.DagParams;
import com.cloudera.hue.debugBundler.framework.ZipStream;
import com.cloudera.hue.debugBundler.helpers.AMArtifactsHelper;
import com.google.inject.Inject;

public class TezTasksLogsListArtifacts implements ArtifactSource {
  private final AMArtifactsHelper helper;

  @Inject
  public TezTasksLogsListArtifacts(AMArtifactsHelper helper) {
    this.helper = helper;
  }

  @Override
  public boolean hasRequiredParams(Params params) {
    if (params.getEnableLogExtraction() && params.getAppType() != null && !params.getAppType().equals("LLAP") &&
        params.getUsesTez()) {
      for (DagParams param : params.getDagParams()) {
        if (!param.getTaskLogs().isFinishedContainers()) {
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
      artifacts.addAll(param.getTaskLogs().getLogListArtifacts(helper, param.getDir("TEZ_TASKS/LOGS"), param));
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
        filterLogs(logsInfo.containerLogInfo, param);
        param.getTaskLogs().addLog(logsInfo.nodeId, logsInfo.containerId,
            logsInfo.logAggregationType, logsInfo.containerLogInfo);
      }
      // This is not correct, but we have no way to tell all the logs have downloaded
      param.getTaskLogs().finishLogs();
    }
  }

  private void filterLogs(List<Params.ContainerLogInfo> containerLogInfo, DagParams param) {
    String syslogPrefix = "syslog_attempt_" + param.getDagId().substring(4) + "_";
    Iterator<Params.ContainerLogInfo> iter = containerLogInfo.iterator();
    while (iter.hasNext()) {
      String fileName = iter.next().fileName;
      if (fileName.startsWith("syslog_attempt_") && !fileName.startsWith(syslogPrefix)) {
        iter.remove();
      }
    }
  }

}
