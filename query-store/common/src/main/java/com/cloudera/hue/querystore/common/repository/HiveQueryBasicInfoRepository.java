// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.Set;

import javax.inject.Inject;

import org.apache.commons.lang3.StringUtils;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.AppAuthentication.Role;
import com.cloudera.hue.querystore.common.dao.HiveQueryBasicInfoDao;
import com.cloudera.hue.querystore.common.dto.FacetEntry;
import com.cloudera.hue.querystore.common.dto.FacetValue;
import com.cloudera.hue.querystore.common.dto.HiveSearchDetails;
import com.cloudera.hue.querystore.common.dto.QuerySearchParams;
import com.cloudera.hue.querystore.common.dto.SortDetails;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.exception.DBUpdateFailedException;
import com.cloudera.hue.querystore.common.services.QuerySearchParamsUtils;

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

  public Optional<List<FacetValue>> getFacetValues(Set<String> facetFieldSets, long startTime,
        long endTime, String userName, Role role, int facetsResultLimit) {

    List<FacetValue> facetValueList = new ArrayList<FacetValue>();

    for (String facetField: facetFieldSets) {
      List<FacetEntry> facetEntry = dao.getFacetValues(facetField, startTime, endTime, userName, checkCurrentUser(role), facetsResultLimit);
      facetValueList.add(new FacetValue(facetField, facetEntry));
    }
    return Optional.of(facetValueList);
  }

  public long getSearchResultsCount(QuerySearchParams params, String userName, AppAuthentication.Role role) {
    return dao.getSearchResultsCount(params.getStartTime(), params.getEndTime(), checkCurrentUser(role), userName);
  }

  public List<HiveQueryBasicInfo> getSearchResults(QuerySearchParams reqParams, String userName, Role role) {
    QuerySearchParams params = QuerySearchParamsUtils.standardize(reqParams);
    HiveSearchDetails fields = new HiveSearchDetails(params);

    SortDetails sort = new SortDetails(params, HiveQueryBasicInfo.TABLE_INFORMATION);

    List<HiveQueryBasicInfo> searchResultList = dao.getSearchResults(
        params.getStartTime(), params.getEndTime(),
        checkCurrentUser(role), userName,

        isNotNull(fields.getText()), fields.getText(), fields.getQueryText(),

        isNotNull(fields.getStatuses()), fields.getStatuses(),
        isNotNull(fields.getQueueNames()), fields.getQueueNames(),
        isNotNull(fields.getUserIds()), fields.getUserIds(),
        isNotNull(fields.getExecutionModes()), fields.getExecutionModes(),
        isNotNull(fields.getUsedCbo()), fields.getUsedCbo(),

        sort.getColumnName(), sort.getOrder(),
        params.getOffset(), params.getLimit()
    );
    return searchResultList;
  }
}
