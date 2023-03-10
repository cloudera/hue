package com.cloudera.hue.querystore.eventProcessor.readers;

import java.io.BufferedReader;
import java.io.EOFException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.zip.GZIPInputStream;

import org.apache.commons.codec.binary.Base64;
import org.apache.commons.lang3.StringUtils;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.joda.time.Instant;

import com.cloudera.hue.querystore.eventProcessor.pipeline.FileProcessingStatus;
import com.cloudera.ipe.model.impala.ImpalaRuntimeProfileTree;
import com.cloudera.ipe.rules.ImpalaRuntimeProfile;
import com.cloudera.ipe.util.ImpalaRuntimeProfileUtils;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ImpalaEventReader implements EventReader<ImpalaRuntimeProfileTree> {
  private final Path filePath;
  private final InputStream stream;
  private final ImpalaFileReader fileReader;
  private final FileProcessingStatus fileStatus;

  // In CDW there is a cases where a line might be split into 16k chunks
  private static final int MARK_LIMIT = 20 * 1024; // 20 Kb

  private BufferedReader reader;
  private long offset = 0;

  public ImpalaEventReader(ImpalaFileReader fileReader, Path filePath,
      FileProcessingStatus fileStatus) throws IOException {
    this.filePath = filePath;
    this.fileStatus = fileStatus;
    this.fileReader = fileReader;

    FileSystem fs = filePath.getFileSystem(fileReader.getConfig());

    // TODO: For non gz, we could improive performance using FSDataInputStream & stream.seek(offset)
    // TODO: Could move CDW specific items to ImpalaCDWEventReader
    InputStream stream = fs.open(filePath);
    if(filePath.toString().toLowerCase().endsWith(".gz")) {
      stream = new GZIPInputStream(stream);
    }

    this.stream = stream;
    this.reader = new BufferedReader(new InputStreamReader(stream));
  }

  public long getOffset() throws IOException {
    return offset;
  }

  public void setOffset(long offset) throws IOException {
    this.offset = offset;

    stream.skip(offset);

    // reader.close() is costly.
    // Just abandon the BufferedReader and create new, next GC will pick and clean it up.
    reader = new BufferedReader(new InputStreamReader(stream));
  }

  public Path getFilePath() {
    return filePath;
  }

  private String readLine() throws IOException {
    String line = reader.readLine();
    if(line != null) {
      // Advance offset. +1 for the new line character
      offset += line.length() + 1;
    }
    return line;
  }

  private String getNextLine() throws IOException {
    reader.mark(MARK_LIMIT);
    String line = reader.readLine();
    reader.reset();
    return line;
  }

  public ImpalaRuntimeProfileTree read() throws IOException {
    try {
      String line = readLine();

      // TODO: Improve the following three blocks - while, if & if while

      while (line != null && StringUtils.countMatches(line, " ") != 2) {
        // Skip invalid lines if any. fluentd in CDW adds 3 lines at the begining.
        line = readLine();
      }

      if (line == null) {
        // End of file - Mark failed to revisit
        fileStatus.readFailed();
        return null;
      }

      if (StringUtils.countMatches(line, " ") == 2) {
        // In CDW there could be cases where a line might be split into 16k chunks
        String nextLine = getNextLine();
        while(nextLine != null && nextLine.length() > 0 && StringUtils.countMatches(nextLine, " ") == 0) {
          line += readLine();
          nextLine = getNextLine();
        }
      }

      String[] parts = line.split(" ");
      byte[] payload = Base64.decodeBase64(parts[2]);
      ImpalaRuntimeProfile p = new ImpalaRuntimeProfile(payload,
      "", "",
      new Instant(), new Instant(),
      ImpalaRuntimeProfile.DEFAULT_TIME_FORMATS, ImpalaRuntimeProfileTree.MILLISECOND_TIME_FORMATTER);

      fileStatus.readSuccess();
      log.info("Impala profile read successful for query {}", parts[1]);

      return ImpalaRuntimeProfileUtils.convertThriftProfileToTree(p.generateThriftProfile());
    } catch (EOFException e) {
      // We are getting EOF for an old file, prevent getting stuck here.
      if (fileStatus.getEntity().getDate().isBefore(fileReader.getNow().toLocalDate())) {
        fileStatus.readFailed();
      }
      log.error("Impala profile read failed", e);
    } catch (Exception e) {
      fileStatus.readFailed();
      log.error("Impala profile read failed", e);
    }
    return null;
  }

  public void close() throws IOException {
    reader.close(); // Closes the stream too
  }
}
