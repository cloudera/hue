// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.dispatchers;

import org.apache.hadoop.fs.Path;

import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;

/**
 * Interface to be implemented by all dispatchers.
 * Each dispatcher will accept an event and based on the event type, calls the respective processor to process the event.
 * It also returns a ProcessingStatus. If status is FINISH, the file is not tracked anymore. File is tracked for SUCCESS & SKIP.
 * @param <T> The type of the event that the processor will process
 */
public interface EventDispatcher<T> {
  ProcessingStatus process(T event, Path filePath, Long eventOffset);
}
