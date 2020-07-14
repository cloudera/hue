// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.util;

import java.nio.file.Paths;

import org.junit.Assert;
import org.junit.Test;

public class CredentialProviderTest {
  private static final String JCEKS_PATH = getCredentialProviderPath();

  protected static String getCredentialProviderPath() {
    String cwd = Paths.get(".").toAbsolutePath().normalize().toString();
    return "jceks://file" + cwd + "/src/test/resources/das_test.jceks";
  }

  @Test
  public void getPassword() throws Exception {
    CredentialProvider credentialProvider = new CredentialProvider(JCEKS_PATH);
    String pswd = credentialProvider.getPassword("data_analytics_studio_database_password");
    Assert.assertEquals(pswd, "testDBPswd");
  }
}