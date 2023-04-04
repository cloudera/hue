// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao.oracle;

import java.util.Optional;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.Bind;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlQuery;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

import com.cloudera.hue.querystore.common.dao.HiveQueryExtendedInfoDao;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;

/**
 * Jdbi dao for QueryDetails
 */
@RegisterBeanMapper(HiveQueryExtendedInfo.class)
public interface HiveQueryExtendedInfoOracleDao extends HiveQueryExtendedInfoDao {
  @Override
  @SqlUpdate("insert into query_details (perf, hive_query_id, explain_plan_compressed, configuration_compressed, " +
      "created_at) values (:perf, :hiveQueryId, :explainPlanCompressed, :configurationCompressed, " +
      ":createdAt)")
  @GetGeneratedKeys("id")
  long insert(@BindBean HiveQueryExtendedInfo entity);

  @Override
  @SqlUpdate("update query_details set perf = :perf, hive_query_id = :hiveQueryId, " +
      "explain_plan_compressed = :explainPlanCompressed, configuration_compressed = :configurationCompressed " +
      "where id = :id" )
  int update(@BindBean HiveQueryExtendedInfo QueryDetails);

  @SqlQuery("select qd.* from query_details qd join hive_query hq on qd.hive_query_id = hq.id " +
      "where hq.query_id = :hiveQueryId")
  Optional<HiveQueryExtendedInfo> findByHiveQueryId(@Bind("hiveQueryId") String hiveQueryId);
}
