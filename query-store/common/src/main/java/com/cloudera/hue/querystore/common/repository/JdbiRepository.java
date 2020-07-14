// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.Collection;
import java.util.Optional;

import org.jdbi.v3.core.HandleCallback;

import com.cloudera.hue.querystore.common.entities.JdbiEntity;
import com.google.inject.TypeLiteral;

public abstract class JdbiRepository<Entity extends JdbiEntity, Dao extends JdbiDao<Entity>> {
  protected final Dao dao;

  protected JdbiRepository(Dao dao) {
    this.dao = dao;
  }

  protected Dao getDao() {
    return this.dao;
  }

  protected <T, X extends Exception> void withHandle(HandleCallback<T, X> callback) throws X {
    dao.withHandle(callback);
  }

/*
Trying to reuse the following code across repositories has a few issues.
- java failed in runtime with save NoSuchMethodError in lambda, which went away with a full rebuild
- jdbi throws an exception "org.jdbi.v3.core.mapper.NoSuchMapperException:No mapper registered
  for type class java.lang.Object". Followed the code path in ide, it went away.
Putting this away for another time and using working around found by Niti for now.
*/
  public Optional<Entity> findOne(long id) {
    return dao.findOne(id);
  }

  public Collection<Entity> findAll() {
    return dao.findAll();
  }

  public Entity save(Entity entity) {
    if (entity.getId() == null) {
      long id = dao.insert(entity);
      entity.setId(id);
    } else {
      dao.update(entity);
    }
    return entity;
  }

  public boolean delete(long id) {
    return dao.delete(id) != 0;
  }

  @SuppressWarnings("unchecked")
  public static <R extends JdbiRepository<Entity, Dao>, Entity extends JdbiEntity,
      Dao extends JdbiDao<Entity>> Class<Dao> getDaoClass(Class<R> jdbiRespositoryClass) {
    return (Class<Dao>) getClassOfGenericParameter(jdbiRespositoryClass, 2);
  }

  private static Class<?> getClassOfGenericParameter(Class<?> jdbiRespositoryClass, int parameterIndex) {
    Class<?> daoClass = null;
    Type type = jdbiRespositoryClass.getGenericSuperclass();
    if (type instanceof ParameterizedType) {
      ParameterizedType pType = (ParameterizedType) type;
      daoClass = (Class<?>) pType.getActualTypeArguments()[parameterIndex];
    } else {
      // Because of guice proxying the object the control will come here.
      // We try to infer the type using TypeLiterals
      Type guiceType = TypeLiteral.get(jdbiRespositoryClass).getSupertype(JdbiRepository.class).getType();
      if (guiceType instanceof ParameterizedType) {
        ParameterizedType pType = (ParameterizedType) guiceType;
        daoClass = (Class<?>) pType.getActualTypeArguments()[parameterIndex];
      } else {
        throw new IllegalArgumentException("Cannot infer the Dao class by reflection");
      }
    }
    return daoClass;
  }
}
