// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.module;

import javax.inject.Singleton;
import javax.ws.rs.client.Client;

import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.eventProcessor.EventProcessorConfiguration;
import com.codahale.metrics.MetricRegistry;
import com.google.inject.AbstractModule;
import com.google.inject.Provides;

import io.dropwizard.client.JerseyClientBuilder;
import io.dropwizard.setup.Environment;

public class EventProcessorModule extends AbstractModule {
  private final EventProcessorConfiguration configuration;
  private final Environment environment;

  public EventProcessorModule(EventProcessorConfiguration configuration, Environment environment) {
    this.configuration = configuration;
    this.environment = environment;
  }

  @Override
  protected void configure() {
    bind(EventProcessorConfiguration.class).toInstance(configuration);
    bind(DasConfiguration.class).toInstance(configuration.getDasConf());
    bind(MetricRegistry.class).toInstance(environment.metrics());
  }

  @Singleton
  @Provides
  public Client provideJerseyClient() {
    final Client client = new JerseyClientBuilder(environment)
        .using(configuration.getJerseyClientConfiguration())
        .build(EventProcessorModule.class.getName());
    return client;
  }
}
