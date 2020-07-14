// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.resource;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Use this Annotation to mark all the REST resource methods that can only be invoked by user with ROLE = {@link com.cloudera.hue.querystore.common.AppAuthentication.Role ADMIN}
 * If non Admin user tries to access the resource it should throw an {@link com.cloudera.hue.querystore.common.exception.NotPermissibleException}
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(value= {ElementType.METHOD, ElementType.TYPE})
public @interface AdminOnly {
}
