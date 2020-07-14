// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor;

import java.util.List;

import javax.validation.Valid;

import com.cloudera.hue.querystore.common.config.AuthConfig;
import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.fasterxml.jackson.annotation.JsonProperty;

import io.dropwizard.Configuration;
import io.dropwizard.client.JerseyClientConfiguration;
import io.dropwizard.db.DataSourceFactory;
import io.dropwizard.flyway.FlywayFactory;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
public class EventProcessorConfiguration extends Configuration {
  @Valid
  private DataSourceFactory database = null;

  private FlywayFactory flyway = null;

  @Valid
  @JsonProperty("jerseyClient")
  private JerseyClientConfiguration jerseyClientConfiguration;

  @Valid
  private DasConfiguration dasConf = null;

  @Valid
  private AuthConfig authConfig = null;

  @Valid
  private String credentialProviderPath = null;

  @Valid
  private List<String> passwordAliases = null;
}
