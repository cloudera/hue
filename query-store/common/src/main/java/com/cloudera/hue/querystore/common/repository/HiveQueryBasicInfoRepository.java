// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import javax.inject.Inject;

import org.jdbi.v3.core.mapper.JoinRow;
import org.jdbi.v3.core.mapper.JoinRowMapper;
import org.jdbi.v3.core.mapper.reflect.BeanMapper;

import com.cloudera.hue.querystore.common.dao.HiveQueryBasicInfoDao;
import com.cloudera.hue.querystore.common.dto.FacetEntry;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.exception.DBUpdateFailedException;

import lombok.extern.slf4j.Slf4j;

/**
 * JDBI repository for Hive Query
 */
@Slf4j
public class HiveQueryBasicInfoRepository extends JdbiRepository<HiveQueryBasicInfo, HiveQueryBasicInfoDao> {

  @Inject
  public HiveQueryBasicInfoRepository(HiveQueryBasicInfoDao dao){
    super(dao);
  }

  public List<JoinRow> executeSearchQuery(String query, Map<String, Object> parameters) {
    return getDao().withHandle(handle -> {
      handle.registerRowMapper(BeanMapper.factory(HiveQueryBasicInfo.class, "hq"));
      handle.registerRowMapper(BeanMapper.factory(TezDagBasicInfo.class, "di"));
      handle.registerRowMapper(JoinRowMapper.forTypes(HiveQueryBasicInfo.class, TezDagBasicInfo.class));
      return handle.createQuery(query).bindMap(parameters).mapTo(JoinRow.class).list();
    });
  }

  public Long executeSearchCountQuery(String countQuery, Map<String, Object> parameters) {
    return getDao().withHandle(handle -> handle.createQuery(countQuery).bindMap(parameters)
        .mapTo(Long.class).findFirst().orElse(0l));
  }

  public List<FacetEntry> executeFacetQuery(String query, Map<String, Object> parameters) {
    return getDao().withHandle(handle -> {
      handle.registerRowMapper(BeanMapper.factory(FacetEntry.class));
        return handle.createQuery(query).bindMap(parameters).mapTo(FacetEntry.class).list();
    });
  }

  public Optional<HiveQueryBasicInfo> findByHiveQueryId(String queryId) {
    return dao.findByHiveQueryId(queryId);
  }

  public void updateQueriesAsProcessed(List<Long> ids) {
    int count = dao.updateProcessed(ids);
    log.info("{} queries are updated as processed.",  count);
  }

  @Override
  public Optional<HiveQueryBasicInfo> findOne(long id) {
    return dao.findOne(id);
  }

  @Override
  public Collection<HiveQueryBasicInfo> findAll() {
    return dao.findAll();
  }

  /**
   * saves or updates the entity. The returned entity does not contain the auto updated fields like version.
   * Do not use this entity to update again. Get the entity again using findOne and use that object to do any
   * further updates. The return type is carried over from legacy hibernate implementation
   * TODO: make this method and super method return void for better clarity.
   * @param entity Entity object to be saved or updated.
   * @return
   */
  @Override
  public HiveQueryBasicInfo save(HiveQueryBasicInfo entity) {
    if (entity.getId() == null) {
      Long id = dao.insert(entity);
      entity.setId(id);
    } else {
      int update = dao.update(entity);
      if (0 == update) {
        throw new DBUpdateFailedException(entity);
      }
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
