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
import com.fasterxml.jackson.databind.node.ObjectNode;

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

    ObjectNode server = (ObjectNode) jsonNode.get("server");

    ObjectNode applicationConnectors = (ObjectNode) (server.get("applicationConnectors").get(0));
    if (applicationConnectors.has("keyStorePassword")) {
      applicationConnectors.set("keyStorePassword", null);
    }
    if (applicationConnectors.has("trustStorePassword")) {
      applicationConnectors.set("trustStorePassword", null);
    }
    if (applicationConnectors.has("keyManagerPassword")) {
      applicationConnectors.set("keyManagerPassword", null);
    }

    EventProcessorConfiguration configs = null;
    configs = objectMapper.treeToValue(jsonNode, EventProcessorConfiguration.class);
    configs.getDatabase().setPassword("");
    configs.setAuthConfig(null);
    return Response.ok(configs).build();
  }
}
