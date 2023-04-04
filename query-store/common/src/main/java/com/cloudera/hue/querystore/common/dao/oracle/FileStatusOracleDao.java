// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.querystore.common.dao.oracle;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

import com.cloudera.hue.querystore.common.dao.FileStatusDao;
import com.cloudera.hue.querystore.common.entities.FileStatusEntity;

@RegisterBeanMapper(FileStatusEntity.class)
public interface FileStatusOracleDao extends FileStatusDao {
  @Override
  @SqlUpdate("insert into file_status (file_type, \"date\", file_name, position, " +
      "last_event_time, finished) values (:fileType, :date, :filePath, :position, " +
      ":lastEventTime, :finished)")
  @GetGeneratedKeys("id")
  long insert(@BindBean FileStatusEntity entity);

  @Override
  @SqlUpdate("update file_status set file_type = :fileType, \"date\" = :date, " +
      "file_name = :filePath, position = :position, last_event_time = :lastEventTime, " +
      "finished = :finished where id = :id" )
  int update(@BindBean FileStatusEntity savedQuery);
}
