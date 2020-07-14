// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.util;

import java.io.Closeable;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.GeneralSecurityException;

import javax.inject.Inject;
import javax.inject.Singleton;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.security.authentication.client.AuthenticatedURL;
import org.apache.hadoop.security.authentication.client.AuthenticationException;
import org.apache.hadoop.security.ssl.SSLFactory;

/**
 * Class to create a HTTP connection, which works for both SSL and also takes care of SPNEGO auth.
 *
 * SSLFactory creates a thread to refresh the kerberos tokens, which makes it expensive to create per connection and
 * cleanup has to be implemented. Instead we'll make this a singleton and reuse sslFactory.
 *
 * AuthenticatedURL and token class seems to have some reusability built, but will have to verify. Reusing tokens for
 * the same API's to same server will let us optimize for SPNEGO, since the tokens will be reused. But we have to think
 * about tokens per server and per user.
 */
@Singleton
public class HadoopHTTPUtils implements Closeable {
  private final SSLFactory sslFactory;

  @Inject
  public HadoopHTTPUtils(Configuration hadoopConf) throws GeneralSecurityException, IOException {
    sslFactory = new SSLFactory(SSLFactory.Mode.CLIENT, hadoopConf);
    try {
      sslFactory.init();
    } catch (GeneralSecurityException | IOException e) {
      sslFactory.destroy();
      throw e;
    }
  }

  public HttpURLConnection getConnection(String urlStr)
      throws IOException, GeneralSecurityException, AuthenticationException {
    URL url = new URL(urlStr);
    AuthenticatedURL.Token token = new AuthenticatedURL.Token();
    // Is this right, can you have spnego over http, which would mean we'll have sslFactory for all cases.
    AuthenticatedURL authenticatedURL = new AuthenticatedURL(null,
        "https".equals(url.getProtocol()) ? sslFactory : null);
    return authenticatedURL.openConnection(url, token);
  }

  @Override
  public void close() {
    sslFactory.destroy();
  }

  @Override
  protected void finalize() throws Throwable {
    super.finalize();
    close();
  }
}
