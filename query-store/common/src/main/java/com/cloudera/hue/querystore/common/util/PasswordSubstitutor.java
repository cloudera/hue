// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.util;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang.StringUtils;
import org.apache.commons.text.StringSubstitutor;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.HashMap;

@Slf4j
public class PasswordSubstitutor extends StringSubstitutor {
  public String replace(String source) {
    ObjectMapper mapper = new ObjectMapper();
    try {
      JsonNode node = mapper.readTree(source);
      String providerPath = node.get("credentialProviderPath").textValue();
      if (!StringUtils.isEmpty(providerPath)) {
        CredentialProvider credentialProvider = new CredentialProvider(providerPath);
        HashMap<String, String> valueMap = new HashMap<>();
        for (JsonNode passwordAlias : node.get("passwordAliases")) {
          String alias = passwordAlias.textValue();
          String password = credentialProvider.getPassword(alias);
          password = StringUtils.isEmpty(password) ? "" : password.trim();
          valueMap.put(alias, password);
        }
        source = StringSubstitutor.replace(source, valueMap);
      }
    } catch(IOException e) {
      log.error("Password replace failed", e);
    }
    return source;
  }
}
