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

import com.cloudera.hue.querystore.common.entities.TezDagExtendedInfo;
import com.cloudera.hue.querystore.common.repository.JdbiDao;

@RegisterBeanMapper(TezDagExtendedInfo.class)
public interface TezDagExtendedInfoDao extends JdbiDao<TezDagExtendedInfo> {
  @Override
  @SqlQuery("select * from dag_details where id = :id")
  Optional<TezDagExtendedInfo> findOne(@Bind("id") long id);

  @Override
  @SqlQuery("select * from dag_details")
  Collection<TezDagExtendedInfo> findAll();

  @Override
  @SqlUpdate("insert into dag_details (diagnostics, hive_query_id, dag_info_id, dag_plan_compressed, " +
      "vertex_name_id_mapping_compressed, counters_compressed, created_at) values (:diagnostics, :hiveQueryId, " +
      ":dagInfoId, :dagPlanCompressed, :vertexNameIdMappingCompressed, :countersCompressed, :createdAt)")
  @GetGeneratedKeys
  long insert(@BindBean TezDagExtendedInfo entity);

  @Override
  @SqlUpdate("delete from dag_details where id = :id")
  int delete(@Bind("id") long id);

  @Override
  @SqlUpdate("update dag_details set diagnostics = :diagnostics, dag_plan_compressed = :dagPlanCompressed, " +
      "vertex_name_id_mapping_compressed = :vertexNameIdMappingCompressed, counters_compressed = :countersCompressed," +
      "hive_query_id = :hiveQueryId, dag_info_id = :dagInfoId where id = :id")
  int update(@BindBean TezDagExtendedInfo QueryDetails);

  @SqlQuery("select dd.* from dag_details as dd join hive_query as hq " +
      "on dd.hive_query_id = hq.id where hq.query_id = :hiveQueryId")
  Collection<TezDagExtendedInfo> findByHiveQueryId(@Bind("hiveQueryId") String hiveQueryId);

  @SqlQuery("select dd.* from dag_details as dd join dag_info as di " +
      "on dd.dag_info_id = di.id where di.dag_id = :dagId")
  Optional<TezDagExtendedInfo> findByDagId(@Bind("dagId") String dagId);

  @SqlUpdate("delete from dag_details dd using dag_info di " +
      "where dd.dag_info_id = di.id and di.start_time < :startTime")
  int deleteOlder(@Bind("startTime") long startTime);

  @SqlUpdate("vacuum full dag_details")
  int purge();

}
