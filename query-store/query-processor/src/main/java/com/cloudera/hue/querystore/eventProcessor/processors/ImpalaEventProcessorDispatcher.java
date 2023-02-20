package com.cloudera.hue.querystore.eventProcessor.processors;

import javax.inject.Inject;

import org.apache.hadoop.fs.Path;

import com.cloudera.hue.querystore.eventProcessor.processors.impala.ImpalaQueryProfileProcessor;
import com.cloudera.ipe.model.impala.ImpalaRuntimeProfileTree;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ImpalaEventProcessorDispatcher implements EventProcessor<ImpalaRuntimeProfileTree> {
  private final ImpalaQueryProfileProcessor queryProfileProcessor;

  @Inject
  public ImpalaEventProcessorDispatcher(ImpalaQueryProfileProcessor queryProfileProcessor) {
    this.queryProfileProcessor = queryProfileProcessor;
  }

  @Override
  public ProcessingStatus process(ImpalaRuntimeProfileTree event, Path filePath) {
    log.info("Processing impala profile for query {}", event.getQueryId());

    ProcessingStatus processingStatus = null;

    // TODO: Better handling of each of the following states
    // Successful processing of event - SUCCESS
    // When process errored - ERROR
    // After processing last file event - FINISH

    if(queryProfileProcessor.process(event)) {
      processingStatus = ProcessingStatus.SUCCESS;
    } else {
      processingStatus = ProcessingStatus.FINISH;
    }

    return processingStatus;
  }
}
