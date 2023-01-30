// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common;

import java.io.IOException;
import java.util.Collections;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import org.apache.hadoop.security.Groups;
import org.apache.hadoop.security.SecurityUtil;
import org.apache.hadoop.security.UserGroupInformation;

import com.cloudera.hue.querystore.common.config.AuthConfig;
import com.cloudera.hue.querystore.common.config.AuthConfig.ServiceAuth;
import com.google.common.collect.Sets;
import com.google.common.util.concurrent.ThreadFactoryBuilder;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class AppAuthentication {
  public enum Role {
    ADMIN,
    USER
  }

  private final String appUser;
  private final Set<String> adminUsers;
  private final Set<String> adminGroups;
  private final boolean overrideRoleToAdmin;

  public AppAuthentication(AuthConfig authConfig) throws IOException {
    UserGroupInformation ugi;
    if (authConfig.getServiceAuth() == ServiceAuth.KERBEROS) {
      String principal = SecurityUtil.getServerPrincipal(authConfig.getServicePrincipal(),
          "0.0.0.0");
      log.info("Trying to login as user: {}, using keytab: {}",
          principal, authConfig.getServiceKeytab());
      ugi = UserGroupInformation.loginUserFromKeytabAndReturnUGI(
          principal, authConfig.getServiceKeytab());
      UserGroupInformation.setLoginUser(ugi);
      log.info("Login succeeded as user: {}, name: {}", principal, ugi.getUserName());
      ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor(
          new ThreadFactoryBuilder().setDaemon(true).setNameFormat("TGT-refresher-%d").build());
      scheduler.scheduleWithFixedDelay(this::refresh, 300, 300, TimeUnit.SECONDS);
    } else {
      ugi = UserGroupInformation.getCurrentUser();
    }
    appUser = ugi.getShortUserName();
    adminUsers = convertToSet(authConfig.getAdminUsers());
    overrideRoleToAdmin = adminUsers.contains("*");
    adminGroups = convertToSet(authConfig.getAdminGroups());
  }

  private Set<String> convertToSet(String string) {
    if (string == null || string.trim().isEmpty()) {
      return Collections.emptySet();
    }
    String[] admins =  string.toLowerCase().split(",");
    for (int i = 0; i < admins.length; ++i) {
      admins[i] = admins[i].trim();
    }
    return Sets.newHashSet(admins);
  }

  public String getAppUser() {
    return appUser;
  }

  public Role getRole(String user) {
    if (overrideRoleToAdmin || adminUsers.contains(user.toLowerCase())) {
      return Role.ADMIN;
    } else if (adminGroups.isEmpty()) {
      return Role.USER;
    }

    try {
      Set<String> groups = Groups.getUserToGroupsMappingService().getGroupsSet(user);
      for (String group : groups) {
        if (adminGroups.contains(group)) {
          return Role.ADMIN;
        }
      }
    } catch (IOException e) {
      log.warn("Error fetching group information for user: {}", user);
    }
    return Role.USER;
  }

  private void refresh() {
    try {
      UserGroupInformation.getLoginUser().checkTGTAndReloginFromKeytab();
    } catch (IOException e) {
      log.error("Error renewing token: ", e);
    }
  }
}
