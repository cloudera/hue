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

import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.repository.JdbiDao;

@RegisterBeanMapper(TezDagBasicInfo.class)
public interface TezDagBasicInfoDao extends JdbiDao<TezDagBasicInfo> {
  @Override
  @SqlQuery("select * from dag_info where id = :id")
  Optional<TezDagBasicInfo> findOne(@Bind("id") long id);

  @Override
  @SqlQuery("select * from dag_info")
  Collection<TezDagBasicInfo> findAll();

  @Override
  @SqlUpdate("insert into dag_info (dag_id, dag_name, application_id, init_time, start_time," +
      " end_time, status, am_webservice_ver, am_log_url, queue_name, caller_id, caller_type," +
      " hive_query_id, created_at, source_file) values (:dagId, :dagName, :applicationId, :initTime, " +
      ":startTime, :endTime, :status, :amWebserviceVer, :amLogUrl, :queueName, :callerId, " +
      ":callerType, :hiveQueryId, :createdAt, :sourceFile)")
  @GetGeneratedKeys
  long insert(@BindBean TezDagBasicInfo entity);

  @Override
  @SqlUpdate("delete from dag_info where id = :id")
  int delete(@Bind("id") long id);

  @Override
  @SqlUpdate("update dag_info set dag_id = :dagId, dag_name = :dagName, application_id = :applicationId," +
      "init_time = :initTime, start_time = :startTime, end_time = :endTime, status = :status," +
      "am_webservice_ver = :amWebserviceVer, am_log_url = :amLogUrl, queue_name = :queueName," +
      "caller_id = :callerId, caller_type = :callerType, hive_query_id = :hiveQueryId, " +
      "created_at = :createdAt, source_file = :sourceFile where id = :id")
  int update(@BindBean TezDagBasicInfo entity);

  @SqlQuery("select * from dag_info where hive_query_id = :id")
  Collection<TezDagBasicInfo> getByHiveQueryTableId(@Bind("id") Long id);

  @SqlQuery("select * from dag_info where dag_id = :dagId")
  Optional<TezDagBasicInfo> getByDagId(@Bind("dagId") String dagId);

  @SqlUpdate("delete from dag_info where start_time < :startTime")
  int deleteOlder(@Bind("startTime") long startTime);

  @SqlUpdate("vacuum full dag_info")
  int purge();

}
