package com.cloudera.hue.querystore.eventProcessor.processors.impala;

import com.cloudera.hue.querystore.common.entities.ImpalaQueryEntity;
import com.cloudera.hue.querystore.common.repository.ImpalaQueryRepository;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.ipe.IPEConstants;
import com.cloudera.ipe.model.impala.ImpalaRuntimeProfileTree;
import com.cloudera.ipe.rules.ImpalaHDFSIOAnalysisRule;
import com.cloudera.ipe.rules.ImpalaMemoryUsageAnalysisRule;
import com.cloudera.ipe.rules.ImpalaRuntimeProfile;
import com.cloudera.ipe.rules.ImpalaThreadTimeAnalysisRule;

import java.net.URI;
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

  @Inject
  public ImpalaQueryProfileProcessor(Provider<ImpalaQueryRepository> impalaQueryRepositoryProvider) {
    this.impalaQueryRepositoryProvider = impalaQueryRepositoryProvider;
  }

  @DASTransaction
  public ProcessingStatus process(ImpalaRuntimeProfileTree tree, Path sourceFile) {

    Map<String, String> details = tree.getSummaryMap();

    ImpalaHDFSIOAnalysisRule hdfsioAnalysisRule = new ImpalaHDFSIOAnalysisRule();
    Map<String, String> hdfsMetrics = hdfsioAnalysisRule.process(tree);

    ImpalaMemoryUsageAnalysisRule memoryUsageAnalysisRule = new ImpalaMemoryUsageAnalysisRule(
        ImpalaRuntimeProfile.DEFAULT_TIME_FORMATS);
    Map<String, String> memoryMetrics = memoryUsageAnalysisRule.process(tree);

    // Uncomment if some value need to be taken from cpuMetrics
    // ImpalaResourceMetricsConverterAnalysisRule resourceAnalysisRule = new ImpalaResourceMetricsConverterAnalysisRule();
    // Map<String, String> cpuMetrics = resourceAnalysisRule.process(tree);

    ImpalaThreadTimeAnalysisRule threadTimeAnalysisRule = new ImpalaThreadTimeAnalysisRule(
        ImpalaRuntimeProfile.DEFAULT_TIME_FORMATS);
    Map<String, String> threadTimeMetrics = threadTimeAnalysisRule.process(tree);

    // Uncomment if some value need to be taken from insertMetrics
    // ImpalaInsertAnalysisRule insertAnalysisRule = new ImpalaInsertAnalysisRule();
    // Map<String, String> insertMetrics = insertAnalysisRule.process(tree);

    ImpalaQueryEntity entity = new ImpalaQueryEntity();

    entity.setQueryId(tree.getQueryId());
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
    entity.setRowsProduced(tree.getRowsProduced());
    entity.setPeakMemory(parseLong(memoryMetrics.get(PropKey.MEMORY_PER_NODE_PEAK)));
    entity.setHdfsBytesRead(parseLong(hdfsMetrics.get(PropKey.HDFS_BYTES_READ)));

    URI sourceFileUri = URI.create(sourceFile.toString());
    entity.setSourceFile(sourceFileUri.getPath());

    ImpalaQueryRepository impalaQueryRepository = impalaQueryRepositoryProvider.get();
    impalaQueryRepository.save(entity);

    return ProcessingStatus.SUCCESS;
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
    String QUERY_STATE = "Impala Query State";
    String QUERY_TYPE = "Query Type";

    String USER = "User";
    String COORDINATOR = "Coordinator";

    String THREAD_CPU_TIME = "thread_cpu_time";
    String MEMORY_PER_NODE_PEAK = "memory_per_node_peak";
    String HDFS_BYTES_READ = "hdfs_bytes_read";
  }
}
