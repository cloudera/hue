// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.config;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class AuthConfig {
  public enum UserAuth {
    NONE,
    KNOX_SSO,
    KNOX_PROXY,
    LDAP,
    SPNEGO,
    SAML;
  }
  public enum ServiceAuth {
    NONE,
    KERBEROS;
  }

  // authorization modes
  public enum AuthorizationMode{
    NONE,
    RANGER
  }

  private UserAuth userAuth;
  private ServiceAuth serviceAuth;

  private String appUserName;
  private String adminUsers;
  private String adminGroups;

  private AuthorizationMode authorizationMode;// it can be "NONE" or "RANGER"

  private String dasJWTCookieName;
  private String publicKey;
  private String privateKey;

  // For service kerberos auth.
  private String serviceKeytab;
  private String servicePrincipal;

  // knox sso config
  private String knoxSSOUrl;
  private String knoxSSOutUrl;
  private String knoxPublicKey;
  private String knoxCookieName;
  private String knoxUrlParamName;
  private String knoxUserAgent;

  // ldap auth config
  private String ldapUrl;
  private String ldapGuidKey;
  private String ldapBasedn;
  private String ldapDomain;
  private String ldapCustomLdapQuery;
  private String ldapUserMemebershipKey;
  private String ldapUserDNPattern;
  private String ldapUserFilter;
  private String ldapGroupClassKey;
  private String ldapGroupMemebershipKey;
  private String ldapGroupDNPattern;
  private String ldapGroupFilter;

  // spnego/knox_proxy config.
  private String spnegoPrincipal;
  private String spnegoKeytab;
  private String nameRules;

  // knox_proxy config
  private String knoxUser;
  private String doAsParamName;

  // saml config
  private String samlPropertiesFile;
  private String samlIdpMetadataFile;
  private String samlKeyStoreFile;
  private String samlKeyStorePassword;
  private String samlKeyStoreAlias;
  private String samlKeyStoreAliasPassword;

  public boolean isUserAuthEnabled() {
    return userAuth != UserAuth.NONE;
  }
}
