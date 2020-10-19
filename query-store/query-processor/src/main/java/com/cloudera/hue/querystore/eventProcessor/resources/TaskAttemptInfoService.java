// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.resources;

import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.entities.VertexInfo;
import com.cloudera.hue.querystore.common.repository.VertexInfoRepository;
import com.cloudera.hue.querystore.common.services.DagInfoService;
import com.google.common.collect.MinMaxPriorityQueue;

import com.cloudera.hue.debugBundler.framework.HistoryEventReader;
import com.cloudera.hue.debugBundler.framework.HistoryEventReader.HistoryEventIterator;

import org.apache.commons.lang.StringUtils;
import org.apache.hadoop.fs.Path;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.HistoryEventProto;

import javax.inject.Inject;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Optional;

/**
 * Service to fetch Task Attempt information
 */
public class TaskAttemptInfoService {

  protected static final String STATUS_KEY = "status";
  protected static final String START_EVENT = "TASK_ATTEMPT_STARTED";
  protected static final String FINISH_EVENT = "TASK_ATTEMPT_FINISHED";

  private static final HashSet<String> STARTED_EVENT_KEYSET = new HashSet<>(
    Arrays.asList("inProgressLogsURL", "containerId", "nodeId", "status"));
  private static final HashSet<String> FINISHED_EVENT_KEYSET = new HashSet<>(
    Arrays.asList("timeTaken", "diagnostics", "startTime", "status"));

  private final VertexInfoRepository vertexInfoService;
  private final DagInfoService dagInfoService;
  private final HistoryEventReader historyEventReader;

  @Inject
  public TaskAttemptInfoService(VertexInfoRepository vertexInfoService, DagInfoService dagInfoService,
                                HistoryEventReader historyEventReader) {
    this.vertexInfoService = vertexInfoService;
    this.dagInfoService = dagInfoService;
    this.historyEventReader = historyEventReader;
  }

  private HashMap<String, String> constructDataMap(HistoryEventProto event,
                                                   HashSet<String> dataListKeySet) {
    HashMap<String, String> map = new HashMap<>();

    for (HistoryLoggerProtos.KVPair kvPair : event.getEventDataList()) {
      if(dataListKeySet.contains(kvPair.getKey())) {
        map.put(kvPair.getKey(), kvPair.getValue());
      }
    }

    map.put("taskId", event.getTaskId());
    map.put("taskAttemptId", event.getTaskAttemptId());

    return map;
  }

  public ArrayList<HashMap<String, String>> getAttempts(String vertexId) throws IOException {
    return getAttempts(vertexId, null, null, 20);
  }

  public ArrayList<HashMap<String, String>> getAttempts(String vertexId, String status,
                                                       String sort, int limit) throws IOException {
    Optional<VertexInfo> vertexInfoOptional = vertexInfoService.findByVertexId(vertexId);
    if(!vertexInfoOptional.isPresent()) {
      throw new RuntimeException("Vertex Information with id '" + vertexId + "' not found");
    }
    Optional<TezDagBasicInfo> dagOptional = dagInfoService.findOne(vertexInfoOptional.get().getDagId());
    TezDagBasicInfo dag = dagOptional.get();
    HashMap<String, HashMap<String, String>> startEventHash = new HashMap<>();
    HashMap<String, String> data;

    if (StringUtils.isEmpty(sort)) {
      sort = "startTime";
    }

    int sortOrder = sort.endsWith(":desc") ? -1 : 1;
    String sortField = sort.split(":")[0];

    MinMaxPriorityQueue<HashMap<String, String>> resultHeap = MinMaxPriorityQueue.orderedBy(
      (HashMap<String, String> h1,HashMap<String, String> h2) -> {
        Long val1 = h1.containsKey(sortField) ? Long.parseLong(h1.get(sortField)) : 0;
        Long val2 = h2.containsKey(sortField) ? Long.parseLong(h2.get(sortField)) : 02;
        return Long.compare(val1, val2) * sortOrder;
      }).maximumSize(limit).create();

    HistoryEventIterator iterator = historyEventReader.getIterator(new Path(dag.getSourceFile()));
    while(iterator.hasNext()) {
      HistoryEventProto event = iterator.next();
      String taskAttemptId = event.getTaskAttemptId();

      if(vertexId.equals(event.getVertexId())) {
        switch(event.getEventType()) {
          case START_EVENT:
            data = constructDataMap(event, STARTED_EVENT_KEYSET);
            data.put("startTime", String.valueOf(event.getEventTime()));
            startEventHash.put(taskAttemptId, data);
            break;
          case FINISH_EVENT:
            data = startEventHash.remove(taskAttemptId);
            data.putAll(constructDataMap(event, FINISHED_EVENT_KEYSET));
            data.put("finishTime", String.valueOf(event.getEventTime()));

            if(StringUtils.isEmpty(status) || status.equals(data.get(STATUS_KEY))) {
              resultHeap.add(data);
            }
            break;
        }
      }
    }
    iterator.close();

    for (HashMap<String, String> startEventData : startEventHash.values()) {
      if(StringUtils.isEmpty(status) || status.equals(startEventData.get(STATUS_KEY))) {
        resultHeap.add(startEventData);
      }
    }

    ArrayList<HashMap<String, String>> result = new ArrayList<>();
    while(resultHeap.size() > 0) {
      result.add(resultHeap.poll());
    }

    return result;
  }

}
