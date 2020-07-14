// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.entities;

import org.junit.Assert;
import org.junit.Test;

public class HiveQueryTest {

  @Test
  public void isComplete() throws Exception {

    HiveQueryBasicInfo hiveQuery = new HiveQueryBasicInfo();

    hiveQuery.setStatus(HiveQueryBasicInfo.Status.STARTED.name());
    Assert.assertFalse("isComplete must be false", hiveQuery.isComplete());

    hiveQuery.setStatus(HiveQueryBasicInfo.Status.ERROR.name());
    Assert.assertTrue("isComplete must be false", hiveQuery.isComplete());

    hiveQuery.setStatus(HiveQueryBasicInfo.Status.RUNNING.name());
    Assert.assertFalse("isComplete must be false", hiveQuery.isComplete());

    hiveQuery.setStatus(HiveQueryBasicInfo.Status.SUCCESS.name());
    Assert.assertTrue("isComplete must be false", hiveQuery.isComplete());
  }

}