// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.lifecycle;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.yarn.util.Clock;
import org.quartz.CronScheduleBuilder;
import org.quartz.CronTrigger;
import org.quartz.Job;
import org.quartz.JobBuilder;
import org.quartz.JobExecutionContext;
import org.quartz.JobExecutionException;
import org.quartz.Scheduler;
import org.quartz.TriggerBuilder;

import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.config.DasConfiguration.ConfVar;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezAppInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.VertexInfoRepository;
import com.cloudera.hue.querystore.common.repository.transaction.TransactionManager;

import io.dropwizard.lifecycle.Managed;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class CleanupManager implements Managed {
  // Needs a quartz scheduler cron expression
  public static final ConfVar<String> CRON_CONFIG =
      new ConfVar<>("hue.query-processor.event-pipeline.cleanup.cron.expression", "0 0 2 * * ?"); // 30 days

  public static final ConfVar<Long> CLEANUP_INTERVAL_SECS =
      new ConfVar<>("hue.query-processor.event-pipeline.cleanup-interval-secs", 30 * 24 * 3600L); // 30 days

  private final DasConfiguration config;
  private final TransactionManager txnManager;

  private final Provider<HiveQueryBasicInfoRepository> hiveQueryBasicInfoRepository;
  private final Provider<HiveQueryExtendedInfoRepository> hiveQueryExtendedInfoRepository;
  private final Provider<TezDagBasicInfoRepository> tezDagBasicInfoRepository;
  private final Provider<TezDagExtendedInfoRepository> tezDagExtendedInfoRepository;
  private final Provider<VertexInfoRepository> vertexInfoRepoProvider;
  private final Provider<TezAppInfoRepository> tezAppInfoRepository;

  private Scheduler scheduler;

  @Inject
  public CleanupManager(DasConfiguration config,
      TransactionManager txnManager,
      Provider<HiveQueryBasicInfoRepository> hiveQueryBasicInfoRepository,
      Provider<HiveQueryExtendedInfoRepository> hiveQueryExtendedInfoRepository,
      Provider<TezDagBasicInfoRepository> tezDagBasicInfoRepository,
      Provider<TezDagExtendedInfoRepository> tezDagExtendedInfoRepository,
      Provider<VertexInfoRepository> vertexInfoRepoProvider,
      Provider<TezAppInfoRepository> tezAppInfoRepository) {

    this.config = config;
    this.txnManager = txnManager;

    this.hiveQueryBasicInfoRepository = hiveQueryBasicInfoRepository;
    this.hiveQueryExtendedInfoRepository = hiveQueryExtendedInfoRepository;
    this.tezDagBasicInfoRepository = tezDagBasicInfoRepository;
    this.tezDagExtendedInfoRepository = tezDagExtendedInfoRepository;
    this.vertexInfoRepoProvider = vertexInfoRepoProvider;
    this.tezAppInfoRepository = tezAppInfoRepository;
  }

  private class CleanupJob implements Job {
    @Override
    public void execute(JobExecutionContext context) throws JobExecutionException {
      long queryInfoDelTime = System.currentTimeMillis() / 1000 - config.getConf(CLEANUP_INTERVAL_SECS);
      txnManager.withTransaction(() -> {
        log.info("Query info clean for records older than: {}", queryInfoDelTime);
        vertexInfoRepoProvider.get().deleteOlder(queryInfoDelTime);
        tezDagExtendedInfoRepository.get().deleteOlder(queryInfoDelTime);
        tezDagBasicInfoRepository.get().deleteOlder(queryInfoDelTime);
        hiveQueryExtendedInfoRepository.get().deleteOlder(queryInfoDelTime);
        hiveQueryBasicInfoRepository.get().deleteOlder(queryInfoDelTime);
        tezAppInfoRepository.get().deleteOlder(queryInfoDelTime);

        return true;
      });
    }
  }

  @Override
  public void start() throws Exception {
    log.info("Starting cleanup service.");
    this.scheduler = new org.quartz.impl.StdSchedulerFactory().getScheduler();
    scheduler.setJobFactory((bundle, scheduler) -> new CleanupJob());
    CronTrigger trigger = TriggerBuilder.newTrigger()
        .withSchedule(CronScheduleBuilder.cronSchedule(config.getConf(CRON_CONFIG)))
        .build();
    scheduler.scheduleJob(JobBuilder.newJob(CleanupJob.class).build(), trigger);
    scheduler.start();
    log.info("Cleanup service started.");
  }

  @Override
  public void stop() throws Exception {
    log.info("Stopping cleanup service");
    if (scheduler != null) {
      log.info("Shutting down cleanup service scheduler");
      scheduler.shutdown(true);
    }
    log.info("Cleanup service stopped");
  }

  // Used in event processor pipeline to ignore all files before this time.
  public static LocalDate getMinDateForProcessing(Clock clock, DasConfiguration config) {
    long time = clock.getTime() / 1000 - config.getConf(CLEANUP_INTERVAL_SECS);
    return LocalDateTime.ofEpochSecond(time, 0, ZoneOffset.UTC).toLocalDate();
  }
}
