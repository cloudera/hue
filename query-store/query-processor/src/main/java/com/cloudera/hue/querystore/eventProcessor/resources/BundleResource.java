// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.resources;

import java.io.IOException;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;

import javax.inject.Inject;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.SecurityContext;
import javax.ws.rs.core.StreamingOutput;

import com.cloudera.hue.debugBundler.BundlerService;
import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;

import lombok.extern.slf4j.Slf4j;

/**
 * Resource to get the search information for the database
 */
@Slf4j
@Path("data-bundle")
public class BundleResource {
  private static final AtomicLong COUNTER = new AtomicLong();

  private final BundlerService bundlerService;
  private final HiveQueryBasicInfoRepository hiveQueryRepo;

  @Inject
  public BundleResource(BundlerService bundlerService, HiveQueryBasicInfoRepository hiveQueryRepo) {
    this.bundlerService = bundlerService;
    this.hiveQueryRepo = hiveQueryRepo;
  }

  private boolean userCheck(String queryID, SecurityContext securityContext) {
    if (securityContext.isUserInRole(AppAuthentication.Role.ADMIN.name())) {
      return true;
    }

    String userName = securityContext.getUserPrincipal().getName();
    if (userName == null || userName.isEmpty()) {
      return false;
    }

    Optional<HiveQueryBasicInfo> hiveQuery = hiveQueryRepo.findByHiveQueryId(queryID);
    if (hiveQuery.isPresent()) {
      return userName.equals(hiveQuery.get().getRequestUser());
    } else {
      return false;
    }
  }

  @GET
  @Path("/{id}")
  @Produces(MediaType.APPLICATION_JSON)
  public Response get(@PathParam("id") String queryID, @Context SecurityContext securityContext) throws IOException {
    String userName = securityContext.getUserPrincipal().getName();
    if (!userCheck(queryID, securityContext)) {
      log.error("User check failed: {}", securityContext);
      return Response.status(Response.Status.UNAUTHORIZED).build();
    }

    String fileSuffix = String.format("%s-%d", userName, COUNTER.incrementAndGet());
    String fileName = bundlerService.constructFileName(queryID, fileSuffix);
    StreamingOutput zipStream = bundlerService.streamBundle(queryID, userName);

    return Response.ok(zipStream, MediaType.APPLICATION_OCTET_STREAM)
      .header("Content-Disposition", "attachment; filename=\"" + fileName + "\"" )
      .build();
  }
}
