// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao.oracle;

import java.util.Collection;
import java.util.Optional;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.Bind;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlQuery;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

import com.cloudera.hue.querystore.common.dao.TezDagExtendedInfoDao;
import com.cloudera.hue.querystore.common.entities.TezDagExtendedInfo;

@RegisterBeanMapper(TezDagExtendedInfo.class)
public interface TezDagExtendedInfoOracleDao extends TezDagExtendedInfoDao {
  @Override
  @SqlUpdate("insert into dag_details (diagnostics, hive_query_id, dag_info_id, dag_plan_compressed, " +
      "vertex_name_id_mapping_compressed, counters_compressed, created_at) values (:diagnostics, :hiveQueryId, " +
      ":dagInfoId, :dagPlanCompressed, :vertexNameIdMappingCompressed, :countersCompressed, :createdAt)")
  @GetGeneratedKeys("id")
  long insert(@BindBean TezDagExtendedInfo entity);

  @SqlQuery("select dd.* from dag_details dd join hive_query hq " +
      "on dd.hive_query_id = hq.id where hq.query_id = :hiveQueryId")
  Collection<TezDagExtendedInfo> findByHiveQueryId(@Bind("hiveQueryId") String hiveQueryId);

  @SqlQuery("select dd.* from dag_details dd join dag_info di " +
      "on dd.dag_info_id = di.id where di.dag_id = :dagId")
  Optional<TezDagExtendedInfo> findByDagId(@Bind("dagId") String dagId);
}
