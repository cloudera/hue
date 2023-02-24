package com.cloudera.hue.querystore.eventProcessor.resources;

import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.SecurityContext;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.dto.QuerySearchParams;
import com.cloudera.hue.querystore.common.dto.QuerySearchResult;
import com.cloudera.hue.querystore.common.entities.ImpalaQueryEntity;
import com.cloudera.hue.querystore.common.repository.ImpalaQueryRepository;
import com.cloudera.hue.querystore.common.services.QuerySearchParamsUtils;
import com.cloudera.hue.querystore.eventProcessor.lifecycle.ImpalaEventProcessorManager;

import javax.inject.Inject;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@Path("/impala")
public class ImpalaResource {
  private final ImpalaEventProcessorManager impalaEventProcessorManager;
  private final ImpalaQueryRepository impalaQueryRepo;
  private final AppAuthentication appAuth;

  @Inject
  public ImpalaResource(
    ImpalaEventProcessorManager impalaEventProcessorManager,
    ImpalaQueryRepository impalaQueryRepo,
    AppAuthentication appAuth
  ) {
    this.impalaEventProcessorManager = impalaEventProcessorManager;
    this.impalaQueryRepo = impalaQueryRepo;
    this.appAuth = appAuth;
  }

  /**
  * Gets a list of matching queries
  */
  @POST
  @Produces(MediaType.APPLICATION_JSON)
  @Path("/queries")
  public Response searchQueries(QuerySearchParams params, @Context SecurityContext securityContext) {
    impalaEventProcessorManager.forceRefresh();

    QuerySearchParams searchParams = QuerySearchParamsUtils.standardize(params);
    String userName = securityContext.getUserPrincipal().getName();
    AppAuthentication.Role role = appAuth.getRole(userName);

    QuerySearchResult<ImpalaQueryEntity> result = new QuerySearchResult<ImpalaQueryEntity>(
      impalaQueryRepo.search(searchParams, userName, role),
      impalaQueryRepo.getSearchSize(searchParams, userName, role),
      searchParams,
      impalaEventProcessorManager.getQueryRefreshTime()
    );
    return Response.ok(result).build();
  }
}
