package com.cloudera.hue.querystore.eventProcessor.readers;

import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileStatus;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.LocatedFileStatus;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.RemoteIterator;
import org.apache.hadoop.fs.permission.FsPermission;
import org.apache.hadoop.yarn.util.Clock;

import com.cloudera.hue.querystore.eventProcessor.pipeline.FileProcessingStatus;

import com.cloudera.ipe.model.impala.ImpalaRuntimeProfileTree;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ImpalaFileReader implements FileReader<ImpalaRuntimeProfileTree> {
  private final Path basePath;
  private final Configuration conf;
  private final Clock clock;

  private static String DATE_KEY = "dt=";

  // Everyone has permission to write, but with sticky set so that delete is restricted.
  private static final FsPermission DIR_PERMISSION = FsPermission.createImmutable((short)01777);

  public ImpalaFileReader(Path baseDir, Configuration conf, Clock clock) throws IOException {
    this.conf = new Configuration(conf);
    this.clock = clock;

    createDirIfNotExists(baseDir);
    this.basePath = baseDir.getFileSystem(conf).resolvePath(baseDir);
  }

  private void createDirIfNotExists(Path path) throws IOException {
    FileSystem fileSystem = path.getFileSystem(conf);
    try {
      if (!fileSystem.exists(path)) {
        fileSystem.mkdirs(path);
        fileSystem.setPermission(path, DIR_PERMISSION);
      }
    } catch (IOException e) {
      // Ignore this exception, if there is a problem it'll fail when trying to read or write.
      log.warn("Error while trying to set permission: ", e);
    }
  }

  public Configuration getConfig() {
    return conf;
  }

  public LocalDateTime getNow() {
    return LocalDateTime.ofEpochSecond(clock.getTime() / 1000, 0, ZoneOffset.UTC);
  }

  /**
   * Returns the directory name for a given date.
   */
  public String getDirForDate(LocalDate date) {
    return DATE_KEY + DateTimeFormatter.ISO_LOCAL_DATE.format(date);
  }

  /**
   * Extract the date from the directory name, this should be a directory created by this class.
   */
  public LocalDate getDateFromDir(String dirName) throws IllegalArgumentException {
    if (!dirName.startsWith(DATE_KEY)) {
      throw new IllegalArgumentException("Invalid directory: "+ dirName);
    }
    return LocalDate.parse(dirName.substring(DATE_KEY.length()), DateTimeFormatter.ISO_LOCAL_DATE);
  }

  /**
   * Create a path for the given date and fileName. This can be used to create a reader.
   */
  public Path getPathForDate(LocalDate date, String fileName) throws IOException {
    Path path = new Path(basePath, getDirForDate(date));
    return new Path(path, fileName);
  }

  /**
   * Returns new or changed files in the given directory. The offsets are used to find
   * changed files.
   */
  public List<FileStatus> scanForChangedFiles(String subDir, Map<String, Long> currentOffsets) throws IOException {
    Path dirPath = new Path(basePath, subDir);
    FileSystem fileSystem = basePath.getFileSystem(conf);
    List<FileStatus> newFiles = new ArrayList<>();
    if (!fileSystem.exists(dirPath)) {
      return newFiles;
    }

    int filesScanned = 0;

    RemoteIterator<LocatedFileStatus> fileStatusListIterator = fileSystem.listFiles(dirPath, true);
    while(fileStatusListIterator.hasNext()){
      filesScanned++;

      LocatedFileStatus status = fileStatusListIterator.next();

      String filePath = status.getPath().toString();

      //TODO: Temporary, remove once cron job is removed for POC
      if(filePath.endsWith("_COPYING_")) {
        continue;
      }

      // TODO: Optimize this part. we shouldnt recursively scan the complete sub dirs.
      // Can do that under dt=<date_stamp>/ns=<impala_ID>/app=impala-profiles, but not under /dt=<date_stamp>
      // Get list of ns directories under, append app=impala-profiles. And if present then do a recursive scan
      if(filePath.contains("app=impala-profiles")) { // Only for CDW
        Long offset = currentOffsets.get(filePath);

        // If the offset was never added or offset < fileSize.
        if (offset == null || offset < status.getLen()) {
          newFiles.add(status);
        }
      }
    }

    log.info("Scanned {} files for Impala query profile", filesScanned);

    return newFiles;
  }

  /**
   * Find next available directory, after the given directory.
   */
  public String getNextDirectory(String currentDir) throws IOException {
    // Fast check, if the next day directory exists return it.
    String nextDate = getDirForDate(getDateFromDir(currentDir).plusDays(1));
    FileSystem fileSystem = basePath.getFileSystem(conf);
    if (fileSystem.exists(new Path(basePath, nextDate))) {
      return nextDate;
    }
    // Have to scan the directory to find min date greater than currentDir.
    String dirName = null;
    for (FileStatus status : fileSystem.listStatus(basePath)) {
      String name = status.getPath().getName();
      // String comparison is good enough, since its of form date=yyyy-MM-dd
      if (name.compareTo(currentDir) > 0 && (dirName == null || name.compareTo(dirName) < 0)) {
        dirName = name;
      }
    }
    return dirName;
  }

  public EventReader<ImpalaRuntimeProfileTree> getEventReader(Path filePath, FileProcessingStatus fileStatus) throws IOException {
    return new ImpalaEventReader(this, filePath, fileStatus);
  }

  public EventReader<ImpalaRuntimeProfileTree> getEventReader(Path filePath) throws IOException {
    return getEventReader(filePath, new FileProcessingStatus(null));
  }
}
