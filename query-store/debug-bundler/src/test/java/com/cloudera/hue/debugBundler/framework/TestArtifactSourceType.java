// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.framework;

import static org.junit.Assert.assertNotNull;
import static org.mockito.Mockito.mock;

import org.junit.Test;

import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezAppInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.VertexInfoRepository;
import com.google.inject.Binder;
import com.google.inject.Guice;
import com.google.inject.Injector;
import com.google.inject.Module;

public class TestArtifactSourceType {

  @Test(timeout=5000)
  public void testCreateAllTypes() {
    DasConfiguration conf = new DasConfiguration();
    HiveQueryBasicInfoRepository hiveQueryService = mock(HiveQueryBasicInfoRepository.class);
    HiveQueryExtendedInfoRepository queryDetailsService = mock(HiveQueryExtendedInfoRepository.class);
    TezDagBasicInfoRepository dagBasicRepo = mock(TezDagBasicInfoRepository.class);
    TezDagExtendedInfoRepository dagExtRepo = mock(TezDagExtendedInfoRepository.class);
    TezAppInfoRepository appRepo = mock(TezAppInfoRepository.class);
    VertexInfoRepository vertexRepo = mock(VertexInfoRepository.class);

    Injector injector = Guice.createInjector(new Module() {
      @Override
      public void configure(Binder binder) {
        binder.bind(DasConfiguration.class).toInstance(conf);
        binder.bind(HiveQueryBasicInfoRepository.class).toInstance(hiveQueryService);
        binder.bind(HiveQueryExtendedInfoRepository.class).toInstance(queryDetailsService);
        binder.bind(TezDagBasicInfoRepository.class).toInstance(dagBasicRepo);
        binder.bind(TezDagExtendedInfoRepository.class).toInstance(dagExtRepo);
        binder.bind(TezAppInfoRepository.class).toInstance(appRepo);
        binder.bind(VertexInfoRepository.class).toInstance(vertexRepo);
      }
    });
    for (ArtifactSourceType type : ArtifactSourceType.values()) {
      assertNotNull(type.getSource(injector));
    }
  }
}
