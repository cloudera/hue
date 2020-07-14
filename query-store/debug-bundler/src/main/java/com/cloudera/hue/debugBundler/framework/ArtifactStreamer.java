// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.apache.commons.lang.exception.ExceptionUtils;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.annotations.VisibleForTesting;
import com.google.inject.Injector;

/**
 * Class to stream all the logs into a zip file.
 */
public class ArtifactStreamer {
  @VisibleForTesting
  static final String ERRORS_ARTIFACT = "error-reports.json";

  @VisibleForTesting
  static final String VERSION_ARTIFACT = "version.json";

  // If there are changes in the structure please increment this version.
  @VisibleForTesting
  static final String VERSION = "3";

  private final Params params;
  private final List<ArtifactSource> pendingSources;
  private final Map<Artifact, ArtifactSource> artifactSource;

  private static final ObjectMapper mapper = new ObjectMapper();

  public ArtifactStreamer(final Injector injector, Params params, List<ArtifactSourceCreator> sourceTypes)
          throws IOException {
    this.params = params;
    this.artifactSource = new HashMap<>();

    this.pendingSources = new ArrayList<>(sourceTypes.size());
    for (ArtifactSourceCreator sourceType : sourceTypes) {
      pendingSources.add(sourceType.getSource(injector));
    }
  }

  public void stream(ZipStream zipStream) throws IOException {
    final Map<String, String> errors = new HashMap<>();
    while (!pendingSources.isEmpty()) {
      List<Artifact> artifacts = collectDownloadableArtifacts(errors);
      if (artifacts.isEmpty() && !pendingSources.isEmpty()) {
        // Artifacts is empty, but some sources are pending.
        // Can be because dagId was given, queryId could not be found, etc ...
        break;
      }

      for (final Artifact artifact : artifacts) {
        try {
          artifactSource.get(artifact).process(params, artifact, zipStream);
        } catch (Throwable t) {
          errors.put(artifact.getName(), ExceptionUtils.getStackTrace(t));
        }
      }
    }

    writeVersion(zipStream);
    writeErrors(zipStream, errors);
  }

  private List<Artifact> collectDownloadableArtifacts(Map<String, String> errors) {
    List<Artifact> artifacts = new ArrayList<>();
    Iterator<ArtifactSource> iter = pendingSources.iterator();
    while (iter.hasNext()) {
      ArtifactSource source = iter.next();
      if (source.hasRequiredParams(params)) {
        try {
          for (Artifact artifact : source.getArtifacts(params)) {
            artifacts.add(artifact);
            artifactSource.put(artifact, source);
          }
        } catch (ArtifactDownloadException e) {
          errors.put(source.getClass().getSimpleName(), ExceptionUtils.getStackTrace(e));
        }
        iter.remove();
      }
    }
    return artifacts;
  }

  private void writeVersion(ZipStream zipStream) throws IOException {
    Map<String, String> data = new HashMap<>();
    data.put("version", VERSION);
    zipStream.writeFile(VERSION_ARTIFACT, mapper.writeValueAsBytes(data));
  }

  private void writeErrors(ZipStream zipStream, Map<String, String> errors) throws IOException {
    if (errors.isEmpty()) {
      return;
    }
    // TODO: Add extra informations - hivetools version, user and other meta data
    // TODO: Add ACL exception in the report.json
    zipStream.writeFile(ERRORS_ARTIFACT, mapper.writeValueAsBytes(errors));
  }
}
