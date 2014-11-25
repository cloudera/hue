package com.cloudera.hue.sparker.server.resources;

import com.cloudera.hue.sparker.server.sessions.Cell;
import com.cloudera.hue.sparker.server.sessions.Session;
import com.cloudera.hue.sparker.server.sessions.SessionManager;
import com.codahale.metrics.annotation.Timed;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import java.util.List;

@Path("/sessions/{sessionId}/cells")
@Produces(MediaType.APPLICATION_JSON)
public class CellResource {

    private final SessionManager sessionManager;

    public CellResource(SessionManager sessionManager) {
        this.sessionManager = sessionManager;
    }

    @GET
    @Timed
    public List<Cell> getCells(@PathParam("sessionId") String sessionId,
                               @QueryParam("from") Integer fromCell,
                               @QueryParam("limit") Integer limit) throws SessionManager.SessionNotFound {
        Session session = sessionManager.get(sessionId);
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

    @Path("/{cellId}")
    @GET
    @Timed
    public Cell getCell(@PathParam("sessionId") String sessionId, @PathParam("cellId") int cellId) throws SessionManager.SessionNotFound {
        Session session = sessionManager.get(sessionId);
        return session.getCell(cellId);
    }

}
