// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.orm.annotation;

import static java.lang.annotation.RetentionPolicy.RUNTIME;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.Target;

/**
 * Annotation to be used at class level to denote the prefix to be used during the query generation
 */
@Retention(RUNTIME)
@Target({ElementType.TYPE})
public @interface SearchQuery {
  String prefix() default "";
  String table();
}
