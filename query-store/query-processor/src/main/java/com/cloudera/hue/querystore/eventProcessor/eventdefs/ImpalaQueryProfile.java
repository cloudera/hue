package com.cloudera.hue.querystore.eventProcessor.eventdefs;

import java.util.Map;

import com.cloudera.ipe.model.impala.ImpalaRuntimeProfileTree;
import com.cloudera.ipe.rules.ImpalaHDFSIOAnalysisRule;
import com.cloudera.ipe.rules.ImpalaInsertAnalysisRule;
import com.cloudera.ipe.rules.ImpalaMemoryUsageAnalysisRule;
import com.cloudera.ipe.rules.ImpalaResourceMetricsConverterAnalysisRule;
import com.cloudera.ipe.rules.ImpalaRuntimeProfile;
import com.cloudera.ipe.rules.ImpalaThreadTimeAnalysisRule;
import com.fasterxml.jackson.annotation.JsonIgnore;

import lombok.Getter;

public class ImpalaQueryProfile {
  @Getter
  @JsonIgnore
  private final ImpalaRuntimeProfileTree tree;

  private Map<String, String> summaryMap;
  private Map<String, String> hdfsMetrics;
  private Map<String, String> memoryMetrics;
  private Map<String, String> cpuMetrics;
  private Map<String, String> threadTimeMetrics;
  private Map<String, String> insertMetrics;

  public ImpalaQueryProfile(ImpalaRuntimeProfileTree tree) {
    this.tree = tree;
  }

  public String getQueryId() {
    return tree.getQueryId();
  }

  public Map<String, String> getSummaryMap() {
    if(summaryMap == null) {
      summaryMap = tree.getSummaryMap();
    }
    return summaryMap;
  }

  public Map<String, String> getHdfsMetrics() {
    if(hdfsMetrics == null) {
      ImpalaHDFSIOAnalysisRule hdfsioAnalysisRule = new ImpalaHDFSIOAnalysisRule();
      hdfsMetrics = hdfsioAnalysisRule.process(tree);
    }
    return hdfsMetrics;
  }

  public Map<String, String> getMemoryMetrics() {
    if(memoryMetrics == null) {
      ImpalaMemoryUsageAnalysisRule memoryUsageAnalysisRule = new ImpalaMemoryUsageAnalysisRule(
        ImpalaRuntimeProfile.DEFAULT_TIME_FORMATS);
      memoryMetrics = memoryUsageAnalysisRule.process(tree);
    }
    return memoryMetrics;
  }

  public Map<String, String> getCpuMetrics() {
    if(cpuMetrics == null) {
      ImpalaResourceMetricsConverterAnalysisRule resourceAnalysisRule = new ImpalaResourceMetricsConverterAnalysisRule();
      cpuMetrics = resourceAnalysisRule.process(tree);
    }
    return cpuMetrics;
  }

  public Map<String, String> getThreadTimeMetrics() {
    if(threadTimeMetrics == null) {
      ImpalaThreadTimeAnalysisRule threadTimeAnalysisRule = new ImpalaThreadTimeAnalysisRule(
        ImpalaRuntimeProfile.DEFAULT_TIME_FORMATS);
        threadTimeMetrics = threadTimeAnalysisRule.process(tree);
    }
    return threadTimeMetrics;
  }

  public Map<String, String> getInsertMetrics() {
    if(insertMetrics == null) {
      ImpalaInsertAnalysisRule insertAnalysisRule = new ImpalaInsertAnalysisRule();
      insertMetrics = insertAnalysisRule.process(tree);
    }
    return insertMetrics;
  }
}
