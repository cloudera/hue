// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao.oracle;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

import com.cloudera.hue.querystore.common.dao.TezDagBasicInfoDao;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;

@RegisterBeanMapper(TezDagBasicInfo.class)
public interface TezDagBasicInfoOracleDao extends TezDagBasicInfoDao {
  @Override
  @SqlUpdate("insert into dag_info (dag_id, dag_name, application_id, init_time, start_time," +
      " end_time, status, am_webservice_ver, am_log_url, queue_name, caller_id, caller_type," +
      " hive_query_id, created_at, source_file) values (:dagId, :dagName, :applicationId, :initTime, " +
      ":startTime, :endTime, :status, :amWebserviceVer, :amLogUrl, :queueName, :callerId, " +
      ":callerType, :hiveQueryId, :createdAt, :sourceFile)")
  @GetGeneratedKeys("id")
  long insert(@BindBean TezDagBasicInfo entity);

}
