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

import com.cloudera.hue.querystore.common.entities.VertexInfo;
import com.cloudera.hue.querystore.common.repository.JdbiDao;

@RegisterBeanMapper(VertexInfo.class)
public interface VertexInfoDao extends JdbiDao<VertexInfo> {

  @Override
  @SqlQuery("select * from vertex_info where id = :id")
  Optional<VertexInfo> findOne(@Bind("id") long id);

  @SqlQuery("select * from vertex_info where vertex_id = :vertexId LIMIT 1")
  Optional<VertexInfo> findByVertexId(@Bind("vertexId") String vertexId);

  @Override
  @SqlQuery("select * from vertex_info")
  Collection<VertexInfo> findAll();

  @SqlQuery("select vi.* from vertex_info vi JOIN dag_info di on vi.dag_id = di.id where di.dag_id = :dagId")
  Collection<VertexInfo> findAllByDagId(@Bind("dagId") String dagId);

  @Override
  @SqlUpdate("insert into vertex_info" +
    "(name, vertex_id, dag_id, domain_id, task_count, succeeded_task_count, completed_task_count," +
    "failed_task_count, killed_task_count, failed_task_attempt_count, killed_task_attempt_count," +
    "class_name, start_time, end_time, init_requested_time, start_requested_time, status," +
    "counters_compressed, stats_compressed, events_compressed, created_at)" +
    " values " +
    "(:name, :vertexId, :dagId, :domainId, :taskCount, :succeededTaskCount, :completedTaskCount," +
    ":failedTaskCount, :killedTaskCount, :failedTaskAttemptCount, :killedTaskAttemptCount," +
    ":className, :startTime, :endTime, :initRequestedTime, :startRequestedTime, :status," +
    ":countersCompressed, :statsCompressed, :eventsCompressed, :createdAt)")
  @GetGeneratedKeys
  long insert(@BindBean VertexInfo entity);

  @Override
  @SqlUpdate("delete from vertex_info where id = :id")
  int delete(@Bind("id") long id);

  @Override
  @SqlUpdate("update vertex_info set " +
    "name = :name, vertex_id = :vertexId, dag_id = :dagId, domain_id = :domainId, task_count = :taskCount," +
    "succeeded_task_count = :succeededTaskCount, completed_task_count = :completedTaskCount," +
    "failed_task_count = :failedTaskCount, killed_task_count = :killedTaskCount," +
    "failed_task_attempt_count = :failedTaskAttemptCount, killed_task_attempt_count = :killedTaskAttemptCount," +
    "class_name = :className, start_time = :startTime, end_time = :endTime," +
    "init_requested_time = :initRequestedTime, start_requested_time = :startRequestedTime, status = :status," +
    "counters_compressed = :countersCompressed, events_compressed = :eventsCompressed, " +
    "stats_compressed = :statsCompressed " +
    "where id = :id" )
  int update(@BindBean VertexInfo savedQuery);

  @SqlUpdate("delete from vertex_info vi using dag_info di " +
      "where di.id = vi.dag_id and di.start_time < :startTime")
  int deleteOlder(@Bind("startTime") long startTime);

  @SqlUpdate("vacuum full vertex_info")
  int purge();

}