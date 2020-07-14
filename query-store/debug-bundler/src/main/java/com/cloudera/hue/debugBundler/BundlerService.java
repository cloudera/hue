// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler;

import java.io.IOException;
import java.util.List;
import java.util.regex.Pattern;

import javax.inject.Inject;
import javax.inject.Singleton;
import javax.ws.rs.core.StreamingOutput;

import com.cloudera.hue.debugBundler.framework.ArtifactSourceCreator;
import com.cloudera.hue.debugBundler.framework.ArtifactSourceType;
import com.cloudera.hue.debugBundler.framework.ArtifactStreamer;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.debugBundler.framework.ZipStream;
import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.config.DasConfiguration.ConfVar;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezAppInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.VertexInfoRepository;
import com.google.inject.Binder;
import com.google.inject.Guice;
import com.google.inject.Injector;
import com.google.inject.Module;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
public class BundlerService {
  private static final ConfVar<Boolean> EXTRACT_LOGS_CONF =
      new ConfVar<>("hue.query-processor.debug-bundler.extract-logs", true);
  private static final ConfVar<String> LOGS_SOURCE_CONF =
      new ConfVar<>("hue.query-processor.debug-bundler.logs-source", "yarn");

  private final DasConfiguration dasConfig;
  private final HiveQueryBasicInfoRepository hiveQueryRepo;
  private final HiveQueryExtendedInfoRepository hiveExtRepo;
  private final TezDagBasicInfoRepository dagBasicRepo;
  private final TezDagExtendedInfoRepository dagExtRepo;
  private final VertexInfoRepository vertexRepo;
  private final TezAppInfoRepository appRepo;

  @Inject
  public BundlerService(DasConfiguration dasConfig, HiveQueryBasicInfoRepository hiveQueryRepo,
      HiveQueryExtendedInfoRepository hiveExtRepo, TezDagBasicInfoRepository dagBasicRepo,
      TezDagExtendedInfoRepository dagExtRepo, VertexInfoRepository vertexRepo, TezAppInfoRepository appRepo) {
    this.dasConfig = dasConfig;
    this.hiveQueryRepo = hiveQueryRepo;
    this.hiveExtRepo = hiveExtRepo;
    this.dagBasicRepo = dagBasicRepo;
    this.dagExtRepo = dagExtRepo;
    this.vertexRepo = vertexRepo;
    this.appRepo = appRepo;
  }

  // Only allow alpha-numerics, '-' and '_' in the fileName.
  private static final Pattern validFileName = Pattern.compile("^[0-9a-zA-Z\\-_]+$");
  public String constructFileName(String queryID, String suffix) {
    String fileName = queryID;

    if (!validFileName.matcher(fileName).matches()) {
      fileName = "artifact_bundle";
    }

    return String.format("%s-%s.zip", fileName, suffix);
  }

  public StreamingOutput streamBundle(String queryID, String user) throws IOException {
    Params params = new Params();
    params.setHiveQueryId(queryID);
    params.setEnableLogExtraction(dasConfig.getConf(EXTRACT_LOGS_CONF));

    // Set user
    params.setRemoteUser(user);

    StreamingOutput streamingOutput = outputStream -> {
      List<ArtifactSourceCreator> sourceTypes = ArtifactSourceType.getValues(dasConfig.getConf(LOGS_SOURCE_CONF));

      Injector injector = Guice.createInjector(new Module() {
        @Override
        public void configure(Binder binder) {
          binder.bind(DasConfiguration.class).toInstance(dasConfig);
          binder.bind(HiveQueryBasicInfoRepository.class).toInstance(hiveQueryRepo);
          binder.bind(HiveQueryExtendedInfoRepository.class).toInstance(hiveExtRepo);
          binder.bind(TezDagBasicInfoRepository.class).toInstance(dagBasicRepo);
          binder.bind(TezDagExtendedInfoRepository.class).toInstance(dagExtRepo);
          binder.bind(TezAppInfoRepository.class).toInstance(appRepo);
          binder.bind(VertexInfoRepository.class).toInstance(vertexRepo);
        }
      });

      try(ZipStream zipStream = new ZipStream(outputStream)) {
        log.info("Starting debug bundle streaming!");
        ArtifactStreamer streamer = new ArtifactStreamer(injector, params, sourceTypes);
        streamer.stream(zipStream);
        log.info("Streaming of debug bundle completed!");
      } catch(Exception e) {
        log.error("Error while streaming debug bundle!", e);
      }

    };

    return streamingOutput;
  }

}
