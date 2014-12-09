package com.cloudera.hue.sparker.server.resources;

import com.cloudera.hue.sparker.server.sessions.Session;
import com.cloudera.hue.sparker.server.sessions.SessionManager;
import com.cloudera.hue.sparker.server.sessions.Statement;
import com.codahale.metrics.annotation.Timed;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import java.util.List;

@Path("/sessions/{sessionId}/statements")
@Produces(MediaType.APPLICATION_JSON)
public class StatementResource {

    private final SessionManager sessionManager;

    public StatementResource(SessionManager sessionManager) {
        this.sessionManager = sessionManager;
    }

    @GET
    @Timed
    public List<Statement> getStatements(@PathParam("sessionId") String sessionId,
                                         @QueryParam("from") Integer fromStatement,
                                         @QueryParam("limit") Integer limit) throws SessionManager.SessionNotFound {
        Session session = sessionManager.get(sessionId);
        List<Statement> statements;

        if (fromStatement == null && limit == null) {
            statements = session.getStatements();
        } else {
            statements = session.getStatementRange(fromStatement, fromStatement + limit);
        }

        return statements;
    }

    @Path("/{statementId}")
    @GET
    @Timed
    public Statement getStatement(@PathParam("sessionId") String sessionId, @PathParam("statementId") int statementId) throws SessionManager.SessionNotFound, Session.StatementNotFound {
        Session session = sessionManager.get(sessionId);
        return session.getStatement(statementId);
    }

}
