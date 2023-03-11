package com.cloudera.hue.querystore.eventProcessor.readers;

import java.io.Closeable;
import java.io.IOException;

import org.apache.hadoop.fs.Path;

public interface EventReader<T> extends Closeable {

  long getOffset() throws IOException;
  void setOffset(long offset) throws IOException;

  Long getLastOffset();

  Path getFilePath();

  T read() throws IOException;

}
