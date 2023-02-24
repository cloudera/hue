// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao;

import java.lang.annotation.*;

import org.jdbi.v3.core.statement.SqlLogger;
import org.jdbi.v3.core.statement.StatementContext;
import org.jdbi.v3.sqlobject.customizer.SqlStatementCustomizer;
import org.jdbi.v3.sqlobject.customizer.SqlStatementCustomizerFactory;
import org.jdbi.v3.sqlobject.customizer.SqlStatementCustomizingAnnotation;

/**
 * Logs the final query that being executed by a Dao
 * Should be used only for development. NOT IN PRODUCTION.
 *
 * Can be used as follows in a Dao interface
 * @LogSqlFactory
 * @RegisterBeanMapper(ImpalaQueryEntity.class)
 * public interface ImpalaQueryDao extends JdbiDao<ImpalaQueryEntity> {
 *   ...
 * }
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@SqlStatementCustomizingAnnotation(LogSqlFactory.Factory.class)
public @interface LogSqlFactory {

  class Factory implements SqlStatementCustomizerFactory {
    @Override
    public SqlStatementCustomizer createForType(Annotation annotation, java.lang.Class<?> sqlObjectType) {
      SqlLogger sqlLogger = new SqlLogger() {
        @Override
        public void logBeforeExecution(StatementContext context) {
          logSql(context);
        }
      };
      return statement -> statement.setSqlLogger(sqlLogger);
    }

    private static void logSql(StatementContext context) {
      System.out.println("Raw SQL:\n" + context.getRawSql());
      System.out.println("Parsed SQL:\n" + context.getParsedSql().getSql());
      System.out.println("Rendered SQL:\n" + context.getRenderedSql());
      System.out.println("Statement:\n" + context.getStatement().toString());
    }
  }
}