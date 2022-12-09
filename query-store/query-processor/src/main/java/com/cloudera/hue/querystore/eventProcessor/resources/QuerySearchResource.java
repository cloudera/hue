// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.resources;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

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
import com.cloudera.hue.querystore.common.dto.FacetValue;
import com.cloudera.hue.querystore.common.dto.FieldInformation;
import com.cloudera.hue.querystore.common.dto.HiveQueryDto;
import com.cloudera.hue.querystore.common.dto.SearchRequest;
import com.cloudera.hue.querystore.common.repository.PageData;
import com.cloudera.hue.querystore.common.services.SearchService;
import com.cloudera.hue.querystore.common.util.MetaInfo;
import com.cloudera.hue.querystore.common.util.Pair;
import com.cloudera.hue.querystore.eventProcessor.lifecycle.EventProcessorManager;
import com.google.common.collect.ImmutableMap;

import lombok.extern.slf4j.Slf4j;

/**
 * Resource class for working with the hive ide Udfs
 */
@Slf4j
@Path("/query")
public class QuerySearchResource {
  private static final int MAX_FACET_FIELDS_SEARCH_ALLOWED = 3;

  private final SearchService searchService;
  private final EventProcessorManager eventProcessorManager;

  @Inject
  public QuerySearchResource(SearchService searchService, EventProcessorManager eventProcessorManager) {
    this.searchService = searchService;
    this.eventProcessorManager = eventProcessorManager;
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

    long queryUpdateTime = eventProcessorManager.getQueryUpdateTime();
    PageData<HiveQueryDto> pageData = searchService.doBasicSearch(queryText, sortText, offset, limit,
      startTime, endTime, facets, rangeFacets, effectiveUser);

    MetaInfo metaInfo = MetaInfo.builder().fromPageData(pageData, queryUpdateTime).build();
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
  public Response getFacetValues(@QueryParam("text") String queryText,
                                 @QueryParam("facetFields") String facetFields,
                                 @QueryParam("startTime") Long startTime,
                                 @QueryParam("endTime") Long endTime,
                                 @Context SecurityContext securityContext) {
    if (StringUtils.isEmpty(facetFields)) {
      return Response.status(Response.Status.BAD_REQUEST).entity("'facetField' query parameter is required.").build();
    }
    Set<String> facetFieldSets = extractFacetFields(facetFields);
    if (facetFieldSets.size() > MAX_FACET_FIELDS_SEARCH_ALLOWED) {
      log.error("Max allowed facets to be queries is {}. Current queried fields is {}",
          MAX_FACET_FIELDS_SEARCH_ALLOWED, facetFieldSets.size());
      return Response.status(Response.Status.BAD_REQUEST).entity("Max allowed facets to be queries is " +
          MAX_FACET_FIELDS_SEARCH_ALLOWED + ". Current queried fields is " + facetFieldSets.size()).build();
    }
    Pair<List<FacetValue>, List<FacetValue>> facetsPair = searchService.getFacetValues(
        queryText, facetFieldSets, startTime, endTime, getEffectiveUser(securityContext));
    List<FacetValue> facets = facetsPair.getFirst();
    List<FacetValue> rangeFacets = facetsPair.getSecond();
    Map<String, Object> response = ImmutableMap.of("facets", facets, "rangeFacets", rangeFacets);
    return Response.ok(response).build();
  }

  private Set<String> extractFacetFields(String facetFieldsText) {
    return Arrays.stream(facetFieldsText.split(",")).map(String::trim).collect(Collectors.toSet());
  }
}
