package com.cloudera.hue.sparker.server;

import io.dropwizard.Application;
import io.dropwizard.setup.Bootstrap;
import io.dropwizard.setup.Environment;

public class SparkerApp extends Application<SparkerConfiguration> {

    public static void main(String[] args) throws Exception {
        new SparkerApp().run(args);
    }

    @Override
    public void initialize(Bootstrap<SparkerConfiguration> bootstrap) {

    }

    @Override
    public void run(SparkerConfiguration sparkerConfiguration, Environment environment) throws Exception {
        final SessionManager sessionManager = new SessionManager();
        final SessionResource resource = new SessionResource(sessionManager);
        environment.jersey().register(resource);
    }
}
