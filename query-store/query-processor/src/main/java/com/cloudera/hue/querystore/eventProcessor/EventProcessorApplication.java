// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor;

import java.util.ArrayList;
import java.util.EnumSet;

import javax.servlet.DispatcherType;
import javax.servlet.Filter;
import javax.ws.rs.Priorities;

import org.eclipse.jetty.server.session.SessionHandler;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.jdbi.v3.core.Jdbi;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.config.AuthConfig;
import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.config.DasConfiguration.ConfVar;
import com.cloudera.hue.querystore.common.filters.RequestContextFilter;
import com.cloudera.hue.querystore.common.filters.SPNEGOFilter;
import com.cloudera.hue.querystore.common.module.CommonModule;
import com.cloudera.hue.querystore.common.resource.HealthCheckResource;
import com.cloudera.hue.querystore.common.util.PasswordSubstitutor;
import com.cloudera.hue.querystore.eventProcessor.bundle.DefaultFlywayBundle;
import com.cloudera.hue.querystore.eventProcessor.lifecycle.CleanupManager;
import com.cloudera.hue.querystore.eventProcessor.lifecycle.EventProcessorManager;
import com.cloudera.hue.querystore.eventProcessor.module.EventProcessorModule;
import com.cloudera.hue.querystore.eventProcessor.resources.AboutResource;
import com.cloudera.hue.querystore.eventProcessor.resources.BundleResource;
import com.cloudera.hue.querystore.eventProcessor.resources.HiveQueryResource;
import com.cloudera.hue.querystore.eventProcessor.resources.QuerySearchResource;
import com.cloudera.hue.querystore.eventProcessor.resources.AdminResource;
import com.codahale.metrics.jdbi3.InstrumentedSqlLogger;
import com.codahale.metrics.jdbi3.strategies.SmartNameStrategy;
import com.codahale.metrics.jmx.JmxReporter;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.google.inject.Guice;
import com.google.inject.Injector;

import io.dropwizard.Application;
import io.dropwizard.configuration.SubstitutingSourceProvider;
import io.dropwizard.jdbi3.JdbiFactory;
import io.dropwizard.jersey.DropwizardResourceConfig;
import io.dropwizard.jersey.setup.JerseyEnvironment;
import io.dropwizard.jetty.setup.ServletEnvironment;
import io.dropwizard.setup.Bootstrap;
import io.dropwizard.setup.Environment;

public class EventProcessorApplication extends Application<EventProcessorConfiguration> {

  private static final ConfVar<Integer> SESSION_TIMEOUT =
      new ConfVar<>("hue.query-processor.session-timeout-secs", 24 * 60 * 60); // 1 day default.
  private static final ConfVar<String> COOKIE_NAME =
      new ConfVar<>("hue.query-processor.session-cookie-name", "HUE_QP_SESSIONID");
  private static final ConfVar<Boolean> ENABLE_EVENT_PROCESSOR =
      new ConfVar<>("hue.query-processor.event-pipeline.enabled", true);
  private static final ConfVar<Boolean> ENABLE_REST_APIS =
      new ConfVar<>("hue.query-processor.rest-apis.enabled", true);

  @Override
  protected void bootstrapLogging() {
    //    to disable logback logging
  }

  public static void main(String[] args) throws Exception {
    new EventProcessorApplication().run(args);
  }

  @Override
  public String getName() {
    return "Hive Studio Event Processor";
  }

  @Override
  public void initialize(Bootstrap<EventProcessorConfiguration> bootstrap) {
    bootstrap.addBundle(new DefaultFlywayBundle());
    bootstrap.addCommand(new ProtoJsonConvertor());
    bootstrap.addCommand(new EventsCopier());
    bootstrap.getObjectMapper().disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    bootstrap.setConfigurationSourceProvider(
      new SubstitutingSourceProvider(bootstrap.getConfigurationSourceProvider(), new PasswordSubstitutor())
    );
  }

  @Override
  public void run(EventProcessorConfiguration configuration, Environment environment) throws Exception {
    AppAuthentication appAuthentication = new AppAuthentication(configuration.getAuthConfig());
    JdbiFactory factory = new JdbiFactory();
    Jdbi jdbi = factory.build(environment, configuration.getDatabase(), "postgresql");
    jdbi.setSqlLogger(new InstrumentedSqlLogger(environment.metrics(), new SmartNameStrategy()));

    JmxReporter reporter = JmxReporter.forRegistry(environment.metrics()).build();
    reporter.start();

    Injector injector = initializeGuice(configuration, environment, jdbi, appAuthentication);
    configureSessionHandler(environment, configuration.getDasConf());
    configureServletFilters(injector, environment, configuration, appAuthentication);
    configureResources(injector, environment, configuration.getDasConf());
    environment.jersey().setUrlPattern("/api/*");

    if (configuration.getDasConf().getConf(ENABLE_EVENT_PROCESSOR)) {
      EventProcessorManager eventProcessorManager = injector.getInstance(EventProcessorManager.class);
      environment.lifecycle().manage(eventProcessorManager);
      environment.lifecycle().manage(injector.getInstance(CleanupManager.class));
    }
  }

  private Injector initializeGuice(EventProcessorConfiguration configuration, Environment environment, Jdbi jdbi,
      AppAuthentication appAuth) {
    return Guice.createInjector(
        new CommonModule(jdbi, appAuth),
        new EventProcessorModule(configuration, environment)
    );
  }

  private void configureSessionHandler(Environment environment, DasConfiguration dasConfig) {
    SessionHandler sessionHandler = new SessionHandler();
    sessionHandler.setMaxInactiveInterval(dasConfig.getConf(SESSION_TIMEOUT));
    sessionHandler.setSessionCookie(dasConfig.getConf(COOKIE_NAME));
    environment.servlets().setSessionHandler(sessionHandler);
  }

  private void configureServletFilters(Injector injector, Environment environment, EventProcessorConfiguration config,
      AppAuthentication appAuth) {
    environment.jersey().register(new AbstractBinder() {
      @Override
      protected void configure() {
        bind(config.getAuthConfig()).to(AuthConfig.class);
        bind(appAuth).to(AppAuthentication.class);
      }
    });

    ServletEnvironment servlets = environment.servlets();

    // List of standard servlet filters to be installed.
    ArrayList<Class<? extends Filter>> filters = new ArrayList<>();
    filters.add(SPNEGOFilter.class);

    for (Class<? extends Filter> filter : filters) {
      servlets.addFilter(filter.getSimpleName(), injector.getInstance(filter))
          .addMappingForUrlPatterns(EnumSet.of(DispatcherType.REQUEST), true, "/*");
    }

    // Special jersey filter to setup security context.
    DropwizardResourceConfig resourceConfig = environment.jersey().getResourceConfig();
    resourceConfig.register(RequestContextFilter.class, Priorities.AUTHORIZATION + 1);
  }

  private void configureResources(Injector injector, Environment environment, DasConfiguration dasConfig) {
    JerseyEnvironment jersey = environment.jersey();
    jersey.register(new HealthCheckResource(environment.healthChecks()));
    jersey.register(injector.getInstance(AboutResource.class));
    if (dasConfig.getConf(ENABLE_REST_APIS)) {
      jersey.register(injector.getInstance(BundleResource.class));
      jersey.register(injector.getInstance(HiveQueryResource.class));
      jersey.register(injector.getInstance(QuerySearchResource.class));
      jersey.register(injector.getInstance(AdminResource.class));
    }
  }
}
