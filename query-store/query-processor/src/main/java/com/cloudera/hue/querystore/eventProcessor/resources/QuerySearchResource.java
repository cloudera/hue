// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.resources;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import javax.inject.Inject;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.SecurityContext;

import org.apache.commons.lang.StringUtils;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.config.DasConfiguration.ConfVar;
import com.cloudera.hue.querystore.common.dto.FacetValue;
import com.cloudera.hue.querystore.common.dto.FieldInformation;
import com.cloudera.hue.querystore.common.dto.HiveQueryDto;
import com.cloudera.hue.querystore.common.dto.SearchRequest;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.PageData;
import com.cloudera.hue.querystore.common.services.SanitizeUtility;
import com.cloudera.hue.querystore.common.services.SearchService;
import com.cloudera.hue.querystore.common.util.MetaInfo;
import com.cloudera.hue.querystore.eventProcessor.lifecycle.EventProcessorManager;
import com.cloudera.hue.querystore.orm.EntityField;
import com.cloudera.hue.querystore.orm.EntityTable;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Sets;

import lombok.extern.slf4j.Slf4j;

/**
 * Resource class for working with the hive ide Udfs
 */
@Slf4j
@Path("/query")
public class QuerySearchResource {
  private static final ConfVar<Integer> QP_FACETS_RESULT_LIMIT =
	      new ConfVar<>("hue.query-processor.search.facet.result.limit", 10);

  private final SearchService searchService;
  private final EventProcessorManager eventProcessorManager;
  private final HiveQueryBasicInfoRepository repository;
  private final DasConfiguration dasConfig;

  @Inject
  public QuerySearchResource(SearchService searchService, EventProcessorManager eventProcessorManager, HiveQueryBasicInfoRepository repository,
        DasConfiguration dasConfig) {
    this.searchService = searchService;
    this.eventProcessorManager = eventProcessorManager;
    this.repository = repository;
    this.dasConfig = dasConfig;
  }

  /**
   * Gets a list of query matching the basic search
   */
  @GET
  @Produces(MediaType.APPLICATION_JSON)
  @Path("/search")
  public Response getBasicSearchedQueries(@QueryParam("text") String queryText,
                                          @QueryParam("sort") String sortText,
                                          @QueryParam("type") String searchType,
                                          @QueryParam("offset") Integer offset,
                                          @QueryParam("limit") Integer limit,
                                          @QueryParam("startTime") Long startTime,
                                          @QueryParam("endTime") Long endTime,
                                          @Context SecurityContext securityContext) {
    return getSearchResponse(queryText, sortText, offset, limit, startTime, endTime,
        new ArrayList<>(), new ArrayList<>(), getEffectiveUser(securityContext), searchType);
  }

  /**
   * Gets a list of query matching the basic search
   */
  @POST
  @Produces(MediaType.APPLICATION_JSON)
  @Path("/search")
  public Response getBasicSearchedQueriesWithFacets(SearchRequest.SearchRequestWrapper request,
                                          @Context SecurityContext securityContext) {

    eventProcessorManager.forceRefresh();

    SearchRequest search = request.getSearch();
    return getSearchResponse(search.getText(), search.getSortText(),
        search.getOffset(), search.getLimit(), search.getStartTime(), search.getEndTime(),
        search.getFacets(), search.getRangeFacets(), getEffectiveUser(securityContext), search.getType());
  }

  private Response getSearchResponse(String queryText, String sortText, Integer offset,
      Integer limit, Long startTime, Long endTime, List<SearchRequest.Facet> facets,
      List<SearchRequest.RangeFacet> rangeFacets, String effectiveUser, String searchType) {

    long updateTime = eventProcessorManager.getQueryRefreshTime();
    PageData<HiveQueryDto> pageData = searchService.doBasicSearch(queryText, sortText, offset, limit,
      startTime, endTime, facets, rangeFacets, effectiveUser);

    MetaInfo metaInfo = MetaInfo.builder().fromPageData(pageData, updateTime).build();
    Map<String, Object> response = ImmutableMap.of("queries", pageData.getEntities(), "meta", metaInfo);

    return Response.ok(response).build();
  }

  @GET
  @Produces(MediaType.APPLICATION_JSON)
  @Path("/fields-information")
  public Response getSearchableColumnInfo() {
    List<FieldInformation> fieldsInformations = SearchService.getFieldsInformation();
    return Response.ok(Collections.singletonMap("fieldsInfo", fieldsInformations)).build();
  }

  private String getEffectiveUser(SecurityContext securityContext) {
    if (securityContext.isUserInRole(AppAuthentication.Role.ADMIN.name())) {
      return null;
    }
    return securityContext.getUserPrincipal().getName();
  }

  @GET
  @Produces(MediaType.APPLICATION_JSON)
  @Path("/facets")
  public Response getFacetValuesNew(@QueryParam("text") String queryText,
                                 @QueryParam("facetFields") String facetFields,
                                 @QueryParam("startTime") Long startTime,
                                 @QueryParam("endTime") Long endTime,
                                 @Context SecurityContext securityContext) {
    if (StringUtils.isEmpty(facetFields)) {
      return Response.status(Response.Status.BAD_REQUEST).entity("'facetField' query parameter is required.").build();
    }

    String ifacetFields = SanitizeUtility.sanitizeQuery(facetFields);
    Set<String> facetFieldSets = extractFacetFields(ifacetFields);

    String iQueryText = SanitizeUtility.sanitizeQuery(queryText);
    Long iStartTime = SanitizeUtility.sanitizeStartTime(startTime, endTime);
    Long iEndTime = SanitizeUtility.sanitizeEndTime(startTime, endTime);

    facetFieldSets = filterFacetable(HiveQueryBasicInfo.TABLE_INFORMATION, facetFieldSets);

    Optional<List<FacetValue>> facetValueList = repository.getFacetValues(facetFieldSets, iQueryText, iStartTime, iEndTime,
        getEffectiveUser(securityContext), dasConfig.getConf(QP_FACETS_RESULT_LIMIT));

    Map<String, Object> response = ImmutableMap.of("facets", facetValueList.get());
	return Response.ok(response).build();
  }

  private Set<String> extractFacetFields(String facetFieldsText) {
    return Arrays.stream(facetFieldsText.split(",")).map(String::trim).collect(Collectors.toSet());
  }

  private Set<String> filterFacetable(EntityTable table, Set<String> facetFields) {
    Stream<EntityField> firstFacetableFields = table.getFields().stream().filter(x -> x.isFacetable());
    Set<String> facetableFields = firstFacetableFields.map(EntityField::getDbFieldName).collect(Collectors.toSet());

    return Sets.intersection(facetFields, facetableFields);
  }
}
