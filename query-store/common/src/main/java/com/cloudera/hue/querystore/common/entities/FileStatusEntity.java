// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import java.time.LocalDate;

import org.jdbi.v3.core.mapper.reflect.ColumnName;

import lombok.Data;

/**
 * Table to store list of files currently being read and their positions.
 */
@Data
public class FileStatusEntity implements JdbiEntity {
  public enum FileStatusType { HIVE, TEZ, TEZ_APP, IMPALA };

  private Long id;
  private FileStatusType fileType;
  private LocalDate date;

  // Keeping column as file_name to avoid migration changes. We have a UNIQUE CONSTRAINT that uses file_name.
  @ColumnName("file_name")
  private String filePath;
  private volatile long position;
  private volatile long lastEventTime;
  private volatile boolean finished;
}
