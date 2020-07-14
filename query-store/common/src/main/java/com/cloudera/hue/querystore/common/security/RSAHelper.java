// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.security;

import java.io.ByteArrayInputStream;
import java.io.UnsupportedEncodingException;
import java.security.KeyFactory;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;

public class RSAHelper {

  private static final String ALG = "RSA";
  private static final String CERT_TYPE = "X.509";
  private static final String KEY_DELIM = "-----";

  public KeyPair generateKeyPair() {
    try {
      KeyPairGenerator generator = KeyPairGenerator.getInstance(ALG);
      generator.initialize(2048);
      return generator.generateKeyPair();
    } catch (NoSuchAlgorithmException e) {
      throw new RuntimeException("KeyPair generator failed", e);
    }
  }

  public String encodePublicKey(PublicKey publicKey) {
    X509EncodedKeySpec keySpecX509 = new X509EncodedKeySpec(publicKey.getEncoded());
    return Base64.getEncoder().encodeToString(keySpecX509.getEncoded());
  }

  public String encodePrivateKey(PrivateKey privateKey) {
    PKCS8EncodedKeySpec keySpecPKCS8 = new PKCS8EncodedKeySpec(privateKey.getEncoded());
    return Base64.getEncoder().encodeToString(keySpecPKCS8.getEncoded());
  }

  public String encodeKeyPair(KeyPair keyPair) {
    String encodedPublicKey = encodePublicKey(keyPair.getPublic());
    String encodedPrivateKey = encodePrivateKey(keyPair.getPrivate());
    return encodedPublicKey + KEY_DELIM + encodedPrivateKey;
  }

  private byte[] normalizeKey(String keyContent) {
    keyContent = keyContent.replaceAll("\\n", "");
    if (keyContent.contains(KEY_DELIM)) {
      keyContent = keyContent.split(KEY_DELIM)[2];
    }
    keyContent = keyContent.replaceAll("\\t", "").replaceAll(" ", "");
    return Base64.getDecoder().decode(keyContent);
  }

  public RSAPublicKey decodePublicKeyCertificate(String keyContent) {
    if (!keyContent.contains(KEY_DELIM)) {
      keyContent = "-----BEGIN CERTIFICATE-----\n" + keyContent + "\n-----END CERTIFICATE-----";
    }
    try {
      ByteArrayInputStream bis = new ByteArrayInputStream(keyContent.getBytes("UTF8"));
      X509Certificate cer = (X509Certificate)CertificateFactory.getInstance(CERT_TYPE).generateCertificate(bis);
      return (RSAPublicKey)cer.getPublicKey();
    } catch (UnsupportedEncodingException | CertificateException exp) {
      throw new RuntimeException("Public key certificate decoding failed", exp);
    }
  }

  public RSAPublicKey decodePublicKey(String encodedKey) {
    try {
      X509EncodedKeySpec keySpecX509 = new X509EncodedKeySpec(normalizeKey(encodedKey));
      return (RSAPublicKey) KeyFactory.getInstance(ALG).generatePublic(keySpecX509);
    } catch (NoSuchAlgorithmException | InvalidKeySpecException exp) {
      throw new RuntimeException("Public key decoding failed", exp);
    }
  }

  public RSAPrivateKey decodePrivateKey(String encodedKey) {
    try {
      PKCS8EncodedKeySpec keySpecPKCS8 = new PKCS8EncodedKeySpec(normalizeKey(encodedKey));
      return (RSAPrivateKey)KeyFactory.getInstance(ALG).generatePrivate(keySpecPKCS8);
    } catch (InvalidKeySpecException | NoSuchAlgorithmException exp) {
      throw new RuntimeException("Private key decoding failed", exp);
    }
  }

  public KeyPair decodeKeyPair(String encodedKeyPair) {
    String[] encodedKeys = encodedKeyPair.split(KEY_DELIM);
    if (encodedKeys.length != 2) {
      throw new RuntimeException("Invalid encoded KeyPair data!");
    }
    return new KeyPair(decodePublicKey(encodedKeys[0]), decodePrivateKey(encodedKeys[1]));
  }

}