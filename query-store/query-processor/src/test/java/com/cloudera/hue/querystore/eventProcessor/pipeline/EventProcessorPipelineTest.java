// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.pipeline;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.atLeast;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.io.EOFException;
import java.io.IOException;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.yarn.util.Clock;
import org.apache.tez.dag.history.logging.proto.DatePartitionedLogger;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.HistoryEventProto;
import org.apache.tez.dag.history.logging.proto.ProtoMessageReader;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.mockito.internal.verification.VerificationModeFactory;

import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.entities.FileStatusEntity.FileStatusType;
import com.cloudera.hue.querystore.common.repository.FileStatusPersistenceManager;
import com.cloudera.hue.querystore.common.repository.transaction.Callable;
import com.cloudera.hue.querystore.common.repository.transaction.TransactionManager;
import com.cloudera.hue.querystore.eventProcessor.processors.EventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.codahale.metrics.MetricRegistry;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;

import lombok.Data;

public class EventProcessorPipelineTest {
  private RunningTestClock clock;
  private TestLogger logger;
  private EventProcessorPipeline<HistoryEventProto> pipeline;
  private MetricRegistry metricRegistry;
  private TransactionManager txnManager;

  @Mock EventProcessor<HistoryEventProto> processor;
  @Mock FileStatusPersistenceManager fsPersistenceManager;
  @Mock ProtoMessageReader<HistoryEventProto> goodReader;
  @Mock ProtoMessageReader<HistoryEventProto> eofReader;
  @Mock ProtoMessageReader<HistoryEventProto> ioExReader;

  @Before
  public void setup() throws Exception {
    MockitoAnnotations.initMocks(this);
    fileLen.set(1L);

    when(goodReader.readEvent()).thenReturn(HistoryEventProto.getDefaultInstance(),
        (HistoryEventProto)null);
    when(eofReader.readEvent()).thenThrow(new EOFException());
    when(ioExReader.readEvent()).thenThrow(new IOException());
    when(fsPersistenceManager.getFileOfType(FileStatusType.TEZ))
        .thenReturn(Collections.emptyList());
    when(fsPersistenceManager.create(any())).thenAnswer(m -> m.getArgument(0));
    when(processor.process(eq(HistoryEventProto.getDefaultInstance()), any()))
        .thenReturn(ProcessingStatus.SUCCESS);

    clock = new RunningTestClock();
    logger = spy(new TestLogger(clock));
    txnManager = new TransactionManager(null) {
      @Override
      public <T, X extends Exception> T withTransaction(Callable<T, X> callable) throws X {
        return callable.call();
      };
    };

    DasConfiguration config = new DasConfiguration();
    config.setConf(EventProcessorPipeline.FOLDER_SCAN_DELAY_MILLIS, 100L);
    metricRegistry = new MetricRegistry();
    pipeline = new EventProcessorPipeline<>(clock, logger, processor, txnManager,
        fsPersistenceManager, FileStatusType.TEZ, config, metricRegistry);
  }

  @Test
  public void testPipelineDoNothing() throws Exception {
    pipeline.start();
    Thread.sleep(100);
    pipeline.shutdown();
    verify(logger, VerificationModeFactory.atLeastOnce())
        .scanForChangedFiles(eq("date=1969-12-02"), any());
  }

  // We could make this cleaner, by using fileLen per path, just use one file to test len change.
  public final AtomicLong fileLen = new AtomicLong(1l);
  private List<FileStatus> fromPaths(List<Path> paths) {
    List<FileStatus> status = new ArrayList<>();
    for (Path path : paths) {
      status.add(new FileStatus(fileLen.get(), false, 3, 1l, 0L, 0L, null, "user1", "group1", path));
    }
    return status;
  }

  @Test
  public void testPipeline() throws Exception {
    clock.setTime(3 * 24 * 60 * 60 * 1000L);
    logger.setupNextDirs("date=1969-12-05", "date=1970-01-01", "date=1970-01-02", "date=1970-01-03");
    Path goodPath = new Path("/basedir/date=1970-01-01/good");
    Path errorOpenEOFPath = new Path("/basedir/date=1970-01-01/error_open_eof");
    Path errorOpenIOPath = new Path("/basedir/date=1970-01-01/error_open_io");
    Path errorReadEOFPath = new Path("/basedir/date=1970-01-01/error_read_eof");
    Path errorReadIOPath = new Path("/basedir/date=1970-01-01/error_read_io");

    List<Path> errorPaths = Lists.newArrayList(errorOpenEOFPath, errorOpenIOPath, errorReadIOPath,
        errorReadEOFPath);
    logger.setupScanPaths(ImmutableMap.<String, Iterator<List<Path>>>of(
        "date=1970-01-01", Lists.newArrayList(Lists.newArrayList(goodPath, errorOpenEOFPath,
            errorOpenIOPath, errorReadIOPath, errorReadEOFPath), errorPaths, errorPaths, errorPaths,
            errorPaths, errorPaths, errorPaths, errorPaths).iterator()
        ));

    pipeline.start();
    long refreshTime = pipeline.getRefreshTime();

    Thread.sleep(1000);

    Assert.assertTrue("Time not updated", refreshTime < pipeline.getRefreshTime());
    refreshTime = pipeline.getRefreshTime();

    // First directory will be 30 days minus current date.
    verify(logger, times(1)).scanForChangedFiles(eq("date=1969-12-05"), any());
    verify(logger).getNextDirectory(eq("date=1969-12-05"));

    // Invoke twice, because we found a file.
    verify(logger, times(7)).scanForChangedFiles(eq("date=1970-01-01"), any());
    verify(logger).getNextDirectory(eq("date=1970-01-01"));

    // The good file is read 5 times, since we have to refresh files which are not modified too.
    verify(logger, times(6)).getReader(eq(goodPath));
    verify(goodReader, times(7)).readEvent();
    verify(goodReader, times(7)).getOffset();
    verify(processor).process(eq(HistoryEventProto.getDefaultInstance()), any());

    verify(logger, times(6)).getReader(eq(errorOpenEOFPath));
    verify(logger, times(6)).getReader(eq(errorOpenIOPath));

    verify(logger, times(6)).getReader(eq(errorReadIOPath));
    verify(ioExReader, times(6)).readEvent();
    // This is never called since read event will fail.
    verify(ioExReader, times(0)).getOffset();

    verify(logger, times(6)).getReader(eq(errorReadEOFPath));
    verify(eofReader, times(6)).readEvent();
    // This is never called since read event will fail.
    verify(eofReader, times(0)).getOffset();

    // All the five above should be persisted.
    verify(fsPersistenceManager, times(5)).create(any());
    // Position is not updated on open failures, 3 files updated 6 times.
    verify(fsPersistenceManager, times(3 * 6)).update(any());

    // Invoke once because no new files.
    verify(logger).scanForChangedFiles(eq("date=1970-01-02"), any());
    verify(logger).getNextDirectory(eq("date=1970-01-02"));

    // Keep invoke because current day is same.
    verify(logger, VerificationModeFactory.atLeastOnce())
      .scanForChangedFiles(eq("date=1970-01-03"), any());
    verify(logger, times(3)).getNextDirectory(eq("date=1970-01-03"));

    verify(logger, times(0)).scanForChangedFiles(eq("date=1970-01-05"), any());

    // No file should be deleted until now.
    verify(fsPersistenceManager, times(0)).delete(any());

    // Move to next and sleep again.
    // Auto close wait time is 4 days for files which have not finished.
    clock.setTime(7 * 24 * 60 * 60 * 1000L + 1);
    Thread.sleep(1000);

    Assert.assertTrue("Time not updated", refreshTime < pipeline.getRefreshTime());

    // Now date has changed it should advance and also delete the old files.
    verify(logger, VerificationModeFactory.atLeastOnce()).getNextDirectory(eq("date=1970-01-03"));
    verify(fsPersistenceManager, times(5)).delete(any());

    pipeline.shutdown();
  }

  @Test
  public void testForceRefresh() throws Exception {
    DasConfiguration config = new DasConfiguration();
    config.setConf(EventProcessorPipeline.FOLDER_SCAN_DELAY_MILLIS, 5 * 60 * 1000l);

    TestClock clock = new TestClock();
    EventProcessorPipeline<HistoryEventProto> pipeline = new EventProcessorPipeline<>(clock, logger, processor, txnManager,
        fsPersistenceManager, FileStatusType.TEZ, config, metricRegistry);

    clock.setTime(3 * 24 * 60 * 60 * 1000L);

    pipeline.start();
    Thread.sleep(1000);
    long refreshTime = pipeline.getRefreshTime();
    Assert.assertTrue("refreshTime wasn't set", refreshTime == clock.getTime());

    clock.setTime(3 * 24 * 60 * 70 * 1000L);

    pipeline.forceRefresh();
    Thread.sleep(1000);
    Assert.assertTrue("Time not updated", refreshTime < pipeline.getRefreshTime());
    refreshTime = pipeline.getRefreshTime();

    pipeline.forceRefresh();
    Thread.sleep(EventProcessorPipeline.REFRESH_THROTTLE_MILLIS / 2);
    pipeline.forceRefresh();
    Thread.sleep(1000);
    Assert.assertTrue("forceRefresh was not throttled", refreshTime == pipeline.getRefreshTime());

    pipeline.shutdown();
  }

  @Test
  public void testRetryStartingErrorGrowingFile() throws Exception {
    clock.setTime(1800); // 1st day.
    logger.setupNextDirs("date=1969-12-02", "date=1970-01-01", "date=1970-01-04", "date=1970-01-05");
    Path errorOpenEOFPath = new Path("/basedir/date=1970-01-01/error_open_eof");
    List<Path> paths = Collections.singletonList(errorOpenEOFPath);
    logger.setupScanPaths(ImmutableMap.<String, Iterator<List<Path>>>of(
        "date=1970-01-01", Iterables.<List<Path>>cycle(Collections.singleton(paths)).iterator()));
    pipeline.start();
    Thread.sleep(1000);

    verify(logger, times(1)).scanForChangedFiles(eq("date=1969-12-02"), any());
    verify(logger, times(1)).getNextDirectory(eq("date=1969-12-02"));
    // We have errors, so first 5 times will try then it should atleast try once
    verify(logger, atLeast(6)).scanForChangedFiles(eq("date=1970-01-01"), any());
    // First 5 times getNextDirectory will not be invoked and then it will be invoked.
    verify(logger, atLeast(1)).getNextDirectory(eq("date=1970-01-01"));
    // The very first time it reads once and then retry comes in place so its 1 + 5
    verify(logger, times(1 + 5)).getReader(eq(errorOpenEOFPath));

    // Grow the file, it should try five times again.
    reset(logger);
    fileLen.incrementAndGet();
    Thread.sleep(1000);

    // Now it should try the same file 5 more times.
    verify(logger, atLeast(6)).scanForChangedFiles(eq("date=1970-01-01"), any());
    verify(logger, times(5)).getReader(eq(errorOpenEOFPath));

    clock.setTime(4 * 24 * 3600 * 1000l + 3600l);
    Thread.sleep(200);
    verify(fsPersistenceManager, times(1)).delete(any());
    verify(logger, times(0)).scanForChangedFiles(eq("date=1970-01-05"), any());
  }

  class TestLogger extends DatePartitionedLogger<HistoryEventProto> {

    public TestLogger(RunningTestClock clock) throws IOException {
      // This is never invoked, just for compiler to be happy.
      super(HistoryEventProto.PARSER, new Path("/tmp/"), new Configuration(), clock);
    }

    @Override
    public Path getPathForDate(LocalDate date, String fileName) throws IOException {
      return new Path("/basedir/" + getDirForDate(date) + "/" + fileName);
    }

    @Override
    public ProtoMessageReader<HistoryEventProto> getReader(Path filePath) throws IOException {
      String fileName = filePath.getName();
      switch (fileName) {
        case "error_open_eof": throw new EOFException();
        case "error_open_io": throw new IOException();
        case "error_read_io": return ioExReader;
        case "error_read_eof": return eofReader;
      }
      return goodReader;
    }

    private Map<String, Iterator<List<Path>>> dirPaths = Collections.emptyMap();
    private void setupScanPaths(Map<String, Iterator<List<Path>>> dirPaths) {
      this.dirPaths = dirPaths;
    }

    @Override
    public List<FileStatus> scanForChangedFiles(String subDir, Map<String, Long> currentOffsets)
        throws IOException {
      Iterator<List<Path>> pathsList = dirPaths.get(subDir);
      if (pathsList != null && pathsList.hasNext()) {
        return fromPaths(pathsList.next());
      }
      return Collections.emptyList();
    }

    private String[] dirs = new String[0];
    private synchronized void setupNextDirs(String ... dirs) {
      this.dirs = dirs;
    }

    @Override
    public synchronized String getNextDirectory(String currentDir) throws IOException {
      for (int i = 0; i < dirs.length - 1; ++i) {
        if (dirs[i].equals(currentDir)) {
          return dirs[i + 1];
        }
      }
      return null;
    }
  }

  @Data
  static class TestClock implements Clock {
    volatile long time = 0;
  }

  @Data
  static class RunningTestClock implements Clock {
    volatile long time = 0;

    public long getTime() {
      time += EventProcessorPipeline.REFRESH_THROTTLE_MILLIS + 1000;
      return time;
    }
  }
}
