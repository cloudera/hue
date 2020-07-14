// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

import java.io.BufferedOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import org.apache.commons.io.IOUtils;
import org.apache.commons.io.output.ProxyOutputStream;

/**
 * Class to stream a zip file.
 */
public class ZipStream implements AutoCloseable {

  private final ZipOutputStream zipOutputStream;

  private final Set<String> directories;

  public ZipStream(OutputStream outputStream) {
    this.zipOutputStream = new ZipOutputStream(new BufferedOutputStream(outputStream));
    this.directories = new HashSet<String>();
  }

  private void streamDirectories(Path directoryPath) throws IOException {
    if(directoryPath != null) {
      String artifactParentStr = directoryPath.toString();
      if(!directories.contains(artifactParentStr)) {
        directories.add(artifactParentStr);
        zipOutputStream.putNextEntry(new ZipEntry(artifactParentStr + "/"));
      }
    }
  }

  private void createFileEntity(String filePath) throws IOException  {
    zipOutputStream.closeEntry();
    streamDirectories(Paths.get(filePath).getParent());
    zipOutputStream.putNextEntry(new ZipEntry(filePath));
  }

  private void closeFileEntity() throws IOException  {
    zipOutputStream.closeEntry();
  }

  public OutputStream openFile(String filePath) throws IOException {
    createFileEntity(filePath);

    return new ProxyOutputStream(zipOutputStream) {
      @Override
      public void close() throws IOException {
        closeFileEntity();
      }
    };
  }

  public void writeFile(String filePath, byte b[]) throws IOException {
    createFileEntity(filePath);
    zipOutputStream.write(b);
    closeFileEntity();
  }

  public void writeFile(String filePath, InputStream inputStream) throws IOException {
    createFileEntity(filePath);
    IOUtils.copyLarge(inputStream, zipOutputStream);
    inputStream.close();
    closeFileEntity();
  }

  @Override
  public void close() throws IOException {
    closeFileEntity();
    zipOutputStream.close();
  }

}