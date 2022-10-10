package com.cloudera.hue.querystore.eventProcessor.resources;

import javax.inject.Inject;
import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

import com.cloudera.hue.querystore.eventProcessor.lifecycle.CleanupManager;

@Path("admin")
public class AdminResource {
  private CleanupManager cleanupmanager;

  @Inject
  AdminResource(CleanupManager cleanupmanager) {
    this.cleanupmanager = cleanupmanager;
  }

  /**
   * Cleans up the databases
   */
  @GET
  @Consumes(MediaType.APPLICATION_JSON)
  @Produces(MediaType.APPLICATION_JSON)
  @Path("/cleanup/{startTime}")
  public void cleanup(@PathParam("startTime") Long startTime) {
    cleanupmanager.deleteOlder(startTime);
    cleanupmanager.purge();
  }

}

