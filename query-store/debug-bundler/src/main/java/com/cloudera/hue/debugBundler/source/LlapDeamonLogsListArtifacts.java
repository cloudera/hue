// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.source;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Calendar;
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

public class LlapDeamonLogsListArtifacts implements ArtifactSource {

  private final AMArtifactsHelper helper;

  @Inject
  public LlapDeamonLogsListArtifacts(AMArtifactsHelper helper) {
    this.helper = helper;
  }

  @Override
  public boolean hasRequiredParams(Params params) {
    if (params.getEnableLogExtraction() && "LLAP".equals(params.getAppType())) {
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
      artifacts.addAll(param.getTaskLogs().getLogListArtifacts(helper, param.getDir("LOGS"), param));
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
      for (Params.ContainerLogsInfo logsInfo : logsInfoList) {
        filterLogs(logsInfo.containerLogInfo, params);
        ((DagParams)artifact.getContext()).getTaskLogs().addLog(
            logsInfo.nodeId, logsInfo.containerId, logsInfo.logAggregationType, logsInfo.containerLogInfo);
      }
      // This is not correct, but we have no way to tell all the logs have downloaded
      ((DagParams)artifact.getContext()).getTaskLogs().finishLogs();
    }
  }

  private void filterLogs(List<Params.ContainerLogInfo> containerLogInfo, Params params) {
    String hiveQueryId = params.getHiveQueryId();
    Iterator<Params.ContainerLogInfo> iter = containerLogInfo.iterator();
    while (iter.hasNext()) {
      String fileName = iter.next().fileName;
      if (fileName.startsWith("llap-daemon")) {
        long startTime = getLlapLogsStartTime(fileName);
        // Hourly rotation.
        if (startTime > 0 && !params.shouldIncludeArtifact(startTime, startTime + 60 * 60 * 1000)) {
          iter.remove();
        }
      } else if (fileName.startsWith("llapdaemon_history")) {
        long startTime = getLlapHistoryStartTime(fileName);
        // Daily rotation.
        long endTime = startTime + 24 * 60 * 60 * 1000;
        if (startTime > 0 && !params.shouldIncludeArtifact(startTime, endTime)) {
          iter.remove();
        }
      } else if (!fileName.startsWith(hiveQueryId) && !fileName.startsWith("gc.log")) {
        iter.remove();
      }
    }
  }

  // llapdeamon-history.log_2017-11-25_1.done
  private static final Pattern llapDaemonHistoryLogPattern =
      Pattern.compile("log_(\\d+)-(\\d+)-(\\d+)_\\d+");
  private long getLlapHistoryStartTime(String fileName) {
    long startTime = 0;
    Matcher matcher = llapDaemonHistoryLogPattern.matcher(fileName);
    if (matcher.find()) {
      int year = Integer.parseInt(matcher.group(1));
      int month = Integer.parseInt(matcher.group(2));
      int date = Integer.parseInt(matcher.group(3));
      startTime = new Calendar.Builder().setDate(year, month - 1, date).build()
          .getTimeInMillis();
    } else if (fileName.endsWith(".log")) {
      Calendar cal = Calendar.getInstance();
      cal.set(Calendar.HOUR_OF_DAY, 0);
      cal.set(Calendar.MINUTE, 0);
      cal.set(Calendar.SECOND, 0);
      cal.set(Calendar.MILLISECOND, 0);
      startTime = cal.getTimeInMillis();
    }
    return startTime;
  }

  // LLAP Deamon log: llap-deamon-<user>-<nodehost>.log_2017-11-25-00_1.done
  private static final Pattern llapDaemonLogPattern =
      Pattern.compile("log_(\\d+)-(\\d+)-(\\d+)-(\\d+)_\\d+");
  private long getLlapLogsStartTime(String fileName) {
    long startTime = 0;
    Matcher matcher = llapDaemonLogPattern.matcher(fileName);
    if (matcher.find()) {
      int year = Integer.parseInt(matcher.group(1));
      int month = Integer.parseInt(matcher.group(2));
      int date = Integer.parseInt(matcher.group(3));
      int hour = Integer.parseInt(matcher.group(4));
      startTime = new Calendar.Builder().setDate(year, month - 1, date)
          .setTimeOfDay(hour, 0, 0).build().getTimeInMillis();
    } else if (fileName.endsWith(".log")) {
      Calendar cal = Calendar.getInstance();
      cal.set(Calendar.MINUTE, 0);
      cal.set(Calendar.SECOND, 0);
      cal.set(Calendar.MILLISECOND, 0);
      startTime = cal.getTimeInMillis();
    }
    return startTime;
  }
}
