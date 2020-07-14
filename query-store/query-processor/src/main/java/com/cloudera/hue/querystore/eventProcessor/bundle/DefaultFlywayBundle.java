// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.bundle;

import com.cloudera.hue.querystore.eventProcessor.EventProcessorConfiguration;

import io.dropwizard.db.PooledDataSourceFactory;
import io.dropwizard.flyway.FlywayBundle;
import io.dropwizard.flyway.FlywayFactory;

/**
 * Concrete Flyway bundle to work with Default persistence unit
 */
public class DefaultFlywayBundle extends FlywayBundle<EventProcessorConfiguration> {

  private static final String METADATA_TABLE_NAME = "schema_version";

  @Override
  public PooledDataSourceFactory getDataSourceFactory(EventProcessorConfiguration configuration) {
    return configuration.getDatabase();
  }

  @Override
  public FlywayFactory getFlywayFactory(EventProcessorConfiguration configuration) {
    /*
      The default value for flyway.table has been changed from schema_version to flyway_schema_history.
      So, if we do not update the default metadata table, it will look for flyway_schema_history in db,
      and if not found it will not look for schema_version table even if we have any.

      The existing system will run fine only if we update the metadata table name as 'schema_version',
      otherwise we need to change the table name in db.
     */
    configuration.getFlyway().setMetaDataTableName(METADATA_TABLE_NAME);

    return configuration.getFlyway();
  }
}
