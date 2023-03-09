// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.pipeline;

import java.io.EOFException;
import java.io.IOException;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;

import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;

import com.cloudera.hue.querystore.common.entities.FileStatusEntity;
import com.cloudera.hue.querystore.common.repository.FileStatusPersistenceManager;
import com.cloudera.hue.querystore.common.repository.transaction.TransactionManager;
import com.cloudera.hue.querystore.eventProcessor.readers.EventReader;
import com.cloudera.hue.querystore.eventProcessor.readers.FileReader;

import lombok.ToString;
import lombok.extern.slf4j.Slf4j;

// This is a shared object b/w the directory refresh thread and read+process thread.
// make sure all accesses are thread safe.
@Slf4j
@ToString
public class FileProcessingStatus {
  // The persisted entity.
  private final FileStatusEntity entity;

  // This is true if the file is in the queue or being processed.
  private final AtomicBoolean scheduled = new AtomicBoolean();

  // This record read failures at a given position in the file, if there are too many failures
  // current strategy is to stop processing this file.
  private final AtomicInteger readRetryCount = new AtomicInteger();

  // The retry count for a processing a record, if we have too many failures for one record then we
  // ignore the record and move forward.
  private final AtomicInteger processRetryCount = new AtomicInteger();

  // The last seen file size, if this changes read retry count is reset, to give the file another
  // chance.
  private long lastListSize = 0;

  public FileProcessingStatus(FileStatusEntity entity) {
    this.entity = entity;
  }

  // Use this only for logging, any other access should be done using this class for thread safety.
  public FileStatusEntity getEntity() {
    return entity;
  }

  public synchronized boolean schedule() {
    return !isFinished() && scheduled.compareAndSet(false, true);
  }

  public synchronized boolean doneRunning() {
    return scheduled.compareAndSet(true, false);
  }

  public synchronized boolean isFinished() {
    return entity.isFinished() || readErrorExceeded();
  }

  public synchronized boolean isFinished(long newLen) {
    if (newLen > lastListSize) {
      lastListSize = newLen;
      readRetryCount.set(0);
    }
    return entity.isFinished() || readErrorExceeded();
  }

  public synchronized long getPosition() {
    return entity.getPosition();
  }

  public synchronized void updateEntity(boolean isFinished, long position, long now) {
    entity.setFinished(isFinished);
    entity.setPosition(position);
    entity.setLastEventTime(now);
  }

  private static final int MAX_RETRY_COUNT = 5;
  public synchronized boolean readErrorExceeded() {
    return readRetryCount.get() >= MAX_RETRY_COUNT;
  }

  public void readFailed() {
    readRetryCount.incrementAndGet();
  }

  public void readSuccess() {
    readRetryCount.set(0);
  }

  public void processingFailed(Exception e) throws Exception {
    log.error("Got error processing event for file: {}", entity.getFilePath());
    if (processRetryCount.incrementAndGet() < MAX_RETRY_COUNT) {
      throw e;
    }
    log.error("Ignoring event for fileName: {} at pos: {}", entity.getFilePath(),
        entity.getPosition());
  }

  public void processingSuccess() {
    processRetryCount.set(0);
  }

  public synchronized boolean removeIfOlder(TransactionManager txnManager,
      FileStatusPersistenceManager fsPersistenceManager, long minTime) {
    if (!scheduled.get() && (entity.isFinished() || entity.getLastEventTime() < minTime)) {
      log.info("Removing file {}, with date {}", entity.getFilePath(), entity.getDate());
      // Remove finished or expired entities.
      txnManager.withTransaction(() -> fsPersistenceManager.delete(entity));
      return true;
    }
    return false;
  }

  public synchronized boolean shouldRefreshOld(FileReader<?> fileReader) {
    if (scheduled.get()) {
      return false;
    }
    try {
      Path path = fileReader.getPathForDate(entity.getDate(), entity.getFilePath());
      FileStatus status = path.getFileSystem(fileReader.getConfig()).getFileStatus(path);
      return entity.getPosition() < status.getLen();
    } catch (IOException e) {
      log.warn("IOException while trying to refresh: " + entity.getFilePath());
    }
    return false;
  }

  public synchronized <T> EventReader<T> getEventReader(FileReader<T> fileReader) {
    try {
      Path filePath = fileReader.getPathForDate(entity.getDate(), entity.getFilePath());
      EventReader<T> reader = fileReader.getEventReader(filePath, this);
      Long offset = entity.getPosition();
      if (offset != null && offset > 0) {
        reader.setOffset(offset);
      }
      return reader;
    } catch (IOException e) {
      this.readFailed();
      if (e instanceof EOFException && this.lastListSize == 0) {
        log.warn("Got EOFException trying to create reader for: {}, ignoring.", this);
      } else {
        log.error("Error trying to create reader for: {}", this, e);
      }
      return null;
    }
  }

  public void updatePosition(FileStatusPersistenceManager fsPersistenceManager) {
    log.debug("Updating file status in database: {}", this);
    fsPersistenceManager.update(entity);
  }

  public int getProcessRetryCount() {
    return processRetryCount.get();
  }
}
