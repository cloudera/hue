// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor.processors.util;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import javax.inject.Inject;

import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.cloudera.hue.querystore.eventProcessor.processors.HiveEventType;
import com.cloudera.hue.querystore.eventProcessor.processors.TezEventType;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Sets;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ProcessorHelper {

  private final ObjectMapper objectMapper;

  @Inject
  public ProcessorHelper(ObjectMapper objectMapper) {
    this.objectMapper = objectMapper;
  }

  public ArrayNode processTablesReadWrite(List<String> tables) {
    if (tables == null) {
      return objectMapper.createArrayNode();
    }
    List<ObjectNode> tableNodes = tables.stream().map(x -> {
      ObjectNode table = objectMapper.createObjectNode();
      String[] split = x.split("\\.");
      table.put("database", split[0]);
      table.put("table", split[1]);
      return table;
    }).collect(Collectors.toList());

    return objectMapper.createArrayNode().addAll(tableNodes);
  }

  public Map<String, Integer> getDatabasesUsedInQuery(List<String> tablesRead, List<String> tablesWritten) {
    Map<String, Integer> databasesWithCount = new HashMap<>();
    updateDBCount(databasesWithCount, tablesRead);
    updateDBCount(databasesWithCount, tablesWritten);
    return databasesWithCount;
  }

  private static void updateDBCount(Map<String, Integer> dbCount, List<String> tableNames) {
    if (tableNames == null) {
      return;
    }
    for (String tableName : tableNames) {
      String[] split = tableName.split("\\.");
      String db = split[0];
      int curVal;
      if (dbCount.containsKey(db)) {
        curVal = dbCount.get(db);
        dbCount.put(db, curVal + 1);
      } else {
        dbCount.put(db, 1);
      }
    };
  }

  public <T> T parseData(String data, Class<T> klass) {
    if(data == null || klass == null) {
      return null;
    }
    try {
      return objectMapper.readValue(data, klass);
    } catch (IOException e) {
      log.error("Failed to parse data: {}", e);
      return null;
    }
  }

  public boolean isValidEvent(String extractedEventType, HiveEventType... validEventType) {
    try {
      return Sets.newHashSet(validEventType).contains(HiveEventType.valueOf(extractedEventType.toUpperCase()));
    } catch (IllegalArgumentException ex) {
      return false;
    }
  }

  public boolean isValidEvent(String extractedEventType, TezEventType... validEventType) {
    try {
      return Sets.newHashSet(validEventType).contains(TezEventType.valueOf(extractedEventType.toUpperCase()));
    } catch (IllegalArgumentException ex) {
      return false;
    }
  }


  public void updateWaitingTime(HiveQueryExtendedInfo details, HiveQueryBasicInfo hiveQuery){
    Long compilationTime = this.getCompilationTime(details);
    long waitingTime = hiveQuery.getFirstTaskStartedTime() - hiveQuery.getStartTime() - compilationTime;
    hiveQuery.setWaitingTime(waitingTime);
  }

  public Long getCompilationTime(HiveQueryExtendedInfo queryDetails) {
    ObjectNode perfJson = queryDetails.getPerf();
    long compilationTime = 0;
    if(null == perfJson){
      log.warn("received perfJson as null in queryDetails : {}", queryDetails);
      return compilationTime;
    }
    JsonNode parseTime = perfJson.get("parse");

    if(null != parseTime){
      compilationTime += parseTime.longValue();
    }

    JsonNode compileTime = perfJson.get("compile");
    if(null != compileTime){
      compilationTime += compileTime.longValue();
    }

    JsonNode dagBuildTime = perfJson.get("TezBuildDag");
    if(null != dagBuildTime){
      compilationTime += dagBuildTime.longValue();
    }

    return compilationTime;
  }
}
