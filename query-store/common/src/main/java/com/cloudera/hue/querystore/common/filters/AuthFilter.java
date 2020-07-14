// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.filters;

import java.io.IOException;
import java.util.EnumSet;
import java.util.List;

import javax.servlet.Filter;
import javax.servlet.FilterChain;
import javax.servlet.FilterConfig;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import com.cloudera.hue.querystore.common.config.AuthConfig;
import com.cloudera.hue.querystore.common.config.AuthConfig.UserAuth;
import com.cloudera.hue.querystore.common.security.AuthCookieService;
import com.cloudera.hue.querystore.common.security.KeyManager;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public abstract class AuthFilter implements Filter {
  protected final AuthConfig authConfig;
  protected final KeyManager keyManager;
  private final List<String> ignorePaths;
  private final EnumSet<UserAuth> filterUserAuth;
  private AuthCookieService authCookieService;

  protected AuthFilter(AuthConfig authConfig, KeyManager keyManager, List<String> ignorePaths, UserAuth first,
      UserAuth... rest) {
    this.authConfig = authConfig;
    this.keyManager = keyManager;

    this.ignorePaths = ignorePaths;
    this.filterUserAuth = EnumSet.of(first, rest);
  }

  @Override
  public final void init(FilterConfig filterConfig) throws ServletException {
    this.authCookieService = new AuthCookieService(authConfig.getDasJWTCookieName(), keyManager.getPublicKey(),
        keyManager.getPrivateKey());

    if (filterUserAuth.contains(authConfig.getUserAuth())) {
      initAuthFilter();
    }
  }

  protected void initAuthFilter() throws ServletException {
  }

  @Override
  public final void destroy() {
    if (filterUserAuth.contains(authConfig.getUserAuth())) {
      destroyAuthFilter();
    }
  }

  protected void destroyAuthFilter() {
  }

  @Override
  public final void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain)
      throws IOException, ServletException {
    HttpServletRequest httpRequest = (HttpServletRequest) servletRequest;
    HttpServletResponse httpResponse = (HttpServletResponse) servletResponse;
    HttpSession session = httpRequest.getSession();
    String username;

    // Wrong auth type or user is already authenticated.
    if (!filterUserAuth.contains(authConfig.getUserAuth()) ||
        session.getAttribute(RequestContextFilter.SESSION_USER_KEY) != null) {
      filterChain.doFilter(servletRequest, servletResponse);
      return;
    }

    // Check if JWT token has not expired and have a valid user name.
    username = authCookieService.getUser(httpRequest);
    if (username != null) {
      // If username is missing in session add it
      setSessionUser(session, username);
      filterChain.doFilter(servletRequest, servletResponse);
      return;
    }

    if (ignorePaths != null) {
      String pathInfo = httpRequest.getPathInfo();
      for (String path : ignorePaths) {
        if (pathInfo.startsWith(path)) {
          filterChain.doFilter(servletRequest, servletResponse);
          return;
        }
      }
    }

    log.debug("In filter for authType: {}", filterUserAuth);
    username = authenticate(httpRequest, httpResponse);
    log.debug("Final user for filter: {}, {}", filterUserAuth, username);
    if (username != null) {
      authCookieService.setUser(httpResponse, username, session.getMaxInactiveInterval());
      setSessionUser(session, username);
      filterChain.doFilter(httpRequest, httpResponse);
    }
    // assume that the authenticate has done the necessary redirects, no filterChain.doFilter.
  }

  private void setSessionUser(HttpSession session, String username) {
    synchronized (session) {
      if (session.getAttribute(RequestContextFilter.SESSION_USER_KEY) == null) {
        session.setAttribute(RequestContextFilter.SESSION_USER_KEY, username);
      }
    }
  }

  public abstract String authenticate(HttpServletRequest request, HttpServletResponse response)
      throws IOException, ServletException;
}
