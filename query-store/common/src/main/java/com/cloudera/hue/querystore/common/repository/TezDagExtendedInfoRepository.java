// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.Collection;
import java.util.Optional;

import javax.inject.Inject;

import com.cloudera.hue.querystore.common.dao.TezDagExtendedInfoDao;
import com.cloudera.hue.querystore.common.entities.TezDagExtendedInfo;

public class TezDagExtendedInfoRepository extends JdbiRepository<TezDagExtendedInfo, TezDagExtendedInfoDao> {

  @Inject
  public TezDagExtendedInfoRepository(TezDagExtendedInfoDao dao) {
    super(dao);
  }

  @Override
  public Optional<TezDagExtendedInfo> findOne(long id) {
    return dao.findOne(id);
  }

  public Collection<TezDagExtendedInfo> findByHiveQueryId(String hiveQueryId) {
    return this.getDao().findByHiveQueryId(hiveQueryId);
  }

  public Optional<TezDagExtendedInfo> findByDagId(String dagId) {
    return dao.findByDagId(dagId);
  }

  @Override
  public Collection<TezDagExtendedInfo> findAll() {
    return dao.findAll();
  }

  @Override
  public TezDagExtendedInfo save(TezDagExtendedInfo entity) {
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
    return dao.delete(id) == 1;
  }

  public int deleteOlder(long startTime) {
    return dao.deleteOlder(startTime * 1000);
  }

  public int purge() {
    return dao.purge();
  }

}
