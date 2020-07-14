// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.tez;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.hive.ql.hooks.HiveProtoLoggingHook;
import org.apache.tez.common.ATSConstants;

import com.cloudera.hue.querystore.common.dto.Counter;
import com.cloudera.hue.querystore.common.dto.CounterGroup;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagExtendedInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.TezHSEvent;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventProcessor;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.util.ProcessorHelper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DagFinishedProcessor implements TezEventProcessor {

  private final ProcessorHelper helper;
  private final Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider;
  private final Provider<TezDagExtendedInfoRepository> dagDetailsRepositoryProvider;
  private final Provider<HiveQueryBasicInfoRepository> hiveQueryRepository;
  private final ObjectMapper objectMapper;


  @Inject
  public DagFinishedProcessor(ProcessorHelper helper,
                              Provider<TezDagBasicInfoRepository> dagInfoRepositoryProvider,
                              Provider<TezDagExtendedInfoRepository> dagDetailsRepositoryProvider,
                              Provider<HiveQueryBasicInfoRepository> hiveQueryRepository,
                              ObjectMapper objectMapper) {
    this.helper = helper;
    this.dagInfoRepositoryProvider = dagInfoRepositoryProvider;
    this.dagDetailsRepositoryProvider = dagDetailsRepositoryProvider;
    this.hiveQueryRepository = hiveQueryRepository;
    this.objectMapper = objectMapper;
  }

  @Override
  @DASTransaction
  public ProcessingStatus processValidEvent(TezHSEvent event, Path filePath) {
    TezDagBasicInfoRepository dagInfoRepository = dagInfoRepositoryProvider.get();
    TezDagExtendedInfoRepository dagDetailsRepository = dagDetailsRepositoryProvider.get();

    String dagId = event.getDagId();
    Optional<TezDagBasicInfo> dagInfoOptional = dagInfoRepository.findByDagId(dagId);

    if (!dagInfoOptional.isPresent()) {
      log.error("Dag Information not found for dag id: {}. Cannot process event", dagId);
      return new ProcessingStatus(new RuntimeException("Dag Info not found for dagId: " + dagId));
    }

    TezDagBasicInfo dagInfo = dagInfoOptional.get();

    Map<String, String> otherInfo = event.getOtherInfo();
    dagInfo.setEndTime(event.getEventTime());
    String otherStatus = otherInfo.get(ATSConstants.STATUS);
    TezDagBasicInfo.Status status = TezDagBasicInfo.Status.valueOf(otherStatus.toUpperCase());
    dagInfo.setStatus(status.name());
    dagInfo.setSourceFile(filePath.toString());

    ArrayNode counters = getCounters(otherInfo.get(ATSConstants.COUNTERS));
    updateHiveQueryData(dagInfo, counters);

    Optional<TezDagExtendedInfo> dagDetailsOptional = dagDetailsRepository.findByDagId(dagId);
    if (dagDetailsOptional.isPresent()) {
      TezDagExtendedInfo dagDetails = dagDetailsOptional.get();
      dagDetails.setCounters(counters);
      dagDetails.setDiagnostics(otherInfo.get(ATSConstants.DIAGNOSTICS));
      dagDetailsRepository.save(dagDetails);
    }

    dagInfoRepository.save(dagInfo);
    return ProcessingStatus.FINISH;
  }

  @VisibleForTesting
  protected Map<String, CounterGroup> getCounterGroupMap(ArrayNode counters) {
    Map<String, CounterGroup> map = new HashMap<>();
    for (JsonNode node : counters) {
      try {
        CounterGroup counterGroup = objectMapper.treeToValue(node, CounterGroup.class);
        map.put(counterGroup.getName(), counterGroup);
      } catch (JsonProcessingException e) {
        log.error("Failed to process json node for getting counters. {}", e);
      }
    }
    return map;
  }


  private void updateHiveQueryData(TezDagBasicInfo dagInfo, ArrayNode counters) {
    Long endTime = dagInfo.getEndTime();

    Map<String, CounterGroup> groupMap = getCounterGroupMap(counters);
    Long cpuTimeFromCounters = getCpuTimeFromCounters(groupMap);
    Long physicalMemoryFromCounters = getPhysicalMemoryFromCounters(groupMap);
    Long virtualMemoryFromCounters = getVirtualMemoryFromCounters(groupMap);
    Long dataReadFromCounters = getDataReadFromCounters(groupMap);
    Long dataWrittenFromCounters = getDataWrittenFromCounters(groupMap);

    Long id = dagInfo.getHiveQueryId();
    HiveQueryBasicInfoRepository queryRepository = hiveQueryRepository.get();

    Optional<HiveQueryBasicInfo> hiveQueryOptional = queryRepository.findOne(id);
    if (hiveQueryOptional.isPresent()) {
      HiveQueryBasicInfo hiveQuery = hiveQueryOptional.get();
      if (TezDagBasicInfo.Status.KILLED.name().equals(dagInfo.getStatus())) {
        if (!HiveQueryBasicInfo.Status.SUCCESS.name().equals(hiveQuery.getStatus())) {
          hiveQuery.setStatus(HiveQueryBasicInfo.Status.ERROR.name());
        }
      }

      updateResourceUtilizationInHiveQuery(groupMap, hiveQuery);
      hiveQuery.setEndTime(endTime);
      hiveQuery.setCpuTime(cpuTimeFromCounters);
      hiveQuery.setPhysicalMemory(physicalMemoryFromCounters);
      hiveQuery.setVirtualMemory(virtualMemoryFromCounters);
      hiveQuery.setDataRead(dataReadFromCounters);
      hiveQuery.setDataWritten(dataWrittenFromCounters);
      queryRepository.save(hiveQuery);
      log.info("updating stats of hive_query with id {}.", id);
    } else {
      log.error("Could not find the hive_query with id : {}", id);
    }
  }

  @VisibleForTesting
  protected void updateResourceUtilizationInHiveQuery(Map<String, CounterGroup> counters, HiveQueryBasicInfo hiveQuery) {
    String executionMode = hiveQuery.getExecutionMode();
    if (null != executionMode) {
      Long resourceUtilization = 0L;
      if (executionMode.equals(HiveProtoLoggingHook.ExecutionMode.LLAP.name())) {
        resourceUtilization += getValueFromCounters(counters.get("org.apache.hadoop.hive.llap.counters.LlapWmCounters"), "SPECULATIVE_RUNNING_NS") / 1000_000;
        resourceUtilization += getValueFromCounters(counters.get("org.apache.tez.common.counters.DAGCounter"), "AM_CPU_MILLISECONDS");
      } else if (executionMode.equals(HiveProtoLoggingHook.ExecutionMode.TEZ.name())) {
        resourceUtilization += getValueFromCounters(counters.get("org.apache.tez.common.counters.TaskCounter"), "CPU_MILLISECONDS");
        resourceUtilization += getValueFromCounters(counters.get("org.apache.tez.common.counters.DAGCounter"), "AM_CPU_MILLISECONDS");
      }
      hiveQuery.setResourceUtilization(resourceUtilization);
    }
  }


  private ArrayNode getCounters(String counters) {
    ObjectNode countersNode = helper.parseData(counters, ObjectNode.class);
    return (ArrayNode) countersNode.get("counterGroups");
  }

//  TODO: Verify this logic of adding both the CPU_MILLIS comes in both DAG and Task Counters.
  private Long getCpuTimeFromCounters(Map<String, CounterGroup> groupMap) {
    CounterGroup dagCounters = groupMap.get("org.apache.tez.common.counters.DAGCounter");
    CounterGroup taskCounters = groupMap.get("org.apache.tez.common.counters.TaskCounter");
    Long cpuMillisDag = getValueFromCounters(dagCounters, "CPU_MILLISECONDS");
    Long cpuMillistasks = getValueFromCounters(taskCounters, "CPU_MILLISECONDS");
    return cpuMillisDag + cpuMillistasks;
  }

  private Long getValueFromCounters(CounterGroup counterGroup, String name) {
    if (counterGroup != null) {
      for (Counter counter : counterGroup.getCounters()) {
        if (counter.getName().equalsIgnoreCase(name)) {
          return Long.valueOf(counter.getValue());
        }
      }
    }
    return 0L;
  }

  private Long getDataWrittenFromCounters(Map<String, CounterGroup> groupMap) {
    CounterGroup fileSystemCounters = groupMap.get("org.apache.tez.common.counters.FileSystemCounter");
    return getValueFromCounters(fileSystemCounters, "HDFS_BYTES_READ") +
            getValueFromCounters(fileSystemCounters, "S3A_BYTES_READ");
  }

  private Long getDataReadFromCounters(Map<String, CounterGroup> groupMap) {
    CounterGroup fileSystemCounters = groupMap.get("org.apache.tez.common.counters.FileSystemCounter");
    return getValueFromCounters(fileSystemCounters, "HDFS_BYTES_WRITTEN") +
            getValueFromCounters(fileSystemCounters, "S3A_BYTES_WRITTEN");
  }

  private Long getVirtualMemoryFromCounters(Map<String, CounterGroup> groupMap) {
    CounterGroup taskCounters = groupMap.get("org.apache.tez.common.counters.TaskCounter");
    return getValueFromCounters(taskCounters, "VIRTUAL_MEMORY_BYTES");
  }

  private Long getPhysicalMemoryFromCounters(Map<String, CounterGroup> groupMap) {
    CounterGroup taskCounters = groupMap.get("org.apache.tez.common.counters.TaskCounter");
    return getValueFromCounters(taskCounters, "PHYSICAL_MEMORY_BYTES");
  }

  @Override
  public TezEventType[] validEvents() {
    return new TezEventType[]{TezEventType.DAG_FINISHED};
  }
}
