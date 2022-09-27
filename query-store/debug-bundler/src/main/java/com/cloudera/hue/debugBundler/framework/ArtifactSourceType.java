// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

import java.util.Arrays;
import java.util.List;

import com.cloudera.hue.debugBundler.source.HiveStudioArtifacts;
import com.cloudera.hue.debugBundler.source.LlapDeamonLogsArtifacts;
import com.cloudera.hue.debugBundler.source.LlapDeamonLogsListArtifacts;
import com.cloudera.hue.debugBundler.source.TezAMInfoArtifacts;
import com.cloudera.hue.debugBundler.source.TezAMLogsArtifacts;
import com.cloudera.hue.debugBundler.source.TezAMLogsListArtifacts;
import com.cloudera.hue.debugBundler.source.TezHDFSArtifacts;
import com.cloudera.hue.debugBundler.source.TezTasksLogsArtifacts;
import com.cloudera.hue.debugBundler.source.TezTasksLogsListArtifacts;
import com.google.inject.Injector;

public enum ArtifactSourceType implements ArtifactSourceCreator {

  // From Hive Studio - Needs Query ID
  HIVE_STUDIO(HiveStudioArtifacts.class),

  TEZ_HDFS(TezHDFSArtifacts.class),

  // From Tez AM - Needs App ID
  TEZ_AM_INFO(TezAMInfoArtifacts.class),
  TEZ_AM_LOG_INFO(TezAMLogsListArtifacts.class),
  TEZ_AM_LOGS(TezAMLogsArtifacts.class),
  // TEZ_AM_JMX(DummyArtifacts.class),
  // TEZ_AM_STACK(DummyArtifacts.class),

  // From Tez AHS - Needs Node ID / Container ID list.
  TEZ_TASK_LOGS_INFO(TezTasksLogsListArtifacts.class),
  TEZ_TASK_LOGS(TezTasksLogsArtifacts.class),

  // LLAP
  LLAP_DEAMON_LOGS_INFO(LlapDeamonLogsListArtifacts.class),
  LLAP_DEAMON_LOGS(LlapDeamonLogsArtifacts.class),
  ;

  private final Class<? extends ArtifactSource> sourceClass;
  private ArtifactSourceType(Class<? extends ArtifactSource> sourceClass) {
    this.sourceClass = sourceClass;
  }

  public ArtifactSource getSource(Injector injector) {
    return injector.getInstance(sourceClass);
  }

  public static List<ArtifactSourceCreator> getValues(String logSource) {
    switch (logSource.toLowerCase()) {
      case "k8s":
        return Arrays.asList(HIVE_STUDIO, TEZ_HDFS);
      default:
        return Arrays.asList(HIVE_STUDIO, TEZ_HDFS, TEZ_AM_INFO);
    }
  }
}
