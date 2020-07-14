// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository.transaction;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Annotation to mark a method or class as transactional.
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(value= {ElementType.METHOD, ElementType.TYPE})
public @interface DASTransaction {}