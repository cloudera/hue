// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao.oracle;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;

import com.cloudera.hue.querystore.common.dao.TezAppInfoDao;
import com.cloudera.hue.querystore.common.entities.TezAppInfo;

@RegisterBeanMapper(TezAppInfo.class)
public interface TezAppInfoOracleDao extends TezAppInfoDao {

  @Override
  @SqlUpdate("INSERT INTO tez_app_info (app_id, submit_time, config_compressed) "
      + "VALUES (:appId, :submitTime, :configCompressed)")
  @GetGeneratedKeys("id")
  long insert(@BindBean TezAppInfo appInfo);

}
