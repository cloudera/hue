// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.source;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import org.apache.http.client.HttpClient;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.junit.After;
import org.junit.Test;

import com.cloudera.hue.debugBundler.framework.Artifact;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.debugBundler.framework.Params.DagParams;
import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.google.common.collect.Lists;
import com.google.inject.Binder;
import com.google.inject.Guice;
import com.google.inject.Injector;
import com.google.inject.Module;

public class TestArtifacts {
  private final Injector injector;
  private final List<Path> tempFiles;

  public TestArtifacts() {
    CloseableHttpClient httpClient = HttpClients.createDefault();
    injector = Guice.createInjector(new Module() {
      @Override
      public void configure(Binder binder) {
        binder.bind(HttpClient.class).toInstance(httpClient);
        binder.bind(DasConfiguration.class).toInstance(new DasConfiguration());
      }
    });
    tempFiles = new ArrayList<>();
  }

  @After
  public void teardown() throws Exception {
    for (Path path : tempFiles) {
      Files.delete(path);
    }
    tempFiles.clear();
  }

  private InputStream getTempStream(String content) throws IOException {
    return new ByteArrayInputStream(content.getBytes(Charset.forName("UTF-8")));
  }

  @Test(timeout=5000)
  public void testLlapDeamonLogsListArtifacts() throws Exception {
    LlapDeamonLogsListArtifacts source = injector.getInstance(
        LlapDeamonLogsListArtifacts.class);
    Params params = new Params();
    params.setHiveQueryId("hqid-1");

    assertFalse(source.hasRequiredParams(params));
    params.setAppType("LLAP");
    DagParams param = new DagParams(0, null, null);
    params.getDagParams().add(param);
    Params.AppLogs taskLogs = param.getTaskLogs();
    taskLogs.addContainer("test-node-id-1:8888", "test-container-id-1");
    taskLogs.addContainer("test-node-id-1:8888", "test-container-id-2");
    taskLogs.addContainer("test-node-id-2:8888", "test-container-id-3");
    taskLogs.finishContainers();

    assertTrue(source.hasRequiredParams(params));

    List<Artifact> artifacts = source.getArtifacts(params);
    assertEquals(3, artifacts.size());

    InputStream stream = getTempStream("{\"containerLogsInfo\":{\"containerLogInfo\":[{\"fileName\":\"launch_container.sh\",\"fileSize\":\"4245\",\"lastModifiedTime\":\"Tue Jul 04 05:51:44 +0000 2017\"},{\"fileName\":\"directory.info\",\"fileSize\":\"10843\",\"lastModifiedTime\":\"Tue Jul 04 05:51:44 +0000 2017\"},{\"fileName\":\"slider-agent.out\",\"fileSize\":\"45\",\"lastModifiedTime\":\"Tue Jul 04 05:51:45 +0000 2017\"},{\"fileName\":\"slider-agent.log\",\"fileSize\":\"29998\",\"lastModifiedTime\":\"Tue Jul 04 05:52:02 +0000 2017\"},{\"fileName\":\"command-1.json\",\"fileSize\":\"6974\",\"lastModifiedTime\":\"Tue Jul 04 05:51:56 +0000 2017\"},{\"fileName\":\"output-1.txt\",\"fileSize\":\"1656\",\"lastModifiedTime\":\"Tue Jul 04 05:51:56 +0000 2017\"},{\"fileName\":\"errors-1.txt\",\"fileSize\":\"0\",\"lastModifiedTime\":\"Tue Jul 04 05:51:56 +0000 2017\"},{\"fileName\":\"command-2.json\",\"fileSize\":\"6937\",\"lastModifiedTime\":\"Tue Jul 04 05:52:00 +0000 2017\"},{\"fileName\":\"output-2.txt\",\"fileSize\":\"162\",\"lastModifiedTime\":\"Tue Jul 04 05:52:00 +0000 2017\"},{\"fileName\":\"errors-2.txt\",\"fileSize\":\"0\",\"lastModifiedTime\":\"Tue Jul 04 05:52:00 +0000 2017\"},{\"fileName\":\"shell.out\",\"fileSize\":\"2999\",\"lastModifiedTime\":\"Tue Jul 04 05:52:00 +0000 2017\"},{\"fileName\":\"llap-daemon-hive-ctr-e133-1493418528701-155152-01-000004.hwx.site.out\",\"fileSize\":\"14021\",\"lastModifiedTime\":\"Tue Jul 04 06:10:26 +0000 2017\"},{\"fileName\":\"status_command_stdout.txt\",\"fileSize\":\"0\",\"lastModifiedTime\":\"Tue Jul 04 06:41:27 +0000 2017\"},{\"fileName\":\"status_command_stderr.txt\",\"fileSize\":\"0\",\"lastModifiedTime\":\"Tue Jul 04 06:41:27 +0000 2017\"},{\"fileName\":\"gc.log.0.current\",\"fileSize\":\"8559\",\"lastModifiedTime\":\"Tue Jul 04 06:09:46 +0000 2017\"},{\"fileName\":\"llapdaemon_history.log\",\"fileSize\":\"2132\",\"lastModifiedTime\":\"Tue Jul 04 06:10:26 +0000 2017\"},{\"fileName\":\"llap-daemon-hive-ctr-e133-1493418528701-155152-01-000004.hwx.site.log_2017-07-04-05_1.done\",\"fileSize\":\"41968\",\"lastModifiedTime\":\"Tue Jul 04 05:53:13 +0000 2017\"},{\"fileName\":\"llap-daemon-hive-ctr-e133-1493418528701-155152-01-000004.hwx.site.log\",\"fileSize\":\"16357\",\"lastModifiedTime\":\"Tue Jul 04 06:10:26 +0000 2017\"},{\"fileName\":\"hive_20170704060941_28dd6d01-2d6c-46f8-964b-e57f26e720ff-dag_1499147207464_0004_1.log.done\",\"fileSize\":\"16967\",\"lastModifiedTime\":\"Tue Jul 04 06:09:47 +0000 2017\"},{\"fileName\":\"hive_20170704061024_bf72f7f6-5684-4e16-95ff-8725e7eba4cf-dag_1499147207464_0004_2.log.done\",\"fileSize\":\"34530\",\"lastModifiedTime\":\"Tue Jul 04 06:10:26 +0000 2017\"},{\"fileName\":\"hive_20170704061024_bf72f7f6-5684-4e16-95ff-8725e7eba4cf-dag_1499147207464_0004_2.log\",\"fileSize\":\"176\",\"lastModifiedTime\":\"Tue Jul 04 06:10:26 +0000 2017\"},{\"fileName\":\"status_command.json\",\"fileSize\":\"2896\",\"lastModifiedTime\":\"Tue Jul 04 06:41:27 +0000 2017\"}],\"logAggregationType\":\"LOCAL\",\"containerId\":\"container_1499147207464_0003_01_000002\",\"nodeId\":\"ctr-e133-1493418528701-155152-01-000004.hwx.site:45454\"}}");
    source.updateParams(params, artifacts.get(0), stream);
    Params.AppLogs logs = param.getTaskLogs();
    assertTrue(logs.isFinishedLogs());
  }

  @Test(timeout=5000)
  public void testLlapDeamonLogsArtifacts() throws Exception {
    LlapDeamonLogsArtifacts source = injector.getInstance(LlapDeamonLogsArtifacts.class);
    Params params = new Params();

    assertFalse(source.hasRequiredParams(params));
    params.setAppType("LLAP");
    DagParams param = new DagParams(0, null, null);
    params.getDagParams().add(param);
    Params.AppLogs taskLogs = param.getTaskLogs();

    taskLogs.addLog("test-node-id-1:8888", "test-container-id-0", "LOCAL",
      Lists.newArrayList(
          new Params.ContainerLogInfo("test-file-0", 100, "01-01-2017")));

    // Non aggregated file, must be replaced with aggregated file
    taskLogs.addLog("test-node-id-1:8888", "test-container-id-1", "LOCAL",
      Lists.newArrayList(
          new Params.ContainerLogInfo("test-file-1", 100, "01-01-2017")));
    taskLogs.addLog("test-node-id-1:8888", "test-container-id-1", "AGGREGATED",
        Lists.newArrayList(
          new Params.ContainerLogInfo("test-file-1", 10, "01-01-2017")));

    taskLogs.addLog("test-node-id-2:8888", "test-container-id-2","AGGREGATED",
        Lists.newArrayList(
          new Params.ContainerLogInfo("test-file-1", 10, "01-01-2017"),
          new Params.ContainerLogInfo("test-file-2", 10, "01-01-2017")));
    taskLogs.finishLogs();

    assertTrue(source.hasRequiredParams(params));

    List<Artifact> artifacts = source.getArtifacts(params);
    assertEquals(4, artifacts.size());
  }
}
