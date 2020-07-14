// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.eventProcessor;

import java.io.EOFException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.hive.ql.hooks.proto.HiveHookEvents.HiveHookEventProto;
import org.apache.hadoop.yarn.util.SystemClock;
import org.apache.tez.common.ATSConstants;
import org.apache.tez.dag.history.logging.proto.DatePartitionedLogger;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.HistoryEventProto;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.HistoryEventProto.Builder;
import org.apache.tez.dag.history.logging.proto.HistoryLoggerProtos.KVPair;
import org.apache.tez.dag.history.logging.proto.ProtoMessageReader;
import org.apache.tez.dag.history.logging.proto.ProtoMessageWriter;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.datatype.jdk8.Jdk8Module;

import io.dropwizard.cli.Command;
import io.dropwizard.setup.Bootstrap;
import lombok.Value;
import net.sourceforge.argparse4j.inf.Namespace;
import net.sourceforge.argparse4j.inf.Subparser;

public class EventsCopier  extends Command {

  private static ObjectMapper mapper = new ObjectMapper();

  protected EventsCopier() {
    super("eventcopy", "Copies tez and hive events into new files.");
    mapper.registerModule(new Jdk8Module());
  }

  @Override
  public void configure(Subparser subparser) {
    subparser.addArgument("--hive", "-e").type(String.class).required(true)
        .help("Hive events file.");
    subparser.addArgument("--query_id", "-q").type(String.class).required(true)
        .help("The hive query id to filter by.");
    subparser.addArgument("--tez", "-t").type(String.class).required(true)
        .help("Tez events file.");
    subparser.addArgument("--path", "-p").type(String.class).required(true)
        .help("The base dir to write the events into.");
    subparser.addArgument("--count", "-c").type(int.class).setDefault(-1)
        .help("Total count (default: -1, infinite)");
    subparser.addArgument("--start", "-s").type(int.class).setDefault(0)
        .help("Starting count value, used when resuming (default: 0)");
  }

  @Override
  public void run(Bootstrap<?> bootstrap, Namespace namespace) throws Exception {
    String hiveFile = namespace.getString("hive");
    String tezFile = namespace.getString("tez");
    int max = namespace.getInt("count");
    int start = namespace.getInt("start");
    String path = namespace.getString("path");
    String hqId = namespace.getString("query_id");

    Configuration conf = new Configuration();
    SystemClock clock = SystemClock.getInstance();

    DatePartitionedLogger<HiveHookEventProto> hiveLogger = new DatePartitionedLogger<>(
        HiveHookEventProto.PARSER, new Path(path + "/query_data"), conf, clock);
    DatePartitionedLogger<HistoryEventProto> tezLogger = new DatePartitionedLogger<>(
        HistoryEventProto.PARSER, new Path(path + "/dag_data"), conf, clock);

    List<HiveHookEventProto.Builder> hiveEvents = readHiveEvents(hiveLogger, hiveFile, hqId);
    if (hiveEvents.isEmpty()) {
      System.err.println("Cannot find queryId: " + hqId);
    }

    List<TezEventBuilders> tezEvents = readTezEvents(tezLogger, tezFile);
    if (tezEvents.isEmpty()) {
      System.err.println("Empty tez events files");
    }

    String fName = new Path(tezFile).getName();

    if (max < 0 || Integer.MAX_VALUE - start < 0) {
      max = Integer.MAX_VALUE - start;
    }
    max = max + start;

    for (int count = start; count < max; ++count) {
      String newHqId = hqId + count;
      copyHiveFile(hiveLogger, hiveEvents, newHqId);
      copyTezFile(tezLogger, tezEvents, count + start, newHqId, fName);
    }
  }

  private List<HiveHookEventProto.Builder> readHiveEvents(
      DatePartitionedLogger<HiveHookEventProto> hiveLogger, String hiveFile, String queryId)
          throws IOException {
    Path path = new Path(hiveFile);
    List<HiveHookEventProto.Builder> events = new ArrayList<>();
    try (ProtoMessageReader<HiveHookEventProto> hiveSource = hiveLogger.getReader(path)) {
      for (HiveHookEventProto evt = hiveSource.readEvent(); evt != null;
          evt = hiveSource.readEvent()) {
        if (evt.getHiveQueryId().equals(queryId)) {
          events.add(evt.toBuilder());
        }
      }
    } catch (EOFException e) {
      // Expected.
    }
    return events;
  }

  private void copyHiveFile(DatePartitionedLogger<HiveHookEventProto> hiveLogger,
      List<HiveHookEventProto.Builder> hiveEvents, String newHqId) throws IOException {
    try (ProtoMessageWriter<HiveHookEventProto> writer = hiveLogger.getWriter(newHqId)) {
      for (HiveHookEventProto.Builder evt : hiveEvents) {
        writer.writeProto(evt.setHiveQueryId(newHqId).build());
      }
    }
  }

  @Value
  static class TezEventBuilders {
    HistoryEventProto.Builder eventBuilder;
    KVPair.Builder kvBuilder;
    Map<String, String> vIdMapping;
  }

  private List<TezEventBuilders> readTezEvents(
      DatePartitionedLogger<HistoryEventProto> tezLogger, String tezFile) throws IOException {
    Path path = new Path(tezFile);
    List<TezEventBuilders> events = new ArrayList<>();
    try (ProtoMessageReader<HistoryEventProto> tezSource = tezLogger.getReader(path)) {
      for (HistoryEventProto evt = tezSource.readEvent(); evt != null;
          evt = tezSource.readEvent()) {
        HistoryEventProto.Builder builder = evt.toBuilder();
        KVPair.Builder kvBuilder = null;
        Map<String, String> vIdMapping = null;
        String evtType = evt.getEventType();
        if (evtType.equals("DAG_INITIALIZED")) {
          for (int i = 0 ; i < evt.getEventDataCount(); ++i) {
            KVPair evtData = evt.getEventData(i);
            if (evtData.getKey().equals(ATSConstants.VERTEX_NAME_ID_MAPPING)) {
              vIdMapping = mapper.readValue(evtData.getValue(), new TypeReference<Map<String, String>>() {});
              kvBuilder = builder.getEventDataBuilder(i);
            }
          }
        } else if (evtType.equals("DAG_FINISHED") || evtType.equals("DAG_SUBMITTED")) {
          for (int i = 0 ; i < builder.getEventDataCount(); ++i) {
            if (builder.getEventData(i).getKey().equals(ATSConstants.CALLER_CONTEXT_ID)) {
              kvBuilder = builder.getEventDataBuilder(i);
            }
          }
        }
        events.add(new TezEventBuilders(builder, kvBuilder, vIdMapping));
      }
    } catch (EOFException e) {
      // Expected.
    }
    return events;
  }

  private void copyTezFile(DatePartitionedLogger<HistoryEventProto> tezLogger,
      List<TezEventBuilders> tezEvents, int c, String newHiveQueryId, String fName)
          throws IOException {
    String suffix = "_" + c;
    try (ProtoMessageWriter<HistoryEventProto> writer = tezLogger.getWriter(fName + c)) {
      for (TezEventBuilders builders : tezEvents) {
        Builder builder = builders.eventBuilder;
        String oldDagId = builder.getDagId();
        String oldVertexId = null;
        builders.eventBuilder.setDagId(oldDagId + suffix);
        String evtType = builder.getEventType();
        if (evtType.equals("DAG_FINISHED") || evtType.equals("DAG_SUBMITTED")) {
          if (builders.kvBuilder != null) {
            builders.kvBuilder.setValue(newHiveQueryId);
          }
        }
        if (evtType.equals("DAG_INITIALIZED")) {
          if (builders.kvBuilder != null && builders.vIdMapping != null) {
            ObjectNode objNode = mapper.createObjectNode();
            for (Entry<String, String> entry : builders.vIdMapping.entrySet()) {
              objNode.put(entry.getKey(), entry.getValue() + suffix);
            }
            builders.kvBuilder.setValue(mapper.writeValueAsString(objNode));
          }
        }
        if (builder.hasVertexId()) {
          oldVertexId = builder.getVertexId();
          builder.setVertexId(oldVertexId + suffix);
        }
        writer.writeProto(builder.build());
        builder.setDagId(oldDagId);
        if (oldVertexId != null) {
          builder.setVertexId(oldVertexId);
        }
      }
    }
  }
}
