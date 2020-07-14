// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.postgres;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import org.flywaydb.core.Flyway;
import org.jdbi.v3.core.Jdbi;
import org.jdbi.v3.sqlobject.SqlObjectPlugin;
import org.junit.Assert;
import org.junit.Before;
import org.junit.ClassRule;
import org.junit.Ignore;
import org.junit.Test;

import com.cloudera.hue.querystore.common.dao.HiveQueryBasicInfoDao;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.exception.DBUpdateFailedException;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.opentable.db.postgres.junit.EmbeddedPostgresRules;
import com.opentable.db.postgres.junit.PreparedDbRule;

import io.dropwizard.flyway.FlywayFactory;
import lombok.extern.slf4j.Slf4j;

// This test is ignored since the embedded postgres is not killed when the test finishes.
@Slf4j
@Ignore
public class HiveQueryRepositoryTest {

  // The flyway preparer uses a different version of Flyway, the default constructor has been removed
  @ClassRule
  public static PreparedDbRule db = EmbeddedPostgresRules.preparedDatabase(ds -> {
    FlywayFactory factory = new FlywayFactory();
    factory.setLocations(Collections.singletonList("filesystem:./src/main/resources/db/migrate"));
    Flyway flyway = factory.build(ds);
    flyway.migrate();
  });

  private Jdbi jdbi;

  @Before
  public void setup(){
    jdbi = Jdbi.create(db.getTestDatabase());
    jdbi.installPlugin(new SqlObjectPlugin());
  }

  @Test
  public void testDirtyWriteFailureInDAO() {
    HiveQueryBasicInfoDao hiveQueryDao = jdbi.onDemand(HiveQueryBasicInfoDao.class);
    HiveQueryBasicInfo hiveQuery = new HiveQueryBasicInfo();
    hiveQuery.setStartTime(10l);
    hiveQuery.setEndTime(20l);

    Long hiveQueryId = hiveQueryDao.insert(hiveQuery);
    log.info("inserted key : {}", hiveQueryId);

    Optional<HiveQueryBasicInfo> one = hiveQueryDao.findOne(hiveQueryId);
    Optional<HiveQueryBasicInfo> two = hiveQueryDao.findOne(hiveQueryId);
    Assert.assertTrue(one.isPresent());
    Assert.assertTrue(two.isPresent());

    HiveQueryBasicInfo hiveQuery1 = one.get();
    HiveQueryBasicInfo hiveQuery2 = two.get();
    hiveQuery1.setExecutionMode("LLAP");
    hiveQuery2.setQueueName("TEZ");

    int update1 = hiveQueryDao.update(hiveQuery1);

    int update2 = hiveQueryDao.update(hiveQuery2);

    Assert.assertEquals(1, update1);
    Assert.assertEquals(0, update2);

    Optional<HiveQueryBasicInfo> updatedHQ = hiveQueryDao.findOne(hiveQueryId);
    HiveQueryBasicInfo hiveQuery3 = updatedHQ.get();
    Assert.assertNull(hiveQuery3.getQueueName());
    Assert.assertEquals("LLAP", hiveQuery3.getExecutionMode());
  }

  @Test
  public void testDirtyWriteFailureInRepo() {
    HiveQueryBasicInfoDao hiveQueryDao = jdbi.onDemand(HiveQueryBasicInfoDao.class);
    HiveQueryBasicInfoRepository hiveQueryRepository = new HiveQueryBasicInfoRepository(hiveQueryDao);

    HiveQueryBasicInfo hiveQuery = new HiveQueryBasicInfo();
    hiveQuery.setStartTime(10l);
    hiveQuery.setEndTime(20l);

    HiveQueryBasicInfo savedHiveQuery = hiveQueryRepository.save(hiveQuery);
    Long hiveQueryId = savedHiveQuery.getId();
    log.info("inserted key : {}", hiveQueryId);

    Optional<HiveQueryBasicInfo> one = hiveQueryRepository.findOne(hiveQueryId);
    Optional<HiveQueryBasicInfo> two = hiveQueryRepository.findOne(hiveQueryId);
    Assert.assertTrue(one.isPresent());
    Assert.assertTrue(two.isPresent());

    HiveQueryBasicInfo hiveQuery1 = one.get();
    HiveQueryBasicInfo hiveQuery2 = two.get();
    hiveQuery1.setExecutionMode("LLAP");
    hiveQuery2.setQueueName("TEZ");

    hiveQueryRepository.save(hiveQuery1);

    boolean caughtException = false;
    try{
      hiveQueryRepository.save(hiveQuery2);
    }catch(DBUpdateFailedException ufe){
      log.info("Exception occurred while saving for second time.");
      caughtException = true;
    }

    Assert.assertTrue(caughtException);

    Optional<HiveQueryBasicInfo> updatedHQ = hiveQueryRepository.findOne(hiveQueryId);
    HiveQueryBasicInfo hiveQuery3 = updatedHQ.get();
    Assert.assertNull(hiveQuery3.getQueueName());
    Assert.assertEquals("LLAP", hiveQuery3.getExecutionMode());
  }

  @Test
  public void testDirtyUpdateProcessedInRepo() {
    HiveQueryBasicInfoDao hiveQueryDao = jdbi.onDemand(HiveQueryBasicInfoDao.class);
    HiveQueryBasicInfoRepository hiveQueryRepository = new HiveQueryBasicInfoRepository(hiveQueryDao);

    HiveQueryBasicInfo hq1 = new HiveQueryBasicInfo();
    hq1.setStartTime(10l);
    hq1.setEndTime(20l);

    HiveQueryBasicInfo hq2 = new HiveQueryBasicInfo();
    hq2.setStartTime(100l);
    hq2.setEndTime(200l);

    HiveQueryBasicInfo hq3 = new HiveQueryBasicInfo();
    hq3.setStartTime(300l);
    hq3.setEndTime(400l);

    HiveQueryBasicInfo savedHiveQuery1 = hiveQueryRepository.save(hq1);
    Long hiveQueryId1 = savedHiveQuery1.getId();
    log.info("inserted key : {}", hiveQueryId1);

    HiveQueryBasicInfo savedHiveQuery2 = hiveQueryRepository.save(hq2);
    Long hiveQueryId2 = savedHiveQuery2.getId();
    log.info("inserted key-2 : {}", hiveQueryId2);

    HiveQueryBasicInfo savedHiveQuery3 = hiveQueryRepository.save(hq3);
    Long hiveQueryId3 = savedHiveQuery3.getId();
    log.info("inserted key-2 : {}", hiveQueryId3);

    Optional<HiveQueryBasicInfo> one = hiveQueryRepository.findOne(hiveQueryId1);
    Optional<HiveQueryBasicInfo> two = hiveQueryRepository.findOne(hiveQueryId2);
    Optional<HiveQueryBasicInfo> three = hiveQueryRepository.findOne(hiveQueryId3);
    Assert.assertTrue(one.isPresent());
    Assert.assertTrue(two.isPresent());
    Assert.assertTrue(three.isPresent());

    HiveQueryBasicInfo hiveQuery1 = one.get();
    HiveQueryBasicInfo hiveQuery2 = two.get();
    HiveQueryBasicInfo hiveQuery3 = three.get();

    List<Long> listOfQueriesIds = Arrays.asList(hiveQuery1.getId(), hiveQuery2.getId());

    hiveQueryRepository.updateQueriesAsProcessed(listOfQueriesIds);

    hiveQuery1.setExecutionMode("LLAP");
    hiveQuery2.setQueueName("TEZ");
    hiveQuery3.setQueueName("TEZ");

    boolean caughtException1 = false;
    try{
      hiveQueryRepository.save(hiveQuery1);
    }catch(DBUpdateFailedException ufe){
      log.info("Exception occurred while saving for second time.");
      caughtException1 = true;
    }

    boolean caughtException2 = false;
    try{
      hiveQueryRepository.save(hiveQuery2);
    }catch(DBUpdateFailedException ufe){
      log.info("Exception occurred while saving for second time.");
      caughtException2 = true;
    }

    boolean caughtException3 = false;
    try{
      hiveQueryRepository.save(hiveQuery3);
    }catch(DBUpdateFailedException ufe){
      log.info("Exception occurred while saving for second time.");
      caughtException3 = true;
    }

    Assert.assertTrue(caughtException1);
    Assert.assertTrue(caughtException2);
    Assert.assertFalse(caughtException3);

    HiveQueryBasicInfo hiveQueryUpdated1 = hiveQueryRepository.findOne(hiveQueryId1).get();
    Assert.assertNull(hiveQueryUpdated1.getQueueName());
    Assert.assertNull(hiveQueryUpdated1.getExecutionMode());

    HiveQueryBasicInfo hiveQueryUpdated2 = hiveQueryRepository.findOne(hiveQueryId2).get();
    Assert.assertNull(hiveQueryUpdated2.getQueueName());
    Assert.assertNull(hiveQueryUpdated2.getExecutionMode());

    HiveQueryBasicInfo hiveQueryUpdated3 = hiveQueryRepository.findOne(hiveQueryId3).get();
    Assert.assertEquals("TEZ",hiveQueryUpdated3.getQueueName());
    Assert.assertNull(hiveQueryUpdated3.getExecutionMode());
  }
}