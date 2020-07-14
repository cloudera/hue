// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map.Entry;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import com.cloudera.hue.debugBundler.helpers.AMArtifactsHelper;
import com.google.common.base.Strings;

import lombok.Data;
import lombok.extern.slf4j.Slf4j;

@Data
@Slf4j
public class Params {
  private String appType;
  private String remoteUser;
  private String domainId;

  private boolean enableLogExtraction = true;

  // Hive information.
  private String hiveQueryId;

  // Start and End time of query/dag.
  private long startTime = 0;
  private long endTime = Long.MAX_VALUE;
  private final List<DagParams> dagParams = new ArrayList<>();

  @Data
  public static class DagParams {
    private final int count;

    // Tez information.
    private final String dagId;
    private final String amAppId;

    private final AppLogs amLogs = new AppLogs();
    private final AppLogs taskLogs = new AppLogs();

    public String getDir(String extraPath) {
      return "DAG" + count + "/" + extraPath;
    }
  }

  public static class AppLogs {
    // logFilePath(containerId/fileName) -> LogFileInfo
    private final ConcurrentHashMap<String, LogFileInfo> appLogs = new ConcurrentHashMap<>();
    // nodeId -> Set(containerIds)
    private final ConcurrentHashMap<String, Set<String>> containers = new ConcurrentHashMap<>();

    private boolean finishedContainers;
    private boolean finishedLogs;

    public int containersCount() {
      return containers.size();
    }

    public void addLog(String nodeId, String containerId, String aggregationType, List<ContainerLogInfo> logs)  {
      for (ContainerLogInfo containerLogInfo : logs) {
        String filePath = containerId + "/" + containerLogInfo.fileName;
        if (appLogs.containsKey(filePath)) {
          LogFileInfo logFileInfo = appLogs.get(filePath);
          if (Objects.equals(logFileInfo.aggregationType, aggregationType)) {
            log.warn("Invalid log data. Duplicate file names.");
          } else if("AGGREGATED".equals(aggregationType)) { // AGGREGATED logs have precedence over other logs
            logFileInfo.aggregationType = aggregationType;
            logFileInfo.nodeId = nodeId;
          }
        } else {
          appLogs.put(filePath, new LogFileInfo(containerLogInfo.fileName, aggregationType, nodeId, containerId));
        }
      }
    }

    public void addContainer(String nodeId, String containerId) {
      if (!containers.containsKey(nodeId)) {
        containers.putIfAbsent(nodeId, new HashSet<>());
      }
      containers.get(nodeId).add(containerId);
    }

    public boolean isFinishedContainers() {
      return finishedContainers;
    }

    public void finishContainers() {
      this.finishedContainers = true;
    }

    public boolean isFinishedLogs() {
      return finishedLogs;
    }

    public void finishLogs() {
      this.finishedLogs = true;
    }

    public List<Artifact> getLogListArtifacts(AMArtifactsHelper helper, String name, Object context) {
      List<Artifact> artifacts = new ArrayList<>();
      for (Entry<String, Set<String>> entry : containers.entrySet()) {
        for (String containerId : entry.getValue()) {
          artifacts.add(helper.getLogListArtifact(name + "/" + containerId + ".logs.json",
            containerId, entry.getKey(), context));
        }
      }
      return artifacts;
    }

    public List<Artifact> getLogArtifacts(AMArtifactsHelper helper, String name) {
      List<Artifact> artifacts = new ArrayList<>();
      for (LogFileInfo fileInfo : appLogs.values()) {
        artifacts.add(helper.getLogArtifact(name + "/" + fileInfo.containerId + "/" + fileInfo.fileName,
          fileInfo.containerId, fileInfo.fileName, fileInfo.nodeId));
      }
      return artifacts;
    }
  }

  public static class LogFileInfo {
    public String fileName;
    public String aggregationType;
    public String nodeId;
    public String containerId;

    public LogFileInfo(String fileName, String aggregationType, String nodeId, String containerId) {
      this.fileName = fileName;
      this.aggregationType = aggregationType;
      this.nodeId = nodeId;
      this.containerId = containerId;
    }
  }

  public static class ContainerLogInfo {
    public ContainerLogInfo() {}
    public ContainerLogInfo(String fileName, long fileSize, String lastModifiedTime) {
      this.fileName = fileName;
      this.fileSize = fileSize;
      this.lastModifiedTime = lastModifiedTime;
    }
    public String fileName;
    public long fileSize;
    public String lastModifiedTime;
  }

  public static class ContainerLogsInfo {
    public List<ContainerLogInfo> containerLogInfo;
    public String containerId;
    public String nodeId;
    public String logAggregationType;
  }

  public boolean getUsesTez() {
    if(!Strings.isNullOrEmpty(appType)) {
      switch(appType) {
        case "TEZ":
        case "LLAP":
          return true;
      }
    }
    return false;
  }

  public boolean getEnableLogExtraction() {
    return enableLogExtraction && dagParams.size() > 0;
  }

  public void updateStartTime(long startTime) {
    if (this.startTime == 0 || startTime < this.startTime) {
      this.startTime = startTime;
    }
  }

  public void updateEndTime(long endTime) {
    if (this.endTime == Long.MAX_VALUE || endTime > this.endTime) {
      this.endTime = endTime;
    }
  }

  public boolean shouldIncludeArtifact(long startTime, long endTime) {
    if (endTime == 0) {
      endTime = Long.MAX_VALUE;
    }
    // overlap is true if one of them started when other was running.
    return (this.startTime <= startTime && startTime <= this.endTime) ||
        (startTime <= this.startTime && this.startTime <= endTime);
  }
}
