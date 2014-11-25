package com.cloudera.hue.sparker.server.resources;

import com.cloudera.hue.sparker.server.sessions.Cell;
import com.cloudera.hue.sparker.server.sessions.ClosedSessionException;
import com.cloudera.hue.sparker.server.sessions.Session;
import com.cloudera.hue.sparker.server.sessions.SessionManager;
import com.codahale.metrics.annotation.Timed;
import com.sun.jersey.core.spi.factory.ResponseBuilderImpl;
import org.hibernate.validator.constraints.NotEmpty;

import javax.validation.Valid;
import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeoutException;

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
        return Collections.list(sessionManager.getSessionIds());
    }

    @POST
    @Timed
    public String createSession(@QueryParam("lang") String language) throws IOException, InterruptedException {
        int sessionType;

        if (language == null) {
            Response resp = new ResponseBuilderImpl().status(400).entity("missing language").build();
            throw new WebApplicationException(resp);
        }

        if (language.equals(SCALA)) {
            sessionType = SessionManager.SCALA;
        } else if (language.equals(PYTHON)) {
            sessionType = SessionManager.PYTHON;
        } else {
            Response resp = new ResponseBuilderImpl().status(400).entity("invalid language").build();
            throw new WebApplicationException(resp);
        }

        Session session = sessionManager.create(sessionType);

        return session.getId();
    }

    @Path("/{id}")
    @GET
    @Timed
    public List<Cell> getSession(@PathParam("id") String id,
                                 @QueryParam("from") Integer fromCell,
                                 @QueryParam("limit") Integer limit) throws SessionManager.SessionNotFound {
        Session session = sessionManager.get(id);
        List<Cell> cells = session.getCells();

        if (fromCell != null || limit != null) {
            if (fromCell == null) {
                fromCell = 0;
            }

            if (limit == null) {
                limit = cells.size();
            }

            cells = cells.subList(fromCell, fromCell + limit);
        }

        return cells;
    }

    @Path("/{id}")
    @POST
    @Timed
    public Cell executeStatement(@PathParam("id") String id, @Valid ExecuteStatementRequest request) throws Exception, ClosedSessionException, SessionManager.SessionNotFound {
        Session session = sessionManager.get(id);
        return session.executeStatement(request.getStatement());
    }

    @Path("/{id}")
    @DELETE
    @Timed
    public Response closeSession(@PathParam("id") String id) throws InterruptedException, TimeoutException, IOException, SessionManager.SessionNotFound {
        sessionManager.close(id);
        return Response.noContent().build();
    }

    private class ExecuteStatementRequest {
        @NotEmpty
        private String statement;

        public ExecuteStatementRequest(String statement) {
            this.statement = statement;
        }

        public String getStatement() {
            return statement;
        }
    }
}
