// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.util.Collection;
import java.util.Optional;

import com.cloudera.hue.querystore.common.dao.VertexInfoDao;
import com.cloudera.hue.querystore.common.entities.VertexInfo;
import com.google.inject.Inject;

public class VertexInfoRepository extends JdbiRepository<VertexInfo, VertexInfoDao> {

  @Inject
  public VertexInfoRepository(VertexInfoDao dao) {
    super(dao);
  }

  @Override
  public Optional<VertexInfo> findOne(long id) {
    return dao.findOne(id);
  }

  @Override
  public Collection<VertexInfo> findAll() {
    return dao.findAll();
  }

  @Override
  public VertexInfo save(VertexInfo entity) {
    if (entity.getId() == null) {
      Long id = dao.insert(entity);
      entity.setId(id);
    } else {
      dao.update(entity);
    }

    return entity;
  }

  @Override
  public boolean delete(long id) {
    return !(0 == dao.delete(id));
  }

  public Optional<VertexInfo> findByVertexId(String vertexId) {
    return dao.findByVertexId(vertexId);
  }

  public Collection<VertexInfo> findAllByDagId(String dagId) {
    return dao.findAllByDagId(dagId);
  }

  public int deleteOlder(long startTime) {
    return dao.deleteOlder(startTime * 1000);
  }

  public int purge() {
    return dao.purge();
  }

}
