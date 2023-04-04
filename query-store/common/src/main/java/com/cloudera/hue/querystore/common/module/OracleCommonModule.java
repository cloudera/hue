// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.module;

import javax.inject.Singleton;

import org.apache.hadoop.conf.Configuration;
import org.jdbi.v3.core.Jdbi;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.dao.FileStatusDao;
import com.cloudera.hue.querystore.common.dao.HiveQueryBasicInfoDao;
import com.cloudera.hue.querystore.common.dao.HiveQueryExtendedInfoDao;
import com.cloudera.hue.querystore.common.dao.ImpalaQueryDao;
import com.cloudera.hue.querystore.common.dao.TezAppInfoDao;
import com.cloudera.hue.querystore.common.dao.TezDagBasicInfoDao;
import com.cloudera.hue.querystore.common.dao.TezDagExtendedInfoDao;
import com.cloudera.hue.querystore.common.dao.VertexInfoDao;
import com.cloudera.hue.querystore.common.dao.oracle.FileStatusOracleDao;
import com.cloudera.hue.querystore.common.dao.oracle.HiveQueryBasicInfoOracleDao;
import com.cloudera.hue.querystore.common.dao.oracle.HiveQueryExtendedInfoOracleDao;
import com.cloudera.hue.querystore.common.dao.oracle.TezAppInfoOracleDao;
import com.cloudera.hue.querystore.common.dao.oracle.TezDagBasicInfoOracleDao;
import com.cloudera.hue.querystore.common.dao.oracle.TezDagExtendedInfoOracleDao;
import com.cloudera.hue.querystore.common.dao.oracle.VertexInfoOracleDao;
import com.cloudera.hue.querystore.common.persistence.mappers.JsonArgumentFactory;
import com.cloudera.hue.querystore.common.persistence.mappers.JsonColumnMapper;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.hue.querystore.common.repository.transaction.TransactionManager;
import com.cloudera.hue.querystore.common.resource.AdminOnly;
import com.cloudera.hue.querystore.common.resource.AdminOnlyInterceptor;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.datatype.jdk8.Jdk8Module;
import com.fasterxml.jackson.jaxrs.json.JacksonJsonProvider;
import com.google.inject.AbstractModule;
import com.google.inject.Provides;
import com.google.inject.matcher.Matchers;

import io.dropwizard.jackson.Jackson;

/**
 * Common injections
 */
public class OracleCommonModule extends AbstractModule {

  private final Jdbi jdbi;
  private AppAuthentication appAuth;

  public OracleCommonModule(Jdbi jdbi, AppAuthentication appAuth){
    this.jdbi = jdbi;
    this.appAuth = appAuth;
  }

  @Override
  protected void configure() {
    // TODO: Find a better place to add this.
    ObjectMapper mapper = new ObjectMapper();
    mapper.registerModule(new Jdk8Module());
    jdbi.registerColumnMapper(ArrayNode.class, new JsonColumnMapper<>(mapper, ArrayNode.class));
    jdbi.registerColumnMapper(ObjectNode.class, new JsonColumnMapper<>(mapper, ObjectNode.class));
    jdbi.registerArgument(new JsonArgumentFactory(mapper, ArrayNode.class));
    jdbi.registerArgument(new JsonArgumentFactory(mapper, ObjectNode.class));

    TransactionManager txnManager = new TransactionManager(jdbi);
    bind(TransactionManager.class).toInstance(txnManager);
    bindInterceptor(Matchers.any(), Matchers.annotatedWith(DASTransaction.class), txnManager);
    bindInterceptor(Matchers.annotatedWith(DASTransaction.class), Matchers.any(), txnManager);

    // Remove this: There may not be roles in event processor.
    AdminOnlyInterceptor adminOnlyInterceptor = new AdminOnlyInterceptor();
    bindInterceptor(Matchers.any(), Matchers.annotatedWith(AdminOnly.class), adminOnlyInterceptor);
    bindInterceptor(Matchers.annotatedWith(AdminOnly.class), Matchers.any(), adminOnlyInterceptor);

    bind(Jdbi.class).toInstance(jdbi);
    bind(AppAuthentication.class).toInstance(appAuth);

  }

  @Provides
  public FileStatusDao getFileStatusDao(TransactionManager txnManager) {
    return txnManager.createDao(FileStatusOracleDao.class);
  }

  @Provides
  public HiveQueryBasicInfoDao getHiveQueryDao(TransactionManager txnManager) {
    return txnManager.createDao(HiveQueryBasicInfoOracleDao.class);
  }

  @Provides
  public HiveQueryExtendedInfoDao getQueryDetailsDao(TransactionManager txnManager) {
    return txnManager.createDao(HiveQueryExtendedInfoOracleDao.class);
  }

  @Provides
  public ImpalaQueryDao getImpalaQueryDao(TransactionManager txnManager) {
    return txnManager.createDao(ImpalaQueryDao.class);
  }

  @Provides
  public TezDagBasicInfoDao getDagInfoDao(TransactionManager txnManager) {
    return txnManager.createDao(TezDagBasicInfoOracleDao.class);
  }

  @Provides
  public TezDagExtendedInfoDao getDagDetailsDao(TransactionManager txnManager) {
    return txnManager.createDao(TezDagExtendedInfoOracleDao.class);
  }

  @Provides
  public VertexInfoDao getVertexInfoDao(TransactionManager txnManager) {
    return txnManager.createDao(VertexInfoOracleDao.class);
  }

  @Provides
  public TezAppInfoDao getTezAppInfoDao(TransactionManager txnManager) {
    return txnManager.createDao(TezAppInfoOracleDao.class);
  }

  @Provides @Singleton
  public ObjectMapper objectMapper() {
    return Jackson.newObjectMapper();
  }

  @Provides @Singleton
  public JacksonJsonProvider jacksonJsonProvider(ObjectMapper mapper) {
    return new JacksonJsonProvider(mapper);
  }

  @Provides @Singleton
  public Configuration provideHadoopConfiguration() {
    return new Configuration();
  }

}
