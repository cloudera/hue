// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.resource;

import org.aopalliance.intercept.MethodInterceptor;
import org.aopalliance.intercept.MethodInvocation;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.exception.NotPermissibleException;

import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.List;

public class AdminOnlyInterceptor implements MethodInterceptor {
  /**
   * checks if arguments have {@link RequestContext}.
   * If not found throw {@link IllegalArgumentException}
   * else check user-role
   * if admin proceed
   * else throw {@link com.cloudera.hue.querystore.common.exception.NotPermissibleException}
   *
   * @param methodInvocation
   * @return
   * @throws Throwable
   */
  @Override
  public Object invoke(MethodInvocation methodInvocation) throws Throwable {
    Object[] arguments = methodInvocation.getArguments();

    // ignore interception of methods of Object class
    Method method = methodInvocation.getMethod();
    List<Method> methodsOfObjectClass = Arrays.asList(Object.class.getMethods());
    if(methodsOfObjectClass.contains(method)){
      return methodInvocation.proceed();
    }

    // check role in request context
    RequestContext requestContext = null;
    for (Object arg : arguments) {
      if (arg instanceof RequestContext) {
        requestContext = (RequestContext) arg;
      }
    }
    if (null == requestContext) {
      throw new IllegalArgumentException("No particular user was defined for this call.");
    } else {
      AppAuthentication.Role role = requestContext.getRole();
      if (role.equals(AppAuthentication.Role.ADMIN)) {
        return methodInvocation.proceed();
      } else {
        throw new NotPermissibleException(String.format("This action is not permissible for user %s",
            requestContext.getUsername()));
      }
    }
  }
}
