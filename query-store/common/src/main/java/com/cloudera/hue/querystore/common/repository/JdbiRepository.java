// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.Collection;
import java.util.Optional;

import org.jdbi.v3.core.HandleCallback;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.entities.JdbiEntity;
import com.cloudera.hue.querystore.common.exception.DBUpdateFailedException;
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

  protected boolean checkCurrentUser(AppAuthentication.Role role) {
    return !AppAuthentication.Role.ADMIN.equals(role);
  }

  protected boolean isNotNull(Object obj) {
    return obj != null;
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

  /**
   * Insert or updates the entity. The returned entity does not contain the auto updated fields like version.
   * Do not use this entity to update again. Get the entity again using findOne and use that object to do any
   * further updates. The return type is carried over from legacy hibernate implementation
   * TODO: make this method and super method return void for better clarity. Or may be we need not Override.
   * @param entity Entity object to be saved or updated.
   * @return
   */
  public Entity save(Entity entity) {
    if (entity.getId() == null) {
      Long id = dao.insert(entity);
      entity.setId(id);
    } else {
      int update = dao.update(entity);
      if (0 == update) {
        throw new DBUpdateFailedException(entity);
      }
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
