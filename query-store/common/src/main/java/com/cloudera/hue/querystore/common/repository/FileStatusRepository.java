// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.Collection;
import java.util.Optional;

import com.cloudera.hue.querystore.common.dao.FileStatusDao;
import com.cloudera.hue.querystore.common.entities.FileStatusEntity;
import com.cloudera.hue.querystore.common.entities.FileStatusEntity.FileStatusType;
import com.google.inject.Inject;

public class FileStatusRepository extends JdbiRepository<FileStatusEntity, FileStatusDao> {
  @Inject
  public FileStatusRepository(FileStatusDao dao) {
    super(dao);
  }

  @Override
  public Optional<FileStatusEntity> findOne(long id) {
    return this.getDao().findOne(id);
  }

  @Override
  public Collection<FileStatusEntity> findAll() {
    return this.getDao().findAll();
  }

  @Override
  public FileStatusEntity save(FileStatusEntity entity) {
    if (entity.getId() == null) {
      long id = this.getDao().insert(entity);
      entity.setId(id);
    } else {
      this.getDao().update(entity);
    }

    return entity;
  }

  @Override
  public boolean delete(long id) {
    return !(0 == this.getDao().delete(id));
  }

  public Collection<FileStatusEntity> findAllByType(FileStatusType type) {
    return this.getDao().findAllByType(type);
  }
}
