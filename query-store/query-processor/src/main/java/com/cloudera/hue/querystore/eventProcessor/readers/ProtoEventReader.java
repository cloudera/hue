package com.cloudera.hue.querystore.eventProcessor.readers;

import java.io.EOFException;
import java.io.IOException;

import org.apache.hadoop.fs.Path;
import org.apache.tez.dag.history.logging.proto.DatePartitionedLogger;
import org.apache.tez.dag.history.logging.proto.ProtoMessageReader;

import com.cloudera.hue.querystore.eventProcessor.pipeline.FileProcessingStatus;
import com.google.protobuf.MessageLite;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ProtoEventReader<T extends MessageLite> implements EventReader<T> {
  private final ProtoMessageReader<T> protoMessageReader;
  private final FileProcessingStatus fileStatus;
  private final DatePartitionedLogger<T> partitionedLogger;

  public ProtoEventReader(ProtoMessageReader<T> protoMessageReader, FileProcessingStatus fileStatus,
      DatePartitionedLogger<T> partitionedLogger) {
    this.protoMessageReader = protoMessageReader;
    this.fileStatus = fileStatus;
    this.partitionedLogger = partitionedLogger;
  }

  public long getOffset() throws IOException {
    return protoMessageReader.getOffset();
  }

  public void setOffset(long offset) throws IOException {
    protoMessageReader.setOffset(offset);
  }

  public Path getFilePath() {
    return protoMessageReader.getFilePath();
  }

  public Long getLastOffset() {
    //TODO: Implement
    return 0l;
  }

  public T read() throws IOException {
    T evt = null;
    try {
      evt  = protoMessageReader.readEvent();
      if (evt == null) {
        long fsPos = fileStatus.getPosition();
        long readerOffset = protoMessageReader.getOffset();
        if (readerOffset == fsPos + 20 + 4) {
          // Handle multiple consecutive sync markers.
          log.warn("Got multi sync marker for file: {}, at location: {}", protoMessageReader.getFilePath(), fsPos);
          protoMessageReader.setOffset(fsPos + 20);
          return read();
        } else if (fsPos < readerOffset) {
          // Prevent getting stuck at this offset.
          log.warn("Incrementing retry count for file: {}, at filePos: {}, offset: {}",
            protoMessageReader.getFilePath(), fsPos, readerOffset);
          fileStatus.readFailed();
        }
      } else {
        // successful read, reset read retry count.
        fileStatus.readSuccess();
      }
    } catch (EOFException e) {
      // We are getting EOF for an old file, prevent getting stuck here.
      if (fileStatus.getEntity().getDate().isBefore(partitionedLogger.getNow().toLocalDate())) {
        fileStatus.readFailed();
      }
    } catch (Exception e) {
      fileStatus.readFailed();
    }
    return evt;
  }

  @Override
  public void close() throws IOException {
    protoMessageReader.close();
  }
}
