package com.cloudera.hue.sparker.server;

import com.cloudera.hue.sparker.server.resources.SessionResource;
import com.cloudera.hue.sparker.server.sessions.SessionManager;
import com.sun.jersey.core.spi.factory.ResponseBuilderImpl;
import io.dropwizard.Application;
import io.dropwizard.setup.Bootstrap;
import io.dropwizard.setup.Environment;

import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;

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
        environment.jersey().register(new SessionManagerExceptionMapper());
    }

    private class SessionManagerExceptionMapper implements ExceptionMapper<SessionManager.SessionNotFound> {

        @Override
        public Response toResponse(SessionManager.SessionNotFound sessionNotFound) {
            return new ResponseBuilderImpl().status(404).entity("session not found").build();
        }
    }
}
