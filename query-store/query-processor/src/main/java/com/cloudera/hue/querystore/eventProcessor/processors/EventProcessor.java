// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors;

import org.apache.hadoop.fs.Path;

/**
 * Interface to be implemented by all processors
 * @param <T> The type of the event that the processor will process
 */
public interface EventProcessor<T> {
  ProcessingStatus process(T event, Path filePath);
}
