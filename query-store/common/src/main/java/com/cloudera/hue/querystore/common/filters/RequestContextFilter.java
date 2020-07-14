// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.filters;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import javax.ws.rs.container.ContainerRequestContext;
import javax.ws.rs.container.ContainerRequestFilter;
import javax.ws.rs.core.Context;
import javax.ws.rs.ext.Provider;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.resource.RequestContext;

import lombok.extern.slf4j.Slf4j;

/**
 * Jersey filter to extract the context information from the request and create the context object.
 */
@Provider
@Slf4j
public class RequestContextFilter implements ContainerRequestFilter {
  public static final String REQUEST_CONTEXT_PROPERTY_NAME = "REQUEST-CONTEXT";
  public static final String SESSION_USER_KEY = "user";

  @Context
  private HttpServletRequest servletRequest;

  @Context
  private AppAuthentication appAuth;

  @Override
  public void filter(ContainerRequestContext containerRequestContext) {
    String username = null;
    boolean secure = true;

    HttpSession session = servletRequest.getSession(false);
    if (session != null) {
      username = (String)session.getAttribute(SESSION_USER_KEY);
    }

    if (username == null) {
      username = appAuth.getAppUser();
    }

    if (username == null) {
      log.error("Username not configured, assuming hive user, things might break badly");
      username = "hive";
      secure = false;
    }

    log.debug("Final username: {}", username);
    RequestContext context = new RequestContext(username, appAuth.getRole(username), secure);
    containerRequestContext.setSecurityContext(context);
  }
}
