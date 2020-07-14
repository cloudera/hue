// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.util;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;

import org.apache.hadoop.io.IOUtils;
import org.junit.Assert;
import org.junit.Test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class PasswordSubstitutorTest {
  protected static String JSON_FILE_PATH = "das-app.json";

  @Test
  public void replace() throws Exception {
    PasswordSubstitutor passwordSubstitutor = new PasswordSubstitutor();
    String jsonString;
    try (InputStream in = PasswordSubstitutorTest.class.getClassLoader().getResourceAsStream(JSON_FILE_PATH)) {
      ByteArrayOutputStream out = new ByteArrayOutputStream(4096);
      IOUtils.copyBytes(in, out, 8192);
      jsonString = new String(out.toByteArray());
    }

    String credentialProviderPath = CredentialProviderTest.getCredentialProviderPath();
    jsonString = jsonString.replace("{{das_credential_provider_paths}}", credentialProviderPath);

    jsonString = passwordSubstitutor.replace(jsonString);

    ObjectMapper mapper = new ObjectMapper();
    JsonNode json = mapper.readTree(jsonString);

    Assert.assertEquals("testDBPswd", json.path("database").path("password").asText());
    Assert.assertEquals("testWebappPswd", json.path("server").path("applicationConnectors").get(0)
        .get("keyStorePassword").asText());
    Assert.assertEquals("testWebappPswd", json.path("server").path("adminConnectors").get(0)
        .get("keyStorePassword").asText());
    Assert.assertEquals("", json.path("noPasswordAlias").asText());
  }
}