// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.filters;

import java.io.IOException;
import java.util.Arrays;
import java.util.Properties;

import javax.inject.Inject;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.commons.lang3.StringUtils;
import org.apache.hadoop.security.SecurityUtil;
import org.apache.hadoop.security.authentication.client.AuthenticationException;
import org.apache.hadoop.security.authentication.server.AuthenticationToken;
import org.apache.hadoop.security.authentication.server.KerberosAuthenticationHandler;

import com.cloudera.hue.querystore.common.config.AuthConfig;
import com.cloudera.hue.querystore.common.config.AuthConfig.UserAuth;
import com.cloudera.hue.querystore.common.security.KeyManager;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class SPNEGOFilter extends AuthFilter {

  private KerberosAuthenticationHandler authHandler;

  @Inject
  public SPNEGOFilter(AuthConfig authConfig, KeyManager keyManager) {
    super(authConfig, keyManager, null, UserAuth.KNOX_PROXY, UserAuth.SPNEGO);
  }

  @Override
  public void initAuthFilter() throws ServletException {
    verifyConfig();
    authHandler = new KerberosAuthenticationHandler("spnego");
    Properties config = new Properties();
    config.setProperty(KerberosAuthenticationHandler.KEYTAB, authConfig.getSpnegoKeytab());
    try {
      config.setProperty(KerberosAuthenticationHandler.PRINCIPAL,
          SecurityUtil.getServerPrincipal(authConfig.getSpnegoPrincipal(), "0.0.0.0"));
    } catch (IOException e) {
      throw new ServletException("Unable to create server principal: ", e);
    }
    if (!StringUtils.isEmpty(authConfig.getNameRules())) {
      config.setProperty(KerberosAuthenticationHandler.NAME_RULES, authConfig.getNameRules());
    }
    authHandler.init(config);
  }

  private void verifyConfig() throws ServletException {
    if (authConfig.getUserAuth() == UserAuth.KNOX_PROXY) {
      if (StringUtils.isEmpty(authConfig.getDoAsParamName())) {
        throw new ServletException("Please configure doAs param name");
      }
      if (StringUtils.isEmpty(authConfig.getKnoxUser())) {
        throw new ServletException("Please configure knox user");
      }
    }
    if (authConfig.getUserAuth() == UserAuth.KNOX_PROXY ||
        authConfig.getUserAuth() == UserAuth.SPNEGO) {
      if (StringUtils.isEmpty(authConfig.getSpnegoKeytab())) {
        throw new ServletException("Please configure spnego keytab");
      }
      if (StringUtils.isEmpty(authConfig.getSpnegoPrincipal())) {
        throw new ServletException("Please configure spnego keytab");
      }
      // name rules is optional.
    }
  }

  @Override
  public String authenticate(HttpServletRequest request, HttpServletResponse response)
      throws IOException, ServletException {
    AuthenticationToken token;
    try {
      token = authHandler.authenticate(request, response);
      if (token == null) {
        return null;
      }
    } catch (AuthenticationException e) {
      log.error("Error authenticating: ", e);
      response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "Internal error");
      return null;
    }
    String username = token.getUserName();
    if (username != null) {
      log.debug("Spnego user: {}", username);
      if (authConfig.getUserAuth() == UserAuth.KNOX_PROXY &&
          username.equals(authConfig.getKnoxUser())) {
        String[] values = request.getParameterValues(authConfig.getDoAsParamName());
        if (values == null || values.length != 1) {
          String strVals = Arrays.toString(values);
          log.warn("Invalid doAs request: {}, {}", authConfig.getDoAsParamName(), strVals);
          response.sendError(HttpServletResponse.SC_BAD_REQUEST, "Invalid doAs: " + strVals);
          return null;
        }
        username = values[0];
      }
    } else {
      log.error("Unexpected token without username");
      response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "Error: Invalid token from auth handler.");
    }
    return username;
  }

  @Override
  public void destroyAuthFilter() {
    if (authHandler != null) {
      authHandler.destroy();
    }
  }
}
