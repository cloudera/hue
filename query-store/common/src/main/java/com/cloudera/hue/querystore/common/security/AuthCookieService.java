// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.security;

import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.text.ParseException;
import java.util.Date;

import javax.servlet.ServletException;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.nimbusds.jose.JOSEException;
import com.nimbusds.jose.JWSAlgorithm;
import com.nimbusds.jose.JWSHeader;
import com.nimbusds.jose.JWSObject;
import com.nimbusds.jose.JWSSigner;
import com.nimbusds.jose.JWSVerifier;
import com.nimbusds.jose.crypto.RSASSASigner;
import com.nimbusds.jose.crypto.RSASSAVerifier;
import com.nimbusds.jwt.JWTClaimsSet;
import com.nimbusds.jwt.SignedJWT;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class AuthCookieService {
  private static final String DEFAULT_COOKIE_NAME = "das-jwt";

  private final String cookieName;

  private JWSVerifier verifier = null;
  private JWSSigner signer = null;

  public AuthCookieService(String cookieName) {
    this.cookieName = cookieName == null ? DEFAULT_COOKIE_NAME : cookieName;
  }

  public AuthCookieService(String cookieName, RSAPublicKey publicKey, RSAPrivateKey privateKey) throws ServletException {
    this(cookieName);
    initRSA(publicKey, privateKey);
  }

  private void initRSA(RSAPublicKey publicKey, RSAPrivateKey privateKey) {
    if (publicKey != null) {
      this.verifier = new RSASSAVerifier(publicKey);
      log.info("Verifier initialized. Public key algorithm : {}", publicKey.getAlgorithm());
    }
    if (privateKey != null) {
      this.signer = new RSASSASigner(privateKey);
      log.info("Verifier initialized. Private key algorithm : {}", privateKey.getAlgorithm());
    }
  }

  public void reset(HttpServletResponse response) {
    addJWTCookie(response, "", 0);
  }

  public String getUser(HttpServletRequest request) {
    String serializedJWT = getJWTCookie(request);
    return extractJWTUser(serializedJWT);
  }

  public boolean setUser(HttpServletResponse response, String username, int secondsToLive) throws ServletException {
    if (signer != null) {
      String serializedJWT = generateCookieValue(username, secondsToLive);
      addJWTCookie(response, serializedJWT, secondsToLive);
      return true;
    }
    return false;
  }

  private void addJWTCookie(HttpServletResponse response, String serializedJWT, int secondsToLive) {
    Cookie cookie = new Cookie(cookieName, serializedJWT);
    cookie.setMaxAge(secondsToLive);
    response.addCookie(cookie);
    log.info("User cookie added Name: {} MaxAge: {} ValueHash: {}", cookieName, secondsToLive, serializedJWT.hashCode());
  }

  private String generateCookieValue(String username, int secondsToLive) throws ServletException {
    Date expDate = new Date(System.currentTimeMillis() + secondsToLive * 1000);

    JWTClaimsSet claimsSet = new JWTClaimsSet.Builder()
            .subject(username)
            .expirationTime(expDate)
            .build();

    SignedJWT signedJWT = new SignedJWT(new JWSHeader(JWSAlgorithm.RS256), claimsSet);
    try {
      signedJWT.sign(signer);
      return signedJWT.serialize();
    } catch (JOSEException e) {
      log.error("JWT Signing failed: {}", e);
      throw new ServletException(e);
    }
  }

  private String extractJWTUser(String serializedJWT) {
    if (serializedJWT != null) {
      try {
        SignedJWT jwtToken = SignedJWT.parse(serializedJWT);
        if (validateToken(jwtToken)) {
          String username = jwtToken.getJWTClaimsSet().getSubject();
          return (username == null || username.length() == 0) ? null : username;
        }
      } catch (ParseException e) {
        log.warn("Invalid jwt token: {}", serializedJWT, e);
      }
    }
    return null;
  }

  private String getJWTCookie(HttpServletRequest request) {
    Cookie[] cookies = request.getCookies();
    if (cookieName != null && cookies != null) {
      for (Cookie cookie : cookies) {
        if (cookieName.equals(cookie.getName())) {
          return cookie.getValue();
        }
      }
    }
    return null;
  }

  private boolean validateToken(SignedJWT jwtToken) {
    if (verifier != null && JWSObject.State.SIGNED == jwtToken.getState() && jwtToken.getSignature() != null) {
      try {
        if (jwtToken.verify(verifier)) {
          Date expires = jwtToken.getJWTClaimsSet().getExpirationTime();
          return (expires == null || new Date().before(expires));
        }
      } catch (ParseException | JOSEException e) {
        log.warn("Error while validating jwtToken", e);
      }
    }
    return false;
  }

}
