// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.Bind;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.customizer.BindList;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlQuery;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.repository.JdbiDao;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

/**
 * Jdbi dao for HiveQuery
 */
@RegisterBeanMapper(HiveQueryBasicInfo.class)
public interface HiveQueryBasicInfoDao extends JdbiDao<HiveQueryBasicInfo> {
  @Override
  @SqlQuery("select * from hive_query where id = :id")
  Optional<HiveQueryBasicInfo> findOne(@Bind("id") long id);

  @Override
  @SqlQuery("select * from hive_query")
  Collection<HiveQueryBasicInfo> findAll();

  @Override
  @SqlUpdate("insert into hive_query (query_id,query,start_time,end_time,elapsed_time,status,queue_name,user_id," +
      "request_user,cpu_time,physical_memory,virtual_memory,data_read,data_written,operation_id,client_ip_address," +
      "hive_instance_address,hive_instance_type,session_id,log_id,thread_id,execution_mode,tables_read,tables_written," +
      "databases_used, domain_id,llap_app_id,used_cbo,first_task_started_time,waiting_time,resource_utilization," +
      "version, created_at) " +
      "values" +
      " (:queryId,:query,:startTime,:endTime,:elapsedTime,:status," +
      ":queueName,:userId,:requestUser,:cpuTime,:physicalMemory,:virtualMemory,:dataRead,:dataWritten,:operationId," +
      ":clientIpAddress,:hiveInstanceAddress,:hiveInstanceType,:sessionId,:logId,:threadId,:executionMode," +
      "cast(:tablesRead as jsonb),cast( :tablesWritten as jsonb),cast( :databasesUsed as jsonb),:domainId," +
      ":llapAppId,:usedCBO,:firstTaskStartedTime,:waitingTime,:resourceUtilization,0,:createdAt)")
  @GetGeneratedKeys
  long insert(@BindBean HiveQueryBasicInfo entity);

  @Override
  @SqlUpdate("delete from hive_query where id = :id")
  int delete(@Bind("id") long id);

  @Override
  @SqlUpdate("update hive_query set query_id = :queryId, query = :query, start_time = :startTime, " +
      "end_time = :endTime, elapsed_time = :elapsedTime, status = :status, queue_name = :queueName, " +
      "user_id = :userId, request_user = :requestUser, cpu_time = :cpuTime, physical_memory = :physicalMemory, " +
      "virtual_memory = :virtualMemory, data_read = :dataRead, data_written = :dataWritten, " +
      "operation_id = :operationId, client_ip_address = :clientIpAddress, " +
      "hive_instance_address = :hiveInstanceAddress, hive_instance_type = :hiveInstanceType, session_id = :sessionId," +
      "log_id = :logId, thread_id = :threadId, execution_mode = :executionMode, tables_read = cast(:tablesRead as jsonb), " +
      "tables_written = cast( :tablesWritten as jsonb), databases_used = cast( :databasesUsed as jsonb), " +
      "domain_id = :domainId, llap_app_id = :llapAppId, used_cbo = :usedCBO, " +
      "first_task_started_time = :firstTaskStartedTime, waiting_time = :waitingTime, " +
      "resource_utilization = :resourceUtilization, version = :version + 1 " +
      "where id = :id and version = :version" )
  int update(@BindBean HiveQueryBasicInfo HiveQuery);

  @SqlUpdate("update hive_query SET processed = true, version = version + 1 WHERE id in (<hiveIds>)")
  int updateProcessed(@BindList("hiveIds") List<Long> hiveIds);

  @SqlQuery("select * from hive_query where query_id = :queryId")
  Optional<HiveQueryBasicInfo> findByHiveQueryId(@Bind("queryId") String queryId);

  @SqlUpdate("delete from hive_query where start_time < :startTime")
  int deleteOlder(@Bind("startTime") long startTime);

  @SqlUpdate("vacuum full hive_query")
  int purge();

}
