// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.lifecycle;

import java.io.IOException;

import javax.inject.Inject;
import javax.inject.Singleton;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.yarn.util.SystemClock;

import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.entities.FileStatusEntity.FileStatusType;
import com.cloudera.hue.querystore.common.repository.FileStatusPersistenceManager;
import com.cloudera.hue.querystore.common.repository.transaction.TransactionManager;
import com.cloudera.hue.querystore.eventProcessor.pipeline.EventProcessorPipeline;
import com.cloudera.hue.querystore.eventProcessor.processors.ImpalaEventProcessorDispatcher;
import com.cloudera.hue.querystore.eventProcessor.readers.ImpalaFileReader;
import com.cloudera.ipe.model.impala.ImpalaRuntimeProfileTree;
import com.codahale.metrics.MetricRegistry;

import io.dropwizard.lifecycle.Managed;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
public class ImpalaEventProcessorManager implements Managed {
  private final Configuration hadoopConfiguration;
  private final DasConfiguration eventProcessingConfig;
  private final ImpalaEventProcessorDispatcher impalaEventProcessor;

  private final FileStatusPersistenceManager fsPersistenceManager;
  private final TransactionManager txnManager;
  private final MetricRegistry metricRegistry;

  private static final String CONF_PROFILE_LOG_DIR = "impala.history.profile_log_dir";

  private EventProcessorPipeline<ImpalaRuntimeProfileTree> impalaEventsPipeline;

  @Inject
  public ImpalaEventProcessorManager(DasConfiguration eventProcessingConfig,
                               Configuration hadoopConfiguration,
                               ImpalaEventProcessorDispatcher impalaEventProcessor,
                               FileStatusPersistenceManager fsPersistenceManager,
                               TransactionManager txnManager,
                               MetricRegistry metricRegistry) {
    this.eventProcessingConfig = eventProcessingConfig;
    this.hadoopConfiguration = hadoopConfiguration;

    this.impalaEventProcessor = impalaEventProcessor;

    this.fsPersistenceManager = fsPersistenceManager;
    this.txnManager = txnManager;
    this.metricRegistry = metricRegistry;
  }

  @Override
  public void start() {
    log.info("Starting");
    startImpalaPipeline();
    log.info("Started");
  }

  @Override
  public void stop() {
    log.info("ImpalaEventProcessorManager: stopping");
    impalaEventsPipeline.shutdown();
    impalaEventsPipeline.awaitTermination();
    log.info("ImpalaEventProcessorManager: stopped");
  }

  public void forceRefresh() {
    log.info("ImpalaEventProcessorManager: forceRefresh");
    impalaEventsPipeline.forceRefresh();
  }

  public long getQueryRefreshTime() {
    return impalaEventsPipeline.getRefreshTime();
  }

  private void startImpalaPipeline() {
    log.info("Starting Impala events pipeline");
    try {
      log.info("Creating Impala events pipeline");
      // TODO: This should read from impala configs.
      String impalaBaseDir = eventProcessingConfig.getString(CONF_PROFILE_LOG_DIR, null);
      if (impalaBaseDir == null) {
        throw new RuntimeException("Failed to create Impala events pipeline, invalid Impala config. " +
            "Please set: " + CONF_PROFILE_LOG_DIR);
      }
      log.info("Impala base dir: " + impalaBaseDir);

      SystemClock clock = SystemClock.getInstance();
      ImpalaFileReader impalaFileReader = new ImpalaFileReader(new Path(impalaBaseDir), hadoopConfiguration, clock);
      impalaEventsPipeline = new EventProcessorPipeline<ImpalaRuntimeProfileTree>(clock, impalaFileReader, impalaEventProcessor, txnManager,
          fsPersistenceManager, FileStatusType.IMPALA, eventProcessingConfig, metricRegistry);
      impalaEventsPipeline.start();

      log.info("Started Impala events pipeline");
    } catch (IOException e) {
      log.error("Failed to start Impala events pipeline");
      throw new RuntimeException("Failed to create Impala events pipeline, got exception: ", e);
    }
  }
}
