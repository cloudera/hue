// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.resources;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URISyntaxException;
import java.security.PrivilegedExceptionAction;

import javax.inject.Inject;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.SecurityContext;

import org.apache.commons.lang.StringUtils;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.http.client.utils.URIBuilder;

import com.cloudera.hue.querystore.common.util.HadoopHTTPUtils;
import com.cloudera.hue.querystore.common.util.SignatureUtils;

/**
 * HTTP/HTTPS Proxy
 */
@Path("proxy")
public class HTTPProxyResource {

  protected static final String INVALID_QUERY_PARAM_MSG= "Query parameter 'targetURL' & 'signature' is required.";
  protected static final String INVALID_SIGNATURE_MSG = "Invalid signature. The URL cannot be proxied!";
  private final HadoopHTTPUtils httpUtils;

  @Inject
  public HTTPProxyResource(HadoopHTTPUtils httpUtils) {
    this.httpUtils = httpUtils;
  }

  @GET
  public Response proxy(@QueryParam("targetURL") String targetURL,
      @QueryParam("signature") String signature,
      @Context SecurityContext context)
          throws IOException {

    if (StringUtils.isEmpty(targetURL) || StringUtils.isEmpty(signature)) {
      return Response.status(Response.Status.BAD_REQUEST).entity(INVALID_QUERY_PARAM_MSG).build();
    }

    if(!signature.equals(SignatureUtils.generate(targetURL, context))) {
      return Response.status(Response.Status.BAD_REQUEST).entity(INVALID_SIGNATURE_MSG).build();
    }

    try {
      return UserGroupInformation.getCurrentUser().doAs(new PrivilegedExceptionAction<Response>() {
        @Override
        public Response run() throws Exception {
          HttpURLConnection connection = httpUtils.getConnection(targetURL);
          Response.ResponseBuilder responseBuilder = Response.ok(connection.getInputStream());
          responseBuilder.header(HttpHeaders.CONTENT_TYPE, connection.getHeaderField(HttpHeaders.CONTENT_TYPE));
          responseBuilder.header(HttpHeaders.CONTENT_DISPOSITION,
              connection.getHeaderField(HttpHeaders.CONTENT_DISPOSITION));
          responseBuilder.header(HttpHeaders.CONTENT_LENGTH, connection.getHeaderField(HttpHeaders.CONTENT_LENGTH));
          return responseBuilder.build();
        }
      });
    } catch (Exception e) {
      throw new RuntimeException("Error trying to download", e);
    }
  }

  @GET
  @Path("{fileName}")
  public Response proxyWithFileName(@PathParam("fileName") String fileName,
      @QueryParam("targetURL") String targetURL,
      @QueryParam("signature") String signature,
      @Context SecurityContext context)
          throws IOException {
    return proxy(targetURL, signature, context);
  }

  public static String constructProxyPath(String fileName, String targetURL, SecurityContext context)
      throws URISyntaxException {
    String signature = SignatureUtils.generate(targetURL, context);

    URIBuilder builder = new URIBuilder();
    builder.setPath("/api/proxy/" + fileName);
    builder.addParameter("targetURL", targetURL);
    builder.addParameter("signature", signature);

    return builder.build().toString();
  }

}
