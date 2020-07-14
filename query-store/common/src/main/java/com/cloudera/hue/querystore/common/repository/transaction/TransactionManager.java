// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository.transaction;

import java.util.HashMap;
import java.util.Map;

import org.aopalliance.intercept.MethodInterceptor;
import org.aopalliance.intercept.MethodInvocation;
import org.jdbi.v3.core.Handle;
import org.jdbi.v3.core.Jdbi;

import com.cloudera.hue.querystore.common.entities.JdbiEntity;
import com.cloudera.hue.querystore.common.repository.JdbiDao;

/**
 * Transaction manager to create dao in transaction and out of transaction context.
 *
 * Register provider for dao with guice, which should use createDao to return dao instances.
 * If a transaction is running, the dao instance will be part of the transaction and is only
 * valid until the transaction finishes.
 *
 * When no transaction is running, an independent dao object is created, which will execute
 * every sql independently, creating a connection on demand.
 *
 * The method interceptor should be used with guice to ensure that annotated methods are executed
 * within a transaction.
 */
public class TransactionManager implements MethodInterceptor {

  private final Jdbi jdbi;
  private final ThreadLocal<Handle> handleThreadLocal = new ThreadLocal<>();
  private final ThreadLocal<Map<Class<?>, JdbiDao<?>>> daoCache = new ThreadLocal<>();

  public TransactionManager(Jdbi jdbi) {
    this.jdbi = jdbi;
  }

  // TODO: Verify if we should ignore methods from object class.
  @Override
  public Object invoke(MethodInvocation invocation) throws Throwable {
    Handle handle = handleThreadLocal.get();
    if (handle != null) {
      return invocation.proceed();
    }
    return withTransaction(() -> {
      try {
        return invocation.proceed();
      } catch (Exception e) {
        throw e;
      } catch (Throwable t) {
        throw new RuntimeException(t);
      }
    });
  }

  public <T, X extends Exception> T withTransaction(Callable<T, X> callable) throws X {
    if (handleThreadLocal.get() != null) {
      return callable.call();
    }
    return jdbi.<T, X>inTransaction(handle -> {
      handleThreadLocal.set(handle);
      daoCache.set(new HashMap<>());
      try {
        return callable.call();
      } finally {
        handleThreadLocal.remove();
        daoCache.remove();
      }
    });
  }

  public <I, E extends JdbiEntity, D extends JdbiDao<E>> D createDao(Class<D> clazz) {
    Map<Class<?>, JdbiDao<?>> cache = daoCache.get();
    if (cache != null) {
      @SuppressWarnings("unchecked")
      D dao = (D)cache.get(clazz);
      if (dao == null) {
        Handle handle = handleThreadLocal.get();
        dao = handle.attach(clazz);
        cache.put(clazz, dao);
      }
      return dao;
    }
    // TODO: An optimization would be to reuse instances.
    //   A global weak hash map for requests outside a transaction.
    return jdbi.onDemand(clazz);
  }
}
