// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.filters;

import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerRequestFilter;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.Provider;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.resource.RequestContext;
import com.google.gson.JsonObject;

import lombok.extern.slf4j.Slf4j;

/**
 * Jersey filter to extract the context information from the request and create the context object.
 */
@Provider
@Slf4j
public class RequestContextFilter implements ContainerRequestFilter {
  public static final String SESSION_USER_KEY = "user";
  public static final String DO_AS_HEADER = "x-do-as";

  @Context
  private HttpServletRequest servletRequest;

  @Context
  private AppAuthentication appAuth;

  @Override
  public void filter(ContainerRequestContext containerRequestContext){
    String username = null;
    boolean secure = true;

    username = servletRequest.getHeader(DO_AS_HEADER);

    if (username == null) {
      String errorMsg = "Invalid request: x-do-as header is missing";
      log.error(errorMsg);

      JsonObject jsonResponse = new JsonObject();
      jsonResponse.addProperty("message", errorMsg);
      containerRequestContext.abortWith(Response.status(Response.Status.BAD_REQUEST)
          .entity(jsonResponse.toString()).build());
      return;
    }

    log.debug("Final username: {}", username);
    RequestContext context = new RequestContext(username, appAuth.getRole(username), secure);
    containerRequestContext.setSecurityContext(context);
  }
}
