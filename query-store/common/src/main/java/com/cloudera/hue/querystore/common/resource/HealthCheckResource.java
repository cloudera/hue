// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.resource;

import java.util.Map;
import java.util.SortedMap;
import java.util.function.Function;
import java.util.stream.Collectors;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

import com.codahale.metrics.health.HealthCheck;
import com.codahale.metrics.health.HealthCheckRegistry;

import lombok.Value;

@Produces(MediaType.APPLICATION_JSON)
@Path("/status")
public class HealthCheckResource {
  private final HealthCheckRegistry healthCheckRegistry;

  public HealthCheckResource(HealthCheckRegistry healthCheckRegistry) {
    this.healthCheckRegistry = healthCheckRegistry;
  }

  @GET
  public Map<String, FormattedResult> runChecks() {
    SortedMap<String, HealthCheck.Result> map = healthCheckRegistry.runHealthChecks();
    return map.keySet().stream().collect(Collectors.toMap(Function.identity(), x -> {
      HealthCheck.Result result = map.get(x);
      return toFormattedResult(result);
    }));
  }

  private FormattedResult toFormattedResult(HealthCheck.Result result) {
    return new FormattedResult(result.isHealthy(), result.getMessage());
  }

  @Value
  public static class FormattedResult {
    private final boolean healthy;
    private final String message;
  }
}
