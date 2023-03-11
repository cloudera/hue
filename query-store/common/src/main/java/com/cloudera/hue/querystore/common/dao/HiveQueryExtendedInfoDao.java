// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.Bind;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.customizer.BindList;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlQuery;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.cloudera.hue.querystore.common.repository.JdbiDao;

/**
 * Jdbi dao for QueryDetails
 */
@RegisterBeanMapper(HiveQueryExtendedInfo.class)
public interface HiveQueryExtendedInfoDao extends JdbiDao<HiveQueryExtendedInfo> {
  @Override
  @SqlQuery("select * from query_details where id = :id")
  Optional<HiveQueryExtendedInfo> findOne(@Bind("id") long id);

  @Override
  @SqlQuery("select * from query_details")
  Collection<HiveQueryExtendedInfo> findAll();

  @Override
  @SqlUpdate("insert into query_details (perf, hive_query_id, explain_plan_compressed, configuration_compressed, " +
      "created_at) values (cast(:perf as json), :hiveQueryId, :explainPlanCompressed, :configurationCompressed, " +
      ":createdAt)")
  @GetGeneratedKeys
  long insert(@BindBean HiveQueryExtendedInfo entity);

  @Override
  @SqlUpdate("delete from query_details where id = :id")
  int delete(@Bind("id") long id);

  @Override
  @SqlUpdate("update query_details set perf = cast(:perf as json), hive_query_id = :hiveQueryId, " +
      "explain_plan_compressed = :explainPlanCompressed, configuration_compressed = :configurationCompressed " +
      "where id = :id" )
  int update(@BindBean HiveQueryExtendedInfo QueryDetails);

  @SqlQuery("select qd.* from query_details as qd join hive_query as hq on qd.hive_query_id = hq.id " +
      "where hq.query_id = :hiveQueryId")
  Optional<HiveQueryExtendedInfo> findByHiveQueryId(@Bind("hiveQueryId") String hiveQueryId);

  @SqlQuery("select * from query_details  where hive_query_id = :hiveQueryTableId")
  Optional<HiveQueryExtendedInfo> findByHiveQueryTableId(@Bind("hiveQueryTableId") Long hiveQueryTableId);

  @SqlQuery("select qd.* from query_details as qd " +
      "join hive_query as hq on qd.hive_query_id = hq.id " +
      "join dag_info as di on hq.id = di.hive_query_id " +
      "where di.dag_id = :dagId")
  Optional<HiveQueryExtendedInfo> findByDagId(@Bind("dagId") String dagId);

  @SqlQuery("SELECT qd.* FROM query_details as qd join hive_query as hq on qd.hive_query_id = hq.id " +
      "WHERE hq.processed = :processedState AND hq.status IN (<statuses>) limit 1000")
  Stream<HiveQueryExtendedInfo> findNextSetToProcessForStats(@Bind("processedState") boolean processedState,
      @BindList("statuses") List<String> statuses);

  @SqlUpdate("delete from query_details qd using hive_query hq " +
      "where hq.id = qd.hive_query_id and hq.start_time < :startTime")
  int deleteOlder(@Bind("startTime") long startTime);

  @SqlUpdate("vacuum full query_details")
  int purge();

}
