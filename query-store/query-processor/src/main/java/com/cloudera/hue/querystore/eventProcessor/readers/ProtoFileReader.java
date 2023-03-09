package com.cloudera.hue.querystore.eventProcessor.readers;

import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.tez.dag.history.logging.proto.DatePartitionedLogger;

import com.cloudera.hue.querystore.eventProcessor.pipeline.FileProcessingStatus;
import com.google.protobuf.MessageLite;

public class ProtoFileReader<T extends MessageLite> implements FileReader<T> {
  private final DatePartitionedLogger<T> partitionedLogger;

  public ProtoFileReader(DatePartitionedLogger<T> partitionedLogger) {
    this.partitionedLogger = partitionedLogger;
  }

  public Configuration getConfig() {
    return partitionedLogger.getConfig();
  }

  public LocalDateTime getNow() {
    return partitionedLogger.getNow();
  }

  public String getDirForDate(LocalDate date) {
    return partitionedLogger.getDirForDate(date);
  }

  public LocalDate getDateFromDir(String dirName) throws IllegalArgumentException {
    return partitionedLogger.getDateFromDir(dirName);
  }

  public EventReader<T> getEventReader(Path filePath, FileProcessingStatus fileStatus) throws IOException {
    return new ProtoEventReader<>(partitionedLogger.getReader(filePath), fileStatus, partitionedLogger);
  }

  public Path getAbsoluteScanPath(String dateDir) {
    return partitionedLogger.getPathForSubdir(dateDir, ".");
  }

  public Path getPathForDate(LocalDate date, String filePath) throws IOException {
    return partitionedLogger.getPathForDate(date, filePath);
  }

  public List<FileStatus> scanForChangedFiles(String subDir, Map<String, Long> currentOffsets) throws IOException {
    return partitionedLogger.scanForChangedFiles(subDir, currentOffsets);
  }

  public String getNextDirectory(String currentDir) throws IOException {
    return partitionedLogger.getNextDirectory(currentDir);
  }
}
