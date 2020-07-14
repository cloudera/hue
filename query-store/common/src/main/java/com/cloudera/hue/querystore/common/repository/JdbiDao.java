// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.Collection;
import java.util.Optional;

import org.jdbi.v3.sqlobject.SqlObject;

import com.cloudera.hue.querystore.common.entities.JdbiEntity;

public interface JdbiDao<Entity extends JdbiEntity> extends SqlObject {
  /**
   * Finds the record entity with the given id
   * @param id identity of the record
   * @return return Optional of entity if found Optional.empty if not found
   */
  Optional<Entity> findOne(long id);

//  TODO : need another api to fetch as an iterator for really big results.
  /**
   * Returns all the records for this entity type.
   * Use with caution as the returned collection can be big.
   * This all is loaded from db to memory.
   * @return Collection of all records
   */
  Collection<Entity> findAll();

  /**
   * inserts the entity
   * @param entity Entity object to be inserted.
   * @return The Integer identity generated
   */
  long insert(Entity entity);

  /**
   * updates the entity
   * @param entity Entity object to be updated.
   * @return The updated count. Should be 1 if the entity exists with given id
   */
  int update(Entity entity);

  /**
   * Deletes the entities
   * @return number of the deleted record. should be 1 if the entity exists else 0
   */
  int delete(long id);
}
