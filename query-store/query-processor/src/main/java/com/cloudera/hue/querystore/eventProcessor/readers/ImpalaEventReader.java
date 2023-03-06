package com.cloudera.hue.querystore.eventProcessor.readers;

import java.io.BufferedReader;
import java.io.EOFException;
import java.io.IOException;
import java.io.InputStreamReader;

import org.apache.commons.codec.binary.Base64;
import org.apache.hadoop.fs.FSDataInputStream;
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
  private final FSDataInputStream stream;
  private final ImpalaFileReader fileReader;
  private final FileProcessingStatus fileStatus;

  private BufferedReader reader;
  private long offset = 0;

  public ImpalaEventReader(ImpalaFileReader fileReader, Path filePath,
      FileProcessingStatus fileStatus) throws IOException {
    this.filePath = filePath;
    this.fileStatus = fileStatus;
    this.fileReader = fileReader;

    FileSystem fs = FileSystem.get(fileReader.getConfig());
    this.stream = fs.open(filePath);

    this.reader = new BufferedReader(new InputStreamReader(stream));
  }

  public long getOffset() throws IOException {
    return offset;
  }

  public void setOffset(long offset) throws IOException {
    this.offset = offset;

    stream.seek(offset);

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

  public ImpalaRuntimeProfileTree read() throws IOException {
    try {
      String line = readLine();

      while ("".equals(line)) {
        // Skip empty lines if any
        line =  readLine();
      }

      if (line == null) {
        // End of file - Mark failed to revisit
        fileStatus.readFailed();
        return null;
      }

      String[] parts = line.split(" ");
      if (parts.length != 3) {
        throw new Error("Unexpected Impala profile format in file " + filePath);
      }

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
