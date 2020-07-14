// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

import java.io.IOException;
import java.util.Iterator;

import javax.inject.Inject;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.yarn.util.SystemClock;
import org.apache.tez.dag.history.logging.proto.DatePartitionedLogger;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.HistoryEventProto;
import org.apache.tez.dag.history.logging.proto.ProtoMessageReader;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class HistoryEventReader {

  DatePartitionedLogger<HistoryEventProto> partitionedLogger;

  @Inject
  public HistoryEventReader(Configuration configuration) {
    initLogger(configuration);
  }

  private void initLogger(Configuration configuration) {
    try {
      SystemClock clock = SystemClock.getInstance();

      partitionedLogger = new DatePartitionedLogger<>(
        HistoryEventProto.PARSER, new org.apache.hadoop.fs.Path("/"),
        configuration, clock);
      // As we don't do any writes to HDFS it's fine to pass the base path.
    } catch(IOException e) {
      log.error("Failed to start init logger {}:", e);
    }
  }

  public HistoryEventIterator getIterator(Path sourceFile) throws IOException {
    return new HistoryEventIterator(sourceFile);
  }

  public class HistoryEventIterator implements Iterator<HistoryEventProto>, AutoCloseable {

    private ProtoMessageReader<HistoryLoggerProtos.HistoryEventProto> reader;
    private HistoryEventProto historyEventProtoObj;

    public HistoryEventIterator(Path sourceFile) throws IOException {
      this.reader = partitionedLogger.getReader(sourceFile);
      this.historyEventProtoObj = readEvent();
    }

    private HistoryEventProto readEvent() {
      HistoryEventProto event = null;
      try {
        event = reader.readEvent();
      } catch (IOException e) {
        // Nothing to do, ignore this, event will be null.
      }
      return event;
    }

    @Override
    public boolean hasNext() {
      return historyEventProtoObj != null;
    }

    @Override
    public HistoryEventProto next() {
      HistoryEventProto next = historyEventProtoObj;
      historyEventProtoObj = readEvent();
      return next;
    }

    @Override
    public void remove() {
      throw new UnsupportedOperationException();
    }

    public void close() throws IOException {
      reader.close();
    }
  }
}
