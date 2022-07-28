// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao;

import java.util.List;
import java.util.Optional;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.Bind;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlQuery;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

import com.cloudera.hue.querystore.common.entities.TezAppInfo;
import com.cloudera.hue.querystore.common.repository.JdbiDao;

@RegisterBeanMapper(TezAppInfo.class)
public interface TezAppInfoDao extends JdbiDao<TezAppInfo> {

  @Override
  @SqlQuery("SELECT * FROM tez_app_info WHERE id = :id")
  Optional<TezAppInfo> findOne(@Bind("id") long id);

  @SqlQuery("SELECT ta.* FROM tez_app_info ta join dag_info di on ta.app_id = di.application_id" +
      " WHERE di.id = :dagInfoId")
  Optional<TezAppInfo> findByDagInfoId(@Bind("dagInfoId") Long dagInfoId);

  @Override
  @SqlQuery("SELECT * FROM tez_app_info")
  List<TezAppInfo> findAll();

  @Override
  @SqlUpdate("INSERT INTO tez_app_info (app_id, submit_time, config_compressed) "
      + "VALUES (:appId, :submitTime, :configCompressed)")
  @GetGeneratedKeys
  long insert(@BindBean TezAppInfo appInfo);

  @Override
  @SqlUpdate("DELETE FROM tez_app_info WHERE id = :id")
  int delete(@Bind("id") long id);

  @Override
  @SqlUpdate("UPDATE tez_app_info SET app_id = :appId, submit_time = :submitTime, " +
      "config_compressed = :configCompressed WHERE id = :id")
  int update(@BindBean TezAppInfo appInfo);

  @SqlUpdate("delete from tez_app_info where submit_time < :submitTime")
  int deleteOlder(@Bind("submitTime") long submitTime);
}
