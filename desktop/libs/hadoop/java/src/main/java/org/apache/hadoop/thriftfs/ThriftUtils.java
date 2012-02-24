/**
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.hadoop.thriftfs;

import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.DataOutputBuffer;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.security.Credentials;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.security.token.Token;
import org.apache.hadoop.security.token.delegation.AbstractDelegationTokenIdentifier;
import org.apache.hadoop.thriftfs.api.IOException;
import org.apache.hadoop.thriftfs.api.ThriftDelegationToken;
import org.apache.hadoop.util.StringUtils;
import org.apache.thrift.TException;


public class ThriftUtils {

  static final Log LOG = LogFactory.getLog(ThriftUtils.class);

  public static final String HUE_USER_NAME_KEY = "hue.kerberos.principal.shortname";
  public static final String HUE_USER_NAME_DEFAULT = "hue";

  public static void initConfigResource() {
    Configuration.addDefaultResource("thriftfs-site.xml");
  }

  public static IOException toThrift(Throwable t) {
    if (t == null) {
      return new IOException();
    }

    IOException ret = new IOException();
    ret.clazz = t.getClass().getName();
    ret.msg = t.getMessage();
    ret.stack = "";
    for (StackTraceElement frame : t.getStackTrace()) {
      ret.stack += frame.toString() + "\n";
    }
    return ret;
  }

  /**
   * An invocation proxy that authorizes all calls into the Thrift interface.
   * This proxy intercepts all method calls on the handler interface, and verifies
   * that the remote UGI is either (a) the hue user, or (b) another HDFS daemon.
   */
  public static class SecurityCheckingProxy<T> implements InvocationHandler {
    private final T wrapped;
    private final Configuration conf;

    @SuppressWarnings("unchecked")
    public static <T> T create(Configuration conf, T wrapped, Class<T> iface) {
      return (T)java.lang.reflect.Proxy.newProxyInstance(
        iface.getClassLoader(),
        new Class[] { iface },
        new SecurityCheckingProxy<T>(wrapped, conf));
    }

    private SecurityCheckingProxy(T wrapped, Configuration conf) {
      this.wrapped = wrapped;
      this.conf = conf;
    }

    public Object invoke(Object proxy, Method m, Object[] args)
      throws Throwable
    {
      try {
        if (LOG.isDebugEnabled()) {
          LOG.debug("Call " + wrapped.getClass() + "." + m.getName()
                    + "(" + StringUtils.join(", ", Arrays.asList(args)) + ")");
        }
        authorizeCall(m);

	    return m.invoke(wrapped, args);
      } catch (InvocationTargetException e) {
	    throw e.getTargetException();
      }
    }

    private void authorizeCall(Method m) throws IOException, TException {
      // TODO: this should use the AccessControlList functionality,
      // ideally.
      try {
        UserGroupInformation caller = UserGroupInformation.getCurrentUser();

        if (!conf.get(HUE_USER_NAME_KEY, HUE_USER_NAME_DEFAULT).equals(
              caller.getShortUserName()) &&
            !UserGroupInformation.getLoginUser().getShortUserName().equals(
              caller.getShortUserName())) {

          String errMsg = "Unauthorized access for user " + caller.getUserName();
          // If we can throw our thrift IOException type, do so, so it goes back
          // to the client correctly.
          if (Arrays.asList(m.getExceptionTypes()).contains(IOException.class)) {
            throw ThriftUtils.toThrift(new Exception(errMsg));
          } else {
            // Otherwise we have to just throw the more generic exception, which
            // won't make it back to the client
            throw new TException(errMsg);
          }
        }
      } catch (java.io.IOException ioe) {
        throw new TException(ioe);
      }
    }
  }

  public static ThriftDelegationToken toThrift(Token<? extends AbstractDelegationTokenIdentifier> delegationToken,
      InetSocketAddress address) throws java.io.IOException {
    String serviceAddress = InetAddress.getByName(address.getHostName()).getHostAddress() + ":"
        + address.getPort();
    delegationToken.setService(new Text(serviceAddress));

    DataOutputBuffer out = new DataOutputBuffer();
    Credentials ts = new Credentials();
    ts.addToken(new Text(serviceAddress), delegationToken);
    ts.writeTokenStorageToStream(out);

    byte[] tokenData = new byte[out.getLength()];
    System.arraycopy(out.getData(), 0, tokenData, 0, tokenData.length);
    return new ThriftDelegationToken(ByteBuffer.wrap(tokenData));
  }
}
