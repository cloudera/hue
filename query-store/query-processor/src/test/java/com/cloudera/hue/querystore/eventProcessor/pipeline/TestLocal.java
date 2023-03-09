// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.pipeline;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.time.LocalDate;
import java.util.function.Function;

import org.jdbi.v3.core.Jdbi;
import org.jdbi.v3.sqlobject.SqlObjectPlugin;
import org.junit.Before;
import org.junit.ClassRule;
import org.junit.Ignore;
import org.junit.Test;

import com.cloudera.hue.querystore.common.entities.FileStatusEntity;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.cloudera.hue.querystore.common.entities.TezAppInfo;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagExtendedInfo;
import com.cloudera.hue.querystore.common.entities.VertexInfo;
import com.cloudera.hue.querystore.common.entities.FileStatusEntity.FileStatusType;
import com.cloudera.hue.querystore.common.persistence.mappers.JsonArgumentFactory;
import com.cloudera.hue.querystore.common.persistence.mappers.JsonColumnMapper;
import com.cloudera.hue.querystore.common.repository.FileStatusRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.JdbiDao;
import com.cloudera.hue.querystore.common.repository.JdbiRepository;
import com.cloudera.hue.querystore.common.repository.TezAppInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.VertexInfoRepository;
import com.cloudera.hue.querystore.common.repository.transaction.TransactionManager;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.opentable.db.postgres.embedded.FlywayPreparer;
import com.opentable.db.postgres.junit.EmbeddedPostgresRules;
import com.opentable.db.postgres.junit.PreparedDbRule;

@Ignore
public class TestLocal {
  private Jdbi jdbi;
  private TransactionManager mgr;
  private ObjectMapper mapper;

  @ClassRule
  public static PreparedDbRule db = EmbeddedPostgresRules
      .preparedDatabase(FlywayPreparer.forClasspathLocation("filesystem:./src/main/resources/db/migrate"));

  @Before
  public void setup() {
    mapper = new ObjectMapper();
    jdbi = Jdbi.create(db.getTestDatabase());
    jdbi.installPlugin(new SqlObjectPlugin());
    jdbi.registerArgument(new JsonArgumentFactory(mapper, ArrayNode.class));
    jdbi.registerArgument(new JsonArgumentFactory(mapper, ObjectNode.class));
    jdbi.registerColumnMapper(ArrayNode.class, new JsonColumnMapper<>(new ObjectMapper(), ArrayNode.class));
    jdbi.registerColumnMapper(ObjectNode.class, new JsonColumnMapper<>(new ObjectMapper(), ObjectNode.class));
    mgr = new TransactionManager(jdbi);
  }

  @SuppressWarnings({ "rawtypes", "unchecked" })
  private <T extends JdbiRepository> T makeRepo(Class<T> clazz) {
    Class<? extends JdbiDao> daoClass = JdbiRepository.getDaoClass(clazz);
    try {
      Object obj = clazz.getConstructor(daoClass).newInstance(mgr.createDao(daoClass));
      return (T) obj;
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  @SuppressWarnings("rawtypes")
  private <T extends JdbiRepository, D extends JdbiDao, R> R withTransaction(Function<T, R> f, Class<T> clazz) {
    return mgr.withTransaction(() -> f.apply(makeRepo(clazz)));
  }

  @Test
  public void testDagInfo() throws Exception {
    TezDagBasicInfoRepository repo = makeRepo(TezDagBasicInfoRepository.class);
    HiveQueryBasicInfoRepository hrepo = makeRepo(HiveQueryBasicInfoRepository.class);

    TezDagBasicInfo dagInfo = new TezDagBasicInfo();
    dagInfo.setDagId("dag_1");
    dagInfo.setDagName("test_name");
    dagInfo.setAmLogUrl("www.url.com");
    dagInfo.setAmWebserviceVer("Am version");
    dagInfo.setApplicationId("100");
    dagInfo.setCallerId("101");
    dagInfo.setCallerType("public");
    dagInfo.setQueueName("Q1");
    dagInfo.setSourceFile("xyz.txt");
    dagInfo.setStatus("running");
    dagInfo.setStartTime(5L);
    //System.out.println(dagInfo.getStartTime());
    // Test dag insert.
    assertTrue(dagInfo == repo.save(dagInfo));
    assertTrue(dagInfo.getId() > 0);

    // Create supporting hive query object to test foreign key constraint.
    HiveQueryBasicInfo hiveQuery = new HiveQueryBasicInfo();
    hiveQuery.setQuery("Test query");
    hiveQuery.setQueryId("hive_1");
    hiveQuery.setTablesWritten(mapper.createArrayNode());
    hrepo.save(hiveQuery);
    assertTrue(hiveQuery.getId() > 0);

    // Check update.
    dagInfo.setAmWebserviceVer("AM version2");
    assertEquals("AM version2", dagInfo.getAmWebserviceVer());
    dagInfo.setHiveQueryId(hiveQuery.getId());
    repo.save(dagInfo);

    // find dag object by table id
    TezDagBasicInfo dag2 = repo.findOne(dagInfo.getId()).get();
    assertEquals(dagInfo, dag2);

    // find dag object by dag id.
    dag2 = repo.findByDagId("dag_1").get();
    assertEquals(dagInfo, dag2);

    // find dag object by hive query table id.
    dag2 = repo.getByHiveQueryTableId(hiveQuery.getId()).iterator().next();
    assertEquals(dagInfo, dag2);

    // cleanup the temp objects created.
    repo.delete(dagInfo.getId());
    hrepo.delete(hiveQuery.getId());

    // Verify dag info has been deleted.
    assertFalse(repo.findOne(dagInfo.getId()).isPresent());

    // test for deleted not older than
    TezDagBasicInfo dag3 = new TezDagBasicInfo();
    dag3.setStartTime(400L);
    dag3.setDagId("dag_temp1");
    dag3.setDagName("temp1_name");
    repo.save(dag3);

    TezDagBasicInfo dag4 = new TezDagBasicInfo();
    dag4.setStartTime(6000L);
    dag4.setDagId("dag_temp2");
    dag4.setDagName("temp2_name");
    repo.save(dag4);

    assertTrue(repo.findOne(dag3.getId()).isPresent());
    assertTrue(repo.findOne(dag4.getId()).isPresent());

    assertEquals(1, repo.deleteOlder(1L));

    assertFalse(repo.findOne(dag3.getId()).isPresent());
    assertTrue(repo.findOne(dag4.getId()).isPresent());

    repo.delete(dag4.getId());
  }

  public void testFileStatus() throws Exception {
    Class<FileStatusRepository> repoClass = FileStatusRepository.class;
    FileStatusEntity setting = new FileStatusEntity();
    setting.setDate(LocalDate.ofEpochDay(0));
    setting.setFilePath("file1");
    setting.setFileType(FileStatusType.HIVE);
    setting.setLastEventTime(1232141241L);
    setting.setFinished(false);

    withTransaction(r -> r.save(setting), repoClass);
    setting.setPosition(100L);
    withTransaction(r -> r.save(setting), repoClass);
    withTransaction(r -> r.findOne(setting.getId()), repoClass).get();
    withTransaction(r -> r.findAll(), repoClass).iterator().next();
    withTransaction(r -> r.findAllByType(FileStatusType.HIVE), repoClass).iterator().next();
    withTransaction(r -> r.delete(setting.getId()), repoClass);
  }

  public void testVertexInfo() throws Exception {
    TezDagBasicInfoRepository dagRepo = makeRepo(TezDagBasicInfoRepository.class);
    TezDagBasicInfo dagInfo = new TezDagBasicInfo();
    dagInfo.setDagId("dag1");
    dagRepo.save(dagInfo);

    Class<VertexInfoRepository> repoClass = VertexInfoRepository.class;
    VertexInfo vi = new VertexInfo();
    vi.setVertexId("vid1");
    vi.setDagId(dagInfo.getId());
    vi.setClassName("TestVertex");
    vi.setDomainId("random_domain");
    vi.setInitRequestedTime(1L);
    vi.setStartRequestedTime(2L);
    vi.setStartTime(3L);
    vi.setEndTime(5L);
    vi.setTaskCount(10);
    vi.setSucceededTaskCount(10);
    vi.setKilledTaskAttemptCount(2);
    vi.setKilledTaskCount(2);
    vi.setFailedTaskAttemptCount(2);
    vi.setFailedTaskCount(0);
    vi.setCompletedTaskCount(10);
    vi.setCounters(mapper.createArrayNode().add("test counter"));
    vi.setEvents(mapper.createArrayNode().add("test event"));
    vi.setStats(mapper.createObjectNode().put("testKey", "test value"));

    withTransaction(r -> r.save(vi), repoClass);
    vi.setTaskCount(10);
    withTransaction(r -> r.save(vi), repoClass);
    withTransaction(r -> r.findOne(vi.getId()), repoClass).get();
    withTransaction(r -> r.findAll(), repoClass).iterator().next();
    withTransaction(r -> r.findByVertexId("vid1"), repoClass).get();
    withTransaction(r -> r.findAllByDagId("dag1"), repoClass).iterator().next();
    withTransaction(r -> r.delete(vi.getId()), repoClass);

    dagRepo.delete(dagInfo.getId());
  }

  public void testQueryDetails() throws Exception {
    HiveQueryBasicInfo hiveQuery = new HiveQueryBasicInfo();
    hiveQuery.setQuery("Test query");
    hiveQuery.setQueryId("hive_1");
    hiveQuery.setTablesWritten(new ObjectMapper().createArrayNode());
    HiveQueryBasicInfoRepository hRepo = makeRepo(HiveQueryBasicInfoRepository.class);
    hRepo.save(hiveQuery);

    Class<HiveQueryExtendedInfoRepository> repoClass = HiveQueryExtendedInfoRepository.class;
    HiveQueryExtendedInfoRepository qdRepo = makeRepo(repoClass);

    HiveQueryExtendedInfo details = new HiveQueryExtendedInfo();
    details.setConfiguration(mapper.createObjectNode());
    details.setExplainPlan(mapper.createObjectNode());
    qdRepo.save(details);

    details.setPerf(mapper.createObjectNode());
    details.setHiveQueryId(hiveQuery.getId());
    qdRepo.save(details);

    withTransaction(r -> r.findOne(details.getId()), repoClass).get();
    withTransaction(r -> r.findAll(), repoClass).iterator().next();
    withTransaction(r -> r.findByHiveQueryId("hive_1"), repoClass).get();
    withTransaction(r -> r.findByDagId("hive_1"), repoClass);

    qdRepo.delete(details.getId());
    hRepo.delete(hiveQuery.getId());
  }

  public void testDagDetails() throws Exception {
    TezDagBasicInfo dagInfo = new TezDagBasicInfo();
    dagInfo.setDagId("dag_1");
    dagInfo.setDagName("test_name");
    TezDagBasicInfo dag = withTransaction(repo -> repo.save(dagInfo), TezDagBasicInfoRepository.class);

    HiveQueryBasicInfo hiveQuery = new HiveQueryBasicInfo();
    hiveQuery.setQuery("Test query");
    hiveQuery.setQueryId("hive_1");
    hiveQuery.setTablesWritten(mapper.createArrayNode());
    HiveQueryBasicInfoRepository hRepo = makeRepo(HiveQueryBasicInfoRepository.class);
    hRepo.save(hiveQuery);

    Class<TezDagExtendedInfoRepository> repoClass = TezDagExtendedInfoRepository.class;
    TezDagExtendedInfoRepository qdRepo = makeRepo(repoClass);

    TezDagExtendedInfo details = new TezDagExtendedInfo();
    details.setDagInfoId(dag.getId());
    details.setDagPlan(mapper.createObjectNode());
    details.setVertexNameIdMapping(mapper.createObjectNode().put("test", "value"));
    details.setDiagnostics("Nothing");
    qdRepo.save(details);

    details.setCounters(mapper.createArrayNode());
    details.setHiveQueryId(hiveQuery.getId());
    qdRepo.save(details);

    TezDagExtendedInfo dd = withTransaction(r -> r.findOne(details.getId()), repoClass).get();
    System.out.println("Is true: " + dd.getVertexNameIdMapping().get("test").asText().equals("value"));
    withTransaction(r -> r.findAll(), repoClass).iterator().next();
    withTransaction(r -> r.findByHiveQueryId("hive_1"), repoClass).iterator().next();
    withTransaction(r -> r.findByDagId("dag_1"), repoClass).get();

    withTransaction(repo -> repo.delete(dag.getId()), TezDagBasicInfoRepository.class);
    qdRepo.delete(details.getId());
    hRepo.delete(hiveQuery.getId());
  }

  public void testTezAppInfo() throws Exception {
    TezAppInfo appInfo = new TezAppInfo();
    appInfo.setAppId("test_app_1");
    appInfo.setConfig(mapper.createObjectNode());

    Class<TezAppInfoRepository> repoClass = TezAppInfoRepository.class;
    TezAppInfoRepository repo = makeRepo(repoClass);

    repo.save(appInfo);
    appInfo.setAppId("test_app_2");
    repo.save(appInfo);

    withTransaction(r -> r.findOne(appInfo.getId()), repoClass).get();
    withTransaction(r -> r.findAll(), repoClass).iterator().next();
    withTransaction(r -> r.delete(appInfo.getId()), repoClass);
  }
}
