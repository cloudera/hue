// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.lifecycle;

import java.io.IOException;

import javax.inject.Inject;
import javax.inject.Singleton;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.hive.conf.HiveConf.ConfVars;
import org.apache.hadoop.hive.ql.hooks.proto.HiveHookEvents.HiveHookEventProto;
import org.apache.hadoop.yarn.util.SystemClock;
import org.apache.tez.dag.api.TezConfiguration;
import org.apache.tez.dag.history.logging.proto.DatePartitionedLogger;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.HistoryEventProto;
import org.apache.tez.dag.history.logging.proto.TezProtoLoggers;

import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.entities.FileStatusEntity.FileStatusType;
import com.cloudera.hue.querystore.common.repository.FileStatusPersistenceManager;
import com.cloudera.hue.querystore.common.repository.transaction.TransactionManager;
import com.cloudera.hue.querystore.eventProcessor.pipeline.EventProcessorPipeline;
import com.cloudera.hue.querystore.eventProcessor.processors.HiveEventProcessorDispatcher;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventProcessorDispatcher;
import com.codahale.metrics.MetricRegistry;

import io.dropwizard.lifecycle.Managed;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
public class EventProcessorManager implements Managed {
  private final Configuration hadoopConfiguration;
  private final DasConfiguration eventProcessingConfig;
  private final TezEventProcessorDispatcher tezEventProcessor;
  private final HiveEventProcessorDispatcher hiveEventProcessor;
  private final FileStatusPersistenceManager fsPersistenceManager;
  private final TransactionManager txnManager;
  private final MetricRegistry metricRegistry;

  private EventProcessorPipeline<HistoryEventProto> tezEventsPipeline;
  private EventProcessorPipeline<HistoryEventProto> tezAppEventsPipeline;
  private EventProcessorPipeline<HiveHookEventProto> hiveEventsPipeline;

  @Inject
  public EventProcessorManager(DasConfiguration eventProcessingConfig,
                               Configuration hadoopConfiguration,
                               TezEventProcessorDispatcher tezEventProcessor,
                               HiveEventProcessorDispatcher hiveEventProcessor,
                               FileStatusPersistenceManager fsPersistenceManager,
                               TransactionManager txnManager,
                               MetricRegistry metricRegistry) {
    this.eventProcessingConfig = eventProcessingConfig;
    this.hadoopConfiguration = hadoopConfiguration;
    this.tezEventProcessor = tezEventProcessor;
    this.hiveEventProcessor = hiveEventProcessor;
    this.fsPersistenceManager = fsPersistenceManager;
    this.txnManager = txnManager;
    this.metricRegistry = metricRegistry;
  }

  @Override
  public void start() {
    log.info("Starting");
    startTezPipeline();
    startHivePipeline();
    log.info("Started");
  }

  @Override
  public void stop() {
    log.info("EventProcessorManager: stopping");
    tezEventsPipeline.shutdown();
    tezAppEventsPipeline.shutdown();
    hiveEventsPipeline.shutdown();
    tezEventsPipeline.awaitTermination();
    tezAppEventsPipeline.awaitTermination();
    hiveEventsPipeline.awaitTermination();
    log.info("EventProcessorManager: stopped");
  }

  public void forceRefresh() {
    log.info("EventProcessorManager: forceRefresh");
    tezEventsPipeline.forceRefresh();
    tezAppEventsPipeline.forceRefresh();
    hiveEventsPipeline.forceRefresh();
  }

  public long getQueryUpdateTime() {
    return hiveEventsPipeline.getUpdateTime();
  }

  private void startTezPipeline() {
    log.info("Starting tez events pipeline");
    try {
      // TODO: This should be read from tez-site.xml
      String tezBaseDir = eventProcessingConfig.getString(
          TezConfiguration.TEZ_HISTORY_LOGGING_PROTO_BASE_DIR, null);
      if (tezBaseDir == null) {
        throw new RuntimeException("Please configure: " +
            TezConfiguration.TEZ_HISTORY_LOGGING_PROTO_BASE_DIR);
      }
      hadoopConfiguration.set(TezConfiguration.TEZ_HISTORY_LOGGING_PROTO_BASE_DIR, tezBaseDir);

      TezProtoLoggers loggers = new TezProtoLoggers();
      SystemClock clock = SystemClock.getInstance();
      if (!loggers.setup(hadoopConfiguration, clock)) {
        throw new RuntimeException("Failed to create tez events pipeline, loggers setup failed");
      }
      tezEventsPipeline = new EventProcessorPipeline<>(clock, loggers.getDagEventsLogger(),
          tezEventProcessor, txnManager, fsPersistenceManager, FileStatusType.TEZ,
          eventProcessingConfig, metricRegistry);
      tezEventsPipeline.start();

      tezAppEventsPipeline = new EventProcessorPipeline<>(clock, loggers.getAppEventsLogger(),
          tezEventProcessor, txnManager, fsPersistenceManager, FileStatusType.TEZ_APP,
          eventProcessingConfig, metricRegistry);
      tezAppEventsPipeline.start();

      log.info("Started tez events pipeline");
    } catch (IOException e) {
      log.error("Failed to start tez events pipeline");
      throw new RuntimeException("Failed to create tez events pipeline, got exception:", e);
    }
  }

  private void startHivePipeline() {
    log.info("Starting hive events pipeline");
    try {
      log.info("Creating hive events pipeline");
      // TODO: This should read from hive-site.xml, and logger should be created in hive codebase.
      String hiveBaseDir = eventProcessingConfig.getString(
          ConfVars.HIVE_PROTO_EVENTS_BASE_PATH.varname, null);
      if (hiveBaseDir == null) {
        throw new RuntimeException("Failed to create hive events pipeline, invalid hive config. " +
            "Please set: " + ConfVars.HIVE_PROTO_EVENTS_BASE_PATH.varname);
      }
      log.info("Hive base dir: " + hiveBaseDir);

      SystemClock clock = SystemClock.getInstance();
      DatePartitionedLogger<HiveHookEventProto> logger = new DatePartitionedLogger<>(
          HiveHookEventProto.PARSER, new Path(hiveBaseDir), hadoopConfiguration, clock);
      hiveEventsPipeline = new EventProcessorPipeline<>(clock, logger, hiveEventProcessor, txnManager,
          fsPersistenceManager, FileStatusType.HIVE, eventProcessingConfig, metricRegistry);
      hiveEventsPipeline.start();

      log.info("Started hive events pipeline");
    } catch (IOException e) {
      log.error("Failed to start hive events pipeline");
      throw new RuntimeException("Failed to create hive events pipeline, got exception: ", e);
    }
  }
}
