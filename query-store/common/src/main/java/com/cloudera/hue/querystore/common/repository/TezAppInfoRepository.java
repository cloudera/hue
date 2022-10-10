// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.Collection;
import java.util.Optional;

import javax.inject.Inject;

import com.cloudera.hue.querystore.common.dao.TezAppInfoDao;
import com.cloudera.hue.querystore.common.entities.TezAppInfo;

public class TezAppInfoRepository extends JdbiRepository<TezAppInfo, TezAppInfoDao> {

  @Inject
  public TezAppInfoRepository(TezAppInfoDao dao) {
    super(dao);
  }

  @Override
  public Optional<TezAppInfo> findOne(long id) {
    return dao.findOne(id);
  }

  public Optional<TezAppInfo> findByDagInfoId(Long dagInfoId) {
    return dao.findByDagInfoId(dagInfoId);
  }

  @Override
  public Collection<TezAppInfo> findAll() {
    return dao.findAll();
  }

  @Override
  public TezAppInfo save(TezAppInfo entity) {
    if (entity.getId() == null) {
      entity.setId(dao.insert(entity));
    } else {
      dao.update(entity);
    }
    return entity;
  }

  @Override
  public boolean delete(long id) {
    return !(0 == dao.delete(id));
  }

  public int deleteOlder(long submitTime) {
    return dao.deleteOlder(submitTime * 1000);
  }

  public int purge() {
    return dao.purge();
  }
}
