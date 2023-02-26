// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.resources;
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
import com.cloudera.hue.querystore.common.dto.QuerySearchParams;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.services.StandardizeParamsUtility;
import com.cloudera.hue.querystore.common.services.SearchService;
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

  private final HiveQueryBasicInfoRepository repository;
  private final DasConfiguration dasConfig;
  private AppAuthentication appAuth;
  private HiveQueryResource hiveQueryResource;

  @Inject
  public QuerySearchResource(HiveQueryBasicInfoRepository repository,
        DasConfiguration dasConfig, AppAuthentication appAuth,
        HiveQueryResource hiveQueryResource) {
    this.repository = repository;
    this.dasConfig = dasConfig;
    this.appAuth = appAuth;
    this.hiveQueryResource = hiveQueryResource;
  }

  public static class QuerySearchParamsWrapper {
    private QuerySearchParams params;
    public QuerySearchParamsWrapper() { }

    public QuerySearchParamsWrapper(QuerySearchParams params) {
      this.params = params;
    }

    public QuerySearchParams getParams() {
      return params;
    }

    public void setSearch(QuerySearchParams params) {
      this.params = params;
    }
  }

  /**
   * Gets a list of query matching the basic search
   */
  @POST
  @Produces(MediaType.APPLICATION_JSON)
  @Path("/search")
  public Response getBasicSearchedQueriesWithFacets(QuerySearchParamsWrapper request, @Context SecurityContext securityContext) {
    return hiveQueryResource.getSearchedQueries(request.getParams(), securityContext);
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
  public Response getFacetValuesNew(@QueryParam("facetFields") String facetFields,
                                 @QueryParam("startTime") Long startTime,
                                 @QueryParam("endTime") Long endTime,
                                 @Context SecurityContext securityContext) {
    if (StringUtils.isEmpty(facetFields)) {
      return Response.status(Response.Status.BAD_REQUEST).entity("'facetField' query parameter is required.").build();
    }

    String ifacetFields = StandardizeParamsUtility.sanitizeQuery(facetFields);

    Long iStartTime = StandardizeParamsUtility.sanitizeStartTime(startTime, endTime);
    Long iEndTime = StandardizeParamsUtility.sanitizeEndTime(startTime, endTime);

    Set<String> facetFieldSets = filterFacetable(HiveQueryBasicInfo.TABLE_INFORMATION, ifacetFields);

    String userName = getEffectiveUser(securityContext);

    Optional<List<FacetValue>> facetValueList = repository.getFacetValues(facetFieldSets, iStartTime, iEndTime,
        userName, appAuth.getRole(userName), dasConfig.getConf(QP_FACETS_RESULT_LIMIT));

    Map<String, Object> response = ImmutableMap.of("facets", facetValueList.get());
	return Response.ok(response).build();
  }

  private Set<String> filterFacetable(EntityTable table, String ifacetFields) {
    Set<String> inputFacetFields = Arrays.stream(ifacetFields.split(",")).map(String::trim).collect(Collectors.toSet());

    Stream<EntityField> firstFacetableFields = table.getFields().stream().filter(x -> x.isFacetable());
    Set<String> facetableFields = firstFacetableFields.map(EntityField::getDbFieldName).collect(Collectors.toSet());

    return Sets.intersection(inputFacetFields, facetableFields);
  }
}
