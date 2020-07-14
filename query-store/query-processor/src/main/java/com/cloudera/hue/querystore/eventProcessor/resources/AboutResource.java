// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.resources;

import javax.inject.Inject;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import com.cloudera.hue.querystore.eventProcessor.EventProcessorConfiguration;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

@Path("about")
public class AboutResource {
  private EventProcessorConfiguration eventProcessorConfiguration;
  private final ObjectMapper objectMapper;

  @Inject
  AboutResource(EventProcessorConfiguration eventProcessorConfiguration, ObjectMapper objectMapper) {
    this.eventProcessorConfiguration = eventProcessorConfiguration;
    this.objectMapper = objectMapper;
  }

  @GET
  @Path("configs")
  @Produces(MediaType.APPLICATION_JSON)
  public Response getConfigs() throws JsonProcessingException {
    JsonNode jsonNode = objectMapper.valueToTree(this.eventProcessorConfiguration);
    EventProcessorConfiguration configs = null;
    configs = objectMapper.treeToValue(jsonNode, EventProcessorConfiguration.class);
    configs.getDatabase().setPassword("");
    configs.setAuthConfig(null);
    return Response.ok(configs).build();
  }
}
