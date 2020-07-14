// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.resource;

import java.security.Principal;

import javax.ws.rs.core.SecurityContext;

import com.cloudera.hue.querystore.common.AppAuthentication.Role;

import lombok.Value;

/**
 * Value object to hold the request context information
 */
@Value
public class RequestContext implements SecurityContext {
  private String username;
  private Role role;
  private boolean secure;

  private final Principal principal = new Principal() {
    @Override
    public String getName() {
      return username;
    }
  };

  @Override
  public Principal getUserPrincipal() {
    return principal;
  }

  @Override
  public boolean isUserInRole(String role) {
    return this.role.name().equals(role);
  }

  @Override
  public String getAuthenticationScheme() {
    return null;
  }
}
