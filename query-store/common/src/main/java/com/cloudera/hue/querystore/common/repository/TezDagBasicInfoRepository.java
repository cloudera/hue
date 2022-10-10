// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.Collection;
import java.util.Optional;

import javax.inject.Inject;

import com.cloudera.hue.querystore.common.dao.TezDagBasicInfoDao;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;

/**
 * JDBI repository for dag_info table.
 */
public class TezDagBasicInfoRepository extends JdbiRepository<TezDagBasicInfo, TezDagBasicInfoDao> {
  @Inject
  public TezDagBasicInfoRepository(TezDagBasicInfoDao dao){
    super(dao);
  }

  public Optional<TezDagBasicInfo> findByDagId(String dagId) {
    return dao.getByDagId(dagId);
  }

  public Collection<TezDagBasicInfo> getByHiveQueryTableId(Long hiveQueryId) {
    return dao.getByHiveQueryTableId(hiveQueryId);
  }

  @Override
  public Optional<TezDagBasicInfo> findOne(long id) {
    return dao.findOne(id);
  }

  @Override
  public Collection<TezDagBasicInfo> findAll() {
    return dao.findAll();
  }

  @Override
  public TezDagBasicInfo save(TezDagBasicInfo entity) {
    if (entity.getId() == null) {
      Long id = dao.insert(entity);
      entity.setId(id);
    } else {
      dao.update(entity);
    }
    return entity;
  }

  @Override
  public boolean delete(long id) {
    return dao.delete(id) != 0;
  }

  public int deleteOlder(long startTime) {
    return dao.deleteOlder(startTime * 1000);
  }

  public int purge() {
    return dao.purge();
  }

}
