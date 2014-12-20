package com.cloudera.hue.livy.server;

import com.cloudera.hue.livy.server.sessions.SessionManager;
import com.cloudera.hue.livy.server.resources.StatementResource;
import com.cloudera.hue.livy.server.resources.SessionResource;
import com.sun.jersey.core.spi.factory.ResponseBuilderImpl;
import io.dropwizard.Application;
import io.dropwizard.setup.Bootstrap;
import io.dropwizard.setup.Environment;

import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;

public class LivyApp extends Application<LivyConfiguration> {

    public static void main(String[] args) throws Exception {
        new LivyApp().run(args);
    }

    @Override
    public void initialize(Bootstrap<LivyConfiguration> bootstrap) {

    }

    @Override
    public void run(LivyConfiguration livyConfiguration, Environment environment) throws Exception {
        final SessionManager sessionManager = new SessionManager();
        environment.jersey().register(new SessionResource(sessionManager));
        environment.jersey().register(new StatementResource(sessionManager));
        environment.jersey().register(new SessionManagerExceptionMapper());
    }

    private class SessionManagerExceptionMapper implements ExceptionMapper<SessionManager.SessionNotFound> {

        @Override
        public Response toResponse(SessionManager.SessionNotFound sessionNotFound) {
            return new ResponseBuilderImpl().status(404).entity("session not found").build();
        }
    }
}
