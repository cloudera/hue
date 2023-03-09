// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.querystore.common.dao;

import java.util.Collection;
import java.util.Optional;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.Bind;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlQuery;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

import com.cloudera.hue.querystore.common.entities.FileStatusEntity;
import com.cloudera.hue.querystore.common.entities.FileStatusEntity.FileStatusType;
import com.cloudera.hue.querystore.common.repository.JdbiDao;


@RegisterBeanMapper(FileStatusEntity.class)
public interface FileStatusDao extends JdbiDao<FileStatusEntity> {

  @Override
  @SqlQuery("select * from file_status where id = :id")
  Optional<FileStatusEntity> findOne(@Bind("id") long id);

  @Override
  @SqlQuery("select * from file_status")
  Collection<FileStatusEntity> findAll();

  @SqlQuery("select * from file_status where file_type = :type")
  Collection<FileStatusEntity> findAllByType(@Bind("type") FileStatusType type);

  @Override
  @SqlUpdate("insert into file_status (file_type, date, file_name, position, " +
      "last_event_time, finished) values (:fileType, :date, :filePath, :position, " +
      ":lastEventTime, :finished)")
  @GetGeneratedKeys
  long insert(@BindBean FileStatusEntity entity);

  @Override
  @SqlUpdate("delete from file_status where id = :id")
  int delete(@Bind("id") long id);

  @Override
  @SqlUpdate("update file_status set file_type = :fileType, date = :date, " +
      "file_name = :filePath, position = :position, last_event_time = :lastEventTime, " +
      "finished = :finished where id = :id" )
  int update(@BindBean FileStatusEntity savedQuery);
}
