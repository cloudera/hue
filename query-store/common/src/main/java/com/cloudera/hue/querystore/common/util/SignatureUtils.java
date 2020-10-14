// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.util;

import java.util.UUID;

import javax.ws.rs.core.SecurityContext;

import org.apache.commons.codec.digest.DigestUtils;

public class SignatureUtils {

  private static String DELIM = ":";
  private static String SECRET_KEY = UUID.randomUUID() + DELIM;

  public static String generate(String data) {
    return DigestUtils.sha256Hex(SECRET_KEY + data);
  }

  public static String generate(String data, SecurityContext securityContext) {
    return generate(securityContext.getUserPrincipal().getName() + DELIM + data);
  }

}
