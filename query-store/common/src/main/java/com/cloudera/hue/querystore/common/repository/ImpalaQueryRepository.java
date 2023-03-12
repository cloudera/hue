// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;

import javax.inject.Inject;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.AppAuthentication.Role;
import com.cloudera.hue.querystore.common.dao.ImpalaQueryDao;
import com.cloudera.hue.querystore.common.dto.FacetEntry;
import com.cloudera.hue.querystore.common.dto.FacetValue;
import com.cloudera.hue.querystore.common.dto.ImpalaSearchDetails;
import com.cloudera.hue.querystore.common.dto.QuerySearchParams;
import com.cloudera.hue.querystore.common.dto.SortDetails;
import com.cloudera.hue.querystore.common.entities.ImpalaQueryEntity;

/**
 * JDBI repository for Impala Queries
 */
public class ImpalaQueryRepository extends JdbiRepository<ImpalaQueryEntity, ImpalaQueryDao> {

  @Inject
  public ImpalaQueryRepository(ImpalaQueryDao dao){
    super(dao);
  }

  public Optional<ImpalaQueryEntity> findByQueryId(String queryId) {
    return dao.findByQueryId(queryId);
  }

  public List<ImpalaQueryEntity> search(QuerySearchParams params, String currentUserName, AppAuthentication.Role role) {
    ImpalaSearchDetails search = new ImpalaSearchDetails(params);
    SortDetails sort = new SortDetails(params, ImpalaQueryEntity.TABLE_INFORMATION);

    List<ImpalaQueryEntity> queries = dao.search(
      params.getStartTime(), params.getEndTime(),
      checkCurrentUser(role), currentUserName,

      isNotNull(search.getText()), search.getText(), search.getQueryText(),

      isNotNull(search.getStatuses()), search.getStatuses(),
      isNotNull(search.getQueryTypes()), search.getQueryTypes(),
      isNotNull(search.getUserNames()), search.getUserNames(),
      isNotNull(search.getCoordinators()), search.getCoordinators(),
      isNotNull(search.getDefaultDbs()), search.getDefaultDbs(),
      isNotNull(search.getRequestPools()), search.getRequestPools(),

      sort.getColumnName(), sort.getOrder(),
      params.getLimit(), params.getOffset()
    );

    return queries;
  }

  public long getSearchSize(QuerySearchParams params, String currentUserName, AppAuthentication.Role role) {
    return dao.getSearchSize(
      params.getStartTime(), params.getEndTime(),
      checkCurrentUser(role), currentUserName
    );
  }

  public int deleteOlder(long startTime) {
    return dao.deleteOlder(startTime * 1000);
  }

  public Optional<List<FacetValue>> getFacetValues(Set<String> facetFieldSets,
        long startTime, long endTime,
        String currentUserName, Role userRole, int facetsResultLimit) {

    List<FacetValue> facetValueList = new ArrayList<FacetValue>();
    boolean checkCurrentUser = checkCurrentUser(userRole);

    for (String facetField: facetFieldSets) {
      List<FacetEntry> facetEntry = dao.getFacetValues(facetField,
          startTime, endTime,
          checkCurrentUser, currentUserName,
          facetsResultLimit);
      facetValueList.add(new FacetValue(facetField, facetEntry));
    }
    return Optional.of(facetValueList);
  }
}
