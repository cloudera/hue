package com.cloudera.hue.querystore.eventProcessor.resources;

import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
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
import com.cloudera.hue.querystore.eventProcessor.eventdefs.ImpalaQueryProfile;
import com.cloudera.hue.querystore.eventProcessor.lifecycle.ImpalaEventProcessorManager;

import javax.inject.Inject;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

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
  @Path("/queries")
  @Produces(MediaType.APPLICATION_JSON)
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

  //TODO: Move to a generic location
  private boolean userCheck(ImpalaQueryEntity query, SecurityContext securityContext) {
    String user = query.getUserName();
    return (securityContext.isUserInRole(AppAuthentication.Role.ADMIN.name())
        || (user != null && user.equals(securityContext.getUserPrincipal().getName())));
  }

  /**
   * Gets single query for the current user
   */
  @GET
  @Produces(MediaType.APPLICATION_JSON)
  @Path("/queries/{queryId}")
  public Response getQuery(@PathParam("queryId") String queryId, @Context SecurityContext securityContext) {
    Optional<ImpalaQueryEntity> queryOpt = impalaQueryRepo.findByQueryId(queryId);
    if (queryOpt.isPresent()) {
      ImpalaQueryEntity query = queryOpt.get();
      if (!userCheck(query, securityContext)) {
        return Response.status(Response.Status.UNAUTHORIZED).build();
      }

      ImpalaQueryProfile profile = impalaEventProcessorManager.loadProfile(query);

      Map<String, Object> response = new HashMap<>();
      response.put("query", query);
      response.put("profile", profile);
      return Response.ok(response).build();
  } else {
      return Response.status(Response.Status.NOT_FOUND).entity("Impala Query with id '" + queryId + "' not found").build();
    }
  }
}
