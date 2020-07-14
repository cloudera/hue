// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.config;

import org.junit.Assert;
import org.junit.Test;

import com.cloudera.hue.querystore.common.config.DasConfiguration.ConfVar;

public class DasConfigurationTest {
  private static enum TestEnum {
    val1,
    val2
  }

  @Test
  public void testAllGets() {
    DasConfiguration configuration = new DasConfiguration();

    // String tests.
    ConfVar<String> strConf = new ConfVar<>("str", "d0");
    Assert.assertFalse(configuration.get("str").isPresent());
    Assert.assertEquals("d1", configuration.getString("str", "d1"));
    Assert.assertEquals("d0", configuration.getConf(strConf));

    configuration.setConf(strConf, "val");
    Assert.assertTrue(configuration.get("str").isPresent());
    Assert.assertEquals("val", configuration.get("str").get());
    Assert.assertEquals("val", configuration.getString("str", "d1"));
    Assert.assertEquals("val", configuration.getConf(strConf));

    // Integer tests.
    ConfVar<Integer> intConf = new ConfVar<>("int", 10);
    Assert.assertEquals(10, (int)configuration.getConf(intConf));
    Assert.assertEquals(100, configuration.getInt("int", 100));
    configuration.setConf(intConf, 1);
    configuration.set("ints", "123");
    Assert.assertEquals(1, (int)configuration.getConf(intConf));
    Assert.assertEquals(123, configuration.getInt("ints", 100));

    // Long tests.
    ConfVar<Long> longConf = new ConfVar<>("long", 20L);
    Assert.assertEquals(20, (long)configuration.getConf(longConf));
    Assert.assertEquals(100l, configuration.getLong("longs", 100l));
    configuration.setConf(longConf, 900900900900L);
    configuration.set("longs", "12345678890123");
    Assert.assertEquals(900900900900L, (long)configuration.getConf(longConf));
    Assert.assertEquals(12345678890123L, configuration.getLong("longs", 100l));

    // Boolean tests.
    ConfVar<Boolean> boolConf = new ConfVar<>("bool", true);
    Assert.assertEquals(true, configuration.getConf(boolConf));
    Assert.assertEquals(false, configuration.getBool("bools", false));
    configuration.setConf(boolConf, false);
    configuration.set("bools", "true");
    Assert.assertEquals(false, configuration.getConf(boolConf));
    Assert.assertEquals(true, configuration.getBool("bools", false));

    // Enum tests
    ConfVar<TestEnum> enumConf = new ConfVar<>("enum", TestEnum.val1);
    Assert.assertEquals(TestEnum.val1, configuration.getConf(enumConf));
    Assert.assertEquals(TestEnum.val1, configuration.getEnum("enums", TestEnum.val1));
    configuration.setConf(enumConf, TestEnum.val2);
    configuration.set("enums", "val2");
    Assert.assertEquals(TestEnum.val2, configuration.getConf(enumConf));
    Assert.assertEquals(TestEnum.val2, configuration.getEnum("enums", TestEnum.val1));
  }
}