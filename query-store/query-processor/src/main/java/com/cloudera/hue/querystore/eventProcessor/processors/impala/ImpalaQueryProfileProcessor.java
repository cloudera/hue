package com.cloudera.hue.querystore.eventProcessor.processors.impala;

import com.cloudera.hue.querystore.common.entities.ImpalaQueryEntity;
import com.cloudera.hue.querystore.common.repository.ImpalaQueryRepository;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.hue.querystore.eventProcessor.eventdefs.ImpalaQueryProfile;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.ipe.IPEConstants;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.inject.Inject;
import javax.inject.Provider;

import org.apache.hadoop.fs.Path;
import org.joda.time.DateTimeZone;
import org.joda.time.Instant;
import org.joda.time.format.DateTimeFormat;
import org.joda.time.format.DateTimeFormatter;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ImpalaQueryProfileProcessor {
  private final Provider<ImpalaQueryRepository> impalaQueryRepositoryProvider;
  private final ObjectMapper objectMapper;

  @Inject
  public ImpalaQueryProfileProcessor(Provider<ImpalaQueryRepository> impalaQueryRepositoryProvider, ObjectMapper objectMapper) {
    this.impalaQueryRepositoryProvider = impalaQueryRepositoryProvider;
    this.objectMapper = objectMapper;
  }

  @DASTransaction
  public ProcessingStatus process(ImpalaQueryProfile profile, Path sourceFile, Long eventOffset) {

    Map<String, String> details = profile.getSummaryMap();
    Map<String, String> hdfsMetrics = profile.getHdfsMetrics();
    Map<String, String> memoryMetrics = profile.getMemoryMetrics();
    Map<String, String> threadTimeMetrics = profile.getThreadTimeMetrics();

    ImpalaQueryEntity entity = new ImpalaQueryEntity();

    entity.setQueryId(profile.getQueryId());
    entity.setQueryText(details.get(PropKey.SQL_STATEMENT));
    entity.setStatus(details.get(PropKey.QUERY_STATE));
    entity.setQueryType(details.get(PropKey.QUERY_TYPE));

    Long startTime = parseTime(details.get(IPEConstants.IMPALA_START_TIME_INFO_STRING));
    Long endTime = parseTime(details.get(IPEConstants.IMPALA_END_TIME_INFO_STRING));
    entity.setStartTime(startTime);
    entity.setEndTime(endTime);
    if(startTime != null && endTime != null) {
      entity.setDuration(endTime - startTime);
    }

    entity.setUserName(details.get(PropKey.USER));
    entity.setCoordinator(details.get(PropKey.COORDINATOR));

    entity.setCpuTime(parseLong(threadTimeMetrics.get(PropKey.THREAD_CPU_TIME)));
    entity.setRowsProduced(profile.getTree().getRowsProduced());
    entity.setPeakMemory(parseLong(memoryMetrics.get(PropKey.MEMORY_PER_NODE_PEAK)));
    entity.setHdfsBytesRead(parseLong(hdfsMetrics.get(PropKey.HDFS_BYTES_READ)));

    entity.setSource(buildSource(sourceFile, eventOffset));

    ImpalaQueryRepository impalaQueryRepository = impalaQueryRepositoryProvider.get();
    impalaQueryRepository.save(entity);

    return ProcessingStatus.SUCCESS;
  }

  private ObjectNode buildSource(Path sourceFile, Long eventOffset) {
    Map<String, List<Long>> source = new HashMap<>();
    source.put(sourceFile.toString(), Arrays.asList(eventOffset));
    return objectMapper.convertValue(source, ObjectNode.class);
  }

  private Long parseLong(String value) {
    try {
      double d = Double.parseDouble(value);
      return (long) d; // To gracefully remove decimal values if any
    } catch(NumberFormatException | NullPointerException e) {
      return null;
    }
  }

  public static final DateTimeFormatter TIME_FORMATTER = DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss.SSS")
      .withZone(DateTimeZone.UTC);
  private static Long parseTime(String timeString) {
    try {
      if(timeString.lastIndexOf(".") == timeString.length() - 10) {
        // Remove nano seconds if present
        timeString = timeString.substring(0, timeString.length() - 6);
      }
      return Instant.parse(timeString, TIME_FORMATTER).getMillis();
    } catch (IllegalArgumentException e) {
      return null;
    }
  }

  interface PropKey {
    String SQL_STATEMENT = "Sql Statement";
    String QUERY_STATE = "Query State";
    String QUERY_TYPE = "Query Type";

    String USER = "User";
    String COORDINATOR = "Coordinator";

    String THREAD_CPU_TIME = "thread_cpu_time";
    String MEMORY_PER_NODE_PEAK = "memory_per_node_peak";
    String HDFS_BYTES_READ = "hdfs_bytes_read";
  }
}
