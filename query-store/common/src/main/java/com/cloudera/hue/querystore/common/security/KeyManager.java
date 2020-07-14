// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.security;

import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;

import javax.inject.Inject;
import javax.inject.Singleton;

import com.cloudera.hue.querystore.common.config.AuthConfig;

import lombok.Getter;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class KeyManager {

  private static final RSAHelper rsaHelper = new RSAHelper();

  @Getter
  private RSAPublicKey publicKey = null;
  @Getter
  private RSAPrivateKey privateKey = null;

  @Inject
  public KeyManager(AuthConfig authConfig) {
    log.info("Initializing Key Manager:");

    if (authConfig.getPublicKey() != null) {
      publicKey = rsaHelper.decodePublicKey(authConfig.getPublicKey());
      log.info("Public Key initialized. Key hash : {}", authConfig.getPublicKey().hashCode());
    }
    if (authConfig.getPrivateKey() != null) {
      privateKey = rsaHelper.decodePrivateKey(authConfig.getPrivateKey());
      log.info("Private Key initialized. Key hash : {}", authConfig.getPrivateKey().hashCode());
    }

    log.info("Key Manager initialization complete.");
  }

}
