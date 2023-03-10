package com.cloudera.hue.querystore.eventProcessor.readers;

import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.Path;

import com.cloudera.hue.querystore.eventProcessor.pipeline.FileProcessingStatus;

/**
 * Interface to be implemented for each file format
 * @param <T> The type of the event to read
 */
public interface FileReader<T> {
  Configuration getConfig();

  LocalDateTime getNow();

  String getDirForDate(LocalDate date);
  LocalDate getDateFromDir(String dirName) throws IllegalArgumentException;

  Path getPathForDate(LocalDate date, String filePath) throws IOException;

  EventReader<T> getEventReader(Path filePath, FileProcessingStatus fileStatus) throws IOException;

  List<FileStatus> scanForChangedFiles(String subDir, Map<String, Long> currentOffsets) throws IOException;

  String getNextDirectory(String currentDir) throws IOException;
}
