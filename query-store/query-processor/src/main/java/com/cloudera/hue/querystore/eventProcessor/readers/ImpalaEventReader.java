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
  private final ImpalaFileReader fileReader;
  private final Path filePath;
  private final FileProcessingStatus fileStatus;
  private final FSDataInputStream stream;
  private final BufferedReader reader;
  // private final LineNumberReader r;

  public ImpalaEventReader(ImpalaFileReader fileReader, Path filePath, FileProcessingStatus fileStatus) throws IOException {
    this.filePath = filePath;
    this.fileStatus = fileStatus;
    this.fileReader = fileReader;

    FileSystem fs = FileSystem.get(fileReader.getConfig());
    this.stream = fs.open(filePath);
    this.reader = new BufferedReader(new InputStreamReader(stream));
  }

  public long getOffset() throws IOException {
    return stream.getPos();
  }

  public void setOffset(long offset) throws IOException {
    stream.seek(offset);
  }

  public Path getFilePath() {
    return filePath;
  }

  public ImpalaRuntimeProfileTree read() throws IOException {
    try {
      String line =  reader.readLine();

      if (line == null) {
        fileStatus.readFailed(); // TODO: Validate this check
        return null;
      }

      String[] parts = line.split(" ");
      if (parts.length != 3) {
        log.error("Unexpected Impala profile format in file {}", filePath);
        fileStatus.readFailed();
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
    stream.close();
    reader.close();
  }
}
