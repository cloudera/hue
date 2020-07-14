// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.Collection;

import javax.inject.Inject;
import javax.inject.Provider;
import javax.inject.Singleton;

import com.cloudera.hue.querystore.common.entities.FileStatusEntity;
import com.cloudera.hue.querystore.common.entities.FileStatusEntity.FileStatusType;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;

@Singleton
@DASTransaction
public class FileStatusPersistenceManager {

  private Provider<FileStatusRepository> fsRepoProvider;

  @Inject
  public FileStatusPersistenceManager(Provider<FileStatusRepository> fsRepoProvider) {
    this.fsRepoProvider = fsRepoProvider;
  }

  public Collection<FileStatusEntity> getFileOfType(FileStatusType fsType) {
    return fsRepoProvider.get().findAllByType(fsType);
  }

  public FileStatusEntity create(FileStatusEntity fsEntity) {
    return fsRepoProvider.get().save(fsEntity);
  }

  public FileStatusEntity update(FileStatusEntity fsEntity) {
    return fsRepoProvider.get().save(fsEntity);
  }

  public boolean delete(FileStatusEntity fsEntity) {
    return fsRepoProvider.get().delete(fsEntity.getId());
  }
}
