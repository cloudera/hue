package com.cloudera.hue.sparker.server;

import com.codahale.metrics.annotation.Timed;
import com.sun.jersey.api.Responses;
import com.sun.jersey.core.spi.factory.ResponseBuilderImpl;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import java.io.IOException;
import java.util.Collections;
import java.util.List;

@Path("/sessions")
@Produces(MediaType.APPLICATION_JSON)
public class SessionResource {

    private static final String SCALA = "scala";
    private static final String PYTHON = "python";

    private final SessionManager sessionManager;

    public SessionResource(SessionManager sessionManager) {
        this.sessionManager = sessionManager;
    }

    @GET
    @Timed
    public List<String> getSessions() {
        return Collections.list(sessionManager.getSessionKeys());
    }

    /*
    @GET
    @Timed
    public Session getSession()
    */

    @POST
    @Timed
    public String createSession(@QueryParam("lang") String language) throws IOException, InterruptedException {
        int sessionType;

        if (language.equals(SCALA)) {
            sessionType = SessionManager.SCALA;
        } else if (language.equals(PYTHON)) {
            sessionType = SessionManager.PYTHON;
        } else {
            Response resp = new ResponseBuilderImpl().status(400).entity("invalid language").build();
            throw new WebApplicationException(resp);
        }

        Session session = sessionManager.create(sessionType);

        return session.getKey();
    }

    @Path("/{id}")
    @GET
    @Timed
    public List<String> getSession(@PathParam("id") String id) {
        Session session = sessionManager.get(id);
        if (session == null) {
            Response resp = new ResponseBuilderImpl().status(404).entity("unknown session").build();
            throw new WebApplicationException(resp);
        }

        session.getOutputLines();
    }
}
