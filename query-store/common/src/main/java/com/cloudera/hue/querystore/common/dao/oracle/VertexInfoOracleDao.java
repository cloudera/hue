// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao.oracle;

import java.util.Optional;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.Bind;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlQuery;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

import com.cloudera.hue.querystore.common.dao.VertexInfoDao;
import com.cloudera.hue.querystore.common.entities.VertexInfo;

@RegisterBeanMapper(VertexInfo.class)
public interface VertexInfoOracleDao extends VertexInfoDao {
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
  @GetGeneratedKeys("id")
  long insert(@BindBean VertexInfo entity);

  @SqlQuery("select * from vertex_info where vertex_id = :vertexId")
  Optional<VertexInfo> findByVertexId(@Bind("vertexId") String vertexId);
}