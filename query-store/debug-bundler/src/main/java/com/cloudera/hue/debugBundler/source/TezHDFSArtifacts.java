// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.source;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.cloudera.hue.debugBundler.entities.history.DAGEntityType;
import com.cloudera.hue.debugBundler.entities.history.HistoryEntity;
import com.cloudera.hue.debugBundler.entities.history.TaskAttemptEntityType;
import com.cloudera.hue.debugBundler.entities.history.TaskEntityType;
import com.cloudera.hue.debugBundler.entities.history.VertexEntityType;
import com.cloudera.hue.debugBundler.framework.Artifact;
import com.cloudera.hue.debugBundler.framework.ArtifactDownloadException;
import com.cloudera.hue.debugBundler.framework.ArtifactSource;
import com.cloudera.hue.debugBundler.framework.HistoryEventsArtifact;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.debugBundler.framework.Params.DagParams;
import com.cloudera.hue.debugBundler.framework.ZipStream;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.inject.Inject;

public class TezHDFSArtifacts implements ArtifactSource {

  private static final Pattern LOGS_URL_PATTERN = Pattern.compile(
    "^.*applicationhistory/containers/(.*?)/logs.*\\?nm.id=(.+:[\\d+]+).*$");

  private final TezDagBasicInfoRepository dagBasicRepo;

  private final DAGEntityType dagEntityType;
  private final VertexEntityType vertexEntityType;
  private final TaskEntityType taskEntityType;
  private final TaskAttemptEntityType taskAttemptEntityType;
  private final ObjectMapper objectMapper;

  @Inject
  public TezHDFSArtifacts(TezDagBasicInfoRepository dagBasicRepo,
                          DAGEntityType dagEntityType, VertexEntityType vertexEntityType,
                          TaskEntityType taskEntityType, TaskAttemptEntityType taskAttemptEntityType,
                          ObjectMapper objectMapper) {
    this.dagBasicRepo = dagBasicRepo;

    this.dagEntityType = dagEntityType;
    this.vertexEntityType = vertexEntityType;
    this.taskEntityType = taskEntityType;
    this.taskAttemptEntityType = taskAttemptEntityType;

    this.objectMapper = objectMapper;
  }

  @Override
  public List<Artifact> getArtifacts(Params params) {
    List<Artifact> artifacts = new ArrayList<>();
    for (DagParams param : params.getDagParams()) {
      Optional<TezDagBasicInfo> dagInfo = dagBasicRepo.findByDagId(param.getDagId());
      if (!dagInfo.isPresent()) {
        continue;
      }

      org.apache.hadoop.fs.Path sourceFile = new org.apache.hadoop.fs.Path(dagInfo.get().getSourceFile());

      artifacts.add(new HistoryEventsArtifact(dagEntityType, sourceFile, param));
      artifacts.add(new HistoryEventsArtifact(vertexEntityType, sourceFile, param));
      artifacts.add(new HistoryEventsArtifact(taskEntityType, sourceFile, param));
      artifacts.add(new HistoryEventsArtifact(taskAttemptEntityType, sourceFile, param));
    }
    return artifacts;
  }

  @Override
  public void process(Params params, Artifact artifact, ZipStream zipStream) throws ArtifactDownloadException {
    try {
      @SuppressWarnings("unchecked")
      HashMap<String, Object> data = (HashMap<String, Object>)artifact.getData();
      updateParams(params, artifact, data);
      zipStream.writeFile(artifact.getName(), objectMapper.writeValueAsBytes(data));
    } catch (IOException e) {
      throw new ArtifactDownloadException(e);
    }
  }

  public void updateParams(Params params, Artifact artifact, HashMap<String, Object> data) throws IOException {
    DagParams param = (DagParams)artifact.getContext();
    String taskAttemptKey = taskAttemptEntityType.getName().toLowerCase();

    if(data.containsKey(taskAttemptKey)) {
      Params.AppLogs appLogs = param.getTaskLogs();
      if (appLogs.isFinishedContainers()) {
        return;
      }

      @SuppressWarnings("unchecked")
      Collection<HistoryEntity> entities = (Collection<HistoryEntity>)data.get(taskAttemptKey);

      for (HistoryEntity entity : entities) {
        HashMap<String, String> taskAttemptStartedEvent = entity.getEvents().get(0);

        String logsUrl = taskAttemptStartedEvent.get("completedLogsURL");
        if (logsUrl == null || logsUrl.isEmpty()) {
          continue;
        }

        Matcher matcher = LOGS_URL_PATTERN.matcher(logsUrl);
        if (matcher.matches()) {
          String containerId = matcher.group(1);
          String nodeId = matcher.group(2);
          appLogs.addContainer(nodeId, containerId);
        } else {
          String containerId = taskAttemptStartedEvent.get("containerId");
          String nodeId = taskAttemptStartedEvent.get("nodeId");
          if (!containerId.isEmpty() && !nodeId.isEmpty()) {
            appLogs.addContainer(nodeId, containerId);
          }
        }
      }

      appLogs.finishContainers();
    }
  }

  @Override
  public boolean hasRequiredParams(Params params) {
    for (DagParams param : params.getDagParams()) {
      if (param.getDagId() != null) {
        return true;
      }
    }
    return false;
  }
}
