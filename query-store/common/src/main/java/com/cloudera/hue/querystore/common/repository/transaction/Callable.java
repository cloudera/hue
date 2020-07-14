// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository.transaction;

/**
 * A callable alternative which allows parameterized exception to be thrown.
 *
 * @param <R> Return type.
 * @param <X> Exception type thrown.
 */
@FunctionalInterface
public interface Callable<R, X extends Throwable> {
  R call() throws X;
}
