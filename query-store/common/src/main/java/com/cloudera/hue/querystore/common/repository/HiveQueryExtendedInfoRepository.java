// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.Collection;
import java.util.Optional;
import java.util.stream.Stream;

import javax.inject.Inject;

import com.cloudera.hue.querystore.common.dao.HiveQueryExtendedInfoDao;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.google.common.collect.Lists;

public class HiveQueryExtendedInfoRepository extends JdbiRepository<HiveQueryExtendedInfo, HiveQueryExtendedInfoDao> {

  @Inject
  public HiveQueryExtendedInfoRepository(HiveQueryExtendedInfoDao queryDetailsDao) {
    super(queryDetailsDao);
  }

  public Optional<HiveQueryExtendedInfo> findByHiveQueryId(String hiveQueryId) {
    return this.getDao().findByHiveQueryId(hiveQueryId);
  }

  public Optional<HiveQueryExtendedInfo> findByHiveQueryTableId(Long hiveQueryTableId) {
    return this.getDao().findByHiveQueryTableId(hiveQueryTableId);
  }

  public Optional<HiveQueryExtendedInfo> findByDagId(String dagId) {
    return this.getDao().findByDagId(dagId);
  }

  public Stream<HiveQueryExtendedInfo> findQueryDetailsForNextSetOfProcessing() {
    return this.getDao().findNextSetToProcessForStats(false, Lists.newArrayList(
        HiveQueryBasicInfo.Status.SUCCESS.toString(), HiveQueryBasicInfo.Status.ERROR.toString()));
  }

  @Override
  public Optional<HiveQueryExtendedInfo> findOne(long id) {
    return this.getDao().findOne(id);
  }

  @Override
  public Collection<HiveQueryExtendedInfo> findAll() {
    return this.getDao().findAll();
  }

  @Override
  public HiveQueryExtendedInfo save(HiveQueryExtendedInfo entity) {
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
    return !(0 == dao.delete(id));
  }

  public int deleteOlder(long startTime) {
    return dao.deleteOlder(startTime * 1000);
  }

  public int purge() {
    return dao.purge();
  }

}
