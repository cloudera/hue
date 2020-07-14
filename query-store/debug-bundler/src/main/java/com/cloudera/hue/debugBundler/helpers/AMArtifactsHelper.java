// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.helpers;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;

import org.apache.commons.io.IOUtils;
import org.apache.hadoop.http.HttpConfig;
import org.apache.hadoop.yarn.conf.YarnConfiguration;

import com.cloudera.hue.debugBundler.framework.Artifact;
import com.cloudera.hue.debugBundler.framework.HttpArtifact;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.querystore.common.util.HadoopHTTPUtils;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.inject.Inject;
import com.google.inject.Singleton;

@Singleton
public class AMArtifactsHelper {

  private static final String RM_WS_PREFIX = "/ws/v1/cluster";
  private static final String AHS_WS_PREFIX = "/ws/v1/applicationhistory";

  private final String rmAddress;
  private final String ahsAddress;
  private final ObjectMapper objectMapper;
  private final HadoopHTTPUtils httpUtils;

  @Inject
  public AMArtifactsHelper(HadoopHTTPUtils httpUtils, YarnConfiguration conf) {
    this.httpUtils = httpUtils;
    this.objectMapper = new ObjectMapper();
    objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
    objectMapper.configure(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY, true);

    String yarnHTTPPolicy = conf.get(YarnConfiguration.YARN_HTTP_POLICY_KEY,
      YarnConfiguration.YARN_HTTP_POLICY_DEFAULT);

    if (HttpConfig.Policy.HTTPS_ONLY == HttpConfig.Policy.fromString(yarnHTTPPolicy)) {
      rmAddress = "https://" + conf.get(YarnConfiguration.RM_WEBAPP_HTTPS_ADDRESS,
        YarnConfiguration.DEFAULT_RM_WEBAPP_HTTPS_ADDRESS);
      ahsAddress = "https://" + conf.get(YarnConfiguration.TIMELINE_SERVICE_WEBAPP_HTTPS_ADDRESS,
        YarnConfiguration.DEFAULT_TIMELINE_SERVICE_WEBAPP_HTTPS_ADDRESS);
    } else {
      rmAddress = "http://" + conf.get(YarnConfiguration.RM_WEBAPP_ADDRESS,
        YarnConfiguration.DEFAULT_RM_WEBAPP_ADDRESS);
      ahsAddress = "http://" + conf.get(YarnConfiguration.TIMELINE_SERVICE_WEBAPP_ADDRESS,
        YarnConfiguration.DEFAULT_TIMELINE_SERVICE_WEBAPP_ADDRESS);
    }
  }

  public Artifact getAMInfoArtifact(String name, String appId, Object context) {
    String attemptsUrl = rmAddress + RM_WS_PREFIX + "/apps/" + appId + "/appattempts";
    return new HttpArtifact(httpUtils, name, attemptsUrl, context);
  }

  public Artifact getLogListArtifact(String name, String containerId, String nodeId, Object context) {
    String logsListUrl = ahsAddress + AHS_WS_PREFIX + "/containers/" + containerId + "/logs";
    if (nodeId != null) {
      logsListUrl += "?nm.id=" + nodeId;
    }
    return new HttpArtifact(httpUtils, name, logsListUrl, context);
  }

  public Artifact getLogArtifact(String name, String containerId, String logFile, String nodeId) {
    String logUrl = ahsAddress + AHS_WS_PREFIX + "/containers/" + containerId + "/logs/" + logFile;
    if (nodeId != null) {
      logUrl += "?nm.id=" + nodeId;
    }
    return new HttpArtifact(httpUtils, name, logUrl, null);
  }

  public static class ContainerLogs {
    public List<Params.ContainerLogsInfo> containerLogsInfo;
  }

  public List<Params.ContainerLogsInfo> parseContainerLogs(InputStream stream) throws IOException {
    TypeReference<List<Params.ContainerLogsInfo>> typeRef = new TypeReference<List<Params.ContainerLogsInfo>>(){};
    // The api return with containerLogsInfo or without it, hence trying both formats.
    byte[] streamCache = IOUtils.toByteArray(stream);
    try {
      return objectMapper.readValue(streamCache, ContainerLogs.class).containerLogsInfo;
    } catch (JsonProcessingException e) {
      return objectMapper.readValue(streamCache, typeRef);
    }
  }

}
