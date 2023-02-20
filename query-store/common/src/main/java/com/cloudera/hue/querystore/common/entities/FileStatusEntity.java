// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import java.time.LocalDate;

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
  private String fileName;
  private volatile long position;
  private volatile long lastEventTime;
  private volatile boolean finished;
}
