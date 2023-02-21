// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.Set;

import javax.inject.Inject;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.AppAuthentication.Role;
import com.cloudera.hue.querystore.common.dao.ImpalaQueryDao;
import com.cloudera.hue.querystore.common.dto.FacetEntry;
import com.cloudera.hue.querystore.common.dto.FacetValue;
import com.cloudera.hue.querystore.common.entities.ImpalaQueryEntity;
import com.cloudera.hue.querystore.common.exception.DBUpdateFailedException;

/**
 * JDBI repository for Hive Query
 */
public class ImpalaQueryRepository extends JdbiRepository<ImpalaQueryEntity, ImpalaQueryDao> {

  @Inject
  public ImpalaQueryRepository(ImpalaQueryDao dao){
    super(dao);
  }

  public Optional<ImpalaQueryEntity> findByHiveQueryId(String queryId) {
    return dao.findByQueryId(queryId);
  }

  @Override
  public Optional<ImpalaQueryEntity> findOne(long id) {
    return dao.findOne(id);
  }

  @Override
  public Collection<ImpalaQueryEntity> findAll() {
    return dao.findAll();
  }

  /**
   * Insert or updates the entity. The returned entity does not contain the auto updated fields like version.
   * Do not use this entity to update again. Get the entity again using findOne and use that object to do any
   * further updates. The return type is carried over from legacy hibernate implementation
   * TODO: make this method and super method return void for better clarity. Or may be we need not Override.
   * @param entity Entity object to be saved or updated.
   * @return
   */
  @Override
  public ImpalaQueryEntity save(ImpalaQueryEntity entity) {
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

  public Optional<List<FacetValue>> getFacetValues(Set<String> facetFieldSets,
        long startTime, long endTime,
        String userName, Role userRole, int facetsResultLimit) {

    List<FacetValue> facetValueList = new ArrayList<FacetValue>();
    boolean userCheck = !AppAuthentication.Role.ADMIN.equals(userRole);

    for (String facetField: facetFieldSets) {
      List<FacetEntry> facetEntry = dao.getFacetValues(facetField,
          startTime, endTime,
          userName, userCheck, facetsResultLimit);
      facetValueList.add(new FacetValue(facetField, facetEntry));
    }
    return Optional.of(facetValueList);
  }
}
