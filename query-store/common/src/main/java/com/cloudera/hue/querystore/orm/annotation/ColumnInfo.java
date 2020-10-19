// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.orm.annotation;

import static java.lang.annotation.ElementType.FIELD;
import static java.lang.annotation.ElementType.METHOD;
import static java.lang.annotation.RetentionPolicy.RUNTIME;

import java.lang.annotation.Retention;
import java.lang.annotation.Target;

/**
 * Annotation to provide the meta-information for the fields in the entity class
 */

@Retention(RUNTIME)
@Target({FIELD, METHOD})
public @interface ColumnInfo {
  boolean id() default false;
  boolean searchable() default false;
  boolean sortable() default false;
  boolean highlightRequired() default false;
  String tsVectorColumnName() default "";
  String highlightProjectionName() default "";
  String columnName();
  String fieldName() default "";
  String displayName() default "";
  boolean facetable() default false;
  boolean rangeFacetable() default false;

  // Excludes the field from fields-information
  boolean exclude() default false;
}
