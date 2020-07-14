// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.source;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.IOUtils;

import com.cloudera.hue.debugBundler.framework.Artifact;
import com.cloudera.hue.debugBundler.framework.ArtifactDownloadException;
import com.cloudera.hue.debugBundler.framework.ArtifactSource;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.debugBundler.framework.Params.DagParams;
import com.cloudera.hue.debugBundler.framework.ZipStream;
import com.cloudera.hue.debugBundler.helpers.AMArtifactsHelper;
import com.fasterxml.jackson.annotation.JsonRootName;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.inject.Inject;

public class TezAMInfoArtifacts implements ArtifactSource {

  protected final AMArtifactsHelper helper;
  protected final ObjectMapper mapper;

  @Inject
  public TezAMInfoArtifacts(AMArtifactsHelper helper) {
    this.helper = helper;
    this.mapper = new ObjectMapper();
    mapper.configure(DeserializationFeature.UNWRAP_ROOT_VALUE, true);
    mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    mapper.configure(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY, true);
  }

  public String getArtifactName(DagParams params) {
    return params.getDir("TEZ_AM/INFO.json");
  }

  @Override
  public boolean hasRequiredParams(Params params) {
     for (DagParams param : params.getDagParams()) {
       if (param.getAmAppId() != null) {
         return true;
       }
     }
     return false;
  }

  @Override
  public List<Artifact> getArtifacts(Params params) {
    List<Artifact> artifacts = new ArrayList<>();
    for (DagParams param : params.getDagParams()) {
      if (param.getAmAppId() != null) {
        artifacts.add(helper.getAMInfoArtifact(getArtifactName(param), param.getAmAppId(), param));
      }
    }
    return artifacts;
  }

  @JsonRootName("appAttempts")
  public static class AMInfo {
    public List<AppAttempt> appAttempt;
  }

  public static class AppAttempt {
    public int id;
    public long startTime;
    public long finishedTime;
    public String containerId;
    public String nodeId;
    public String appAttemptId;
  }

  @Override
  public void process(Params params, Artifact artifact, ZipStream zipStream) throws ArtifactDownloadException {
    try {
      byte[] data = IOUtils.toByteArray((InputStream)artifact.getData());
      updateParams(params, artifact, new ByteArrayInputStream(data));
      zipStream.writeFile(artifact.getName(), data);
    } catch (IOException e) {
      throw new ArtifactDownloadException(e);
    }
  }

  public void updateParams(Params params, Artifact artifact, InputStream stream) throws IOException {
    DagParams param = ((DagParams)artifact.getContext());
    Params.AppLogs amLogs = param.getAmLogs();
    if (amLogs.isFinishedContainers()) {
      return;
    }

    if (artifact.getName().equals(getArtifactName(param))) {
      AMInfo amInfo = mapper.readValue(stream, AMInfo.class);
      if (amInfo != null && amInfo.appAttempt != null) {
        for (AppAttempt attempt: amInfo.appAttempt) {
          if (params.shouldIncludeArtifact(attempt.startTime, attempt.finishedTime)) {
            amLogs.addContainer(attempt.nodeId, attempt.containerId);
          }
        }
        amLogs.finishContainers();
      }
    }
  }

}
