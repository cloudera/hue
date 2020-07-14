// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.UndeclaredThrowableException;
import java.security.PrivilegedExceptionAction;

import org.apache.hadoop.security.UserGroupInformation;

import com.cloudera.hue.querystore.common.util.HadoopHTTPUtils;

/**
 * Class to download a http resource into a given path.
 */
public class HttpArtifact implements Artifact {

  private final String name;
  private final String url;
  private final Object context;

  private final HadoopHTTPUtils httpUtils;

  public HttpArtifact(HadoopHTTPUtils httpUtils, String name, String url, Object context) {
    this.name = name;
    this.url = url;
    this.httpUtils = httpUtils;
    this.context = context;
  }

  @Override
  public String getName() {
    return name;
  }

  @Override
  public Object getData() throws ArtifactDownloadException {
    try {
      return UserGroupInformation.getCurrentUser().doAs(new PrivilegedExceptionAction<InputStream>() {
        @Override
        public InputStream run() throws Exception  {
            return httpUtils.getConnection(url).getInputStream();
        }
      });
    } catch (IOException | InterruptedException | UndeclaredThrowableException e) {
      throw new ArtifactDownloadException("Error downloading from url: " + url, e);
    }
  }

  @Override
  public  Object getContext()  {
    return context;
  }

  @Override
  public String toString() {
    return "HttpArtifact[Name: " + name + ", URL: " + url + "]";
  }
}
