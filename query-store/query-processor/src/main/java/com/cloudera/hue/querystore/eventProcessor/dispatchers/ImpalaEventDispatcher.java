package com.cloudera.hue.querystore.eventProcessor.dispatchers;

import javax.inject.Inject;

import org.apache.hadoop.fs.Path;

import com.cloudera.hue.querystore.eventProcessor.eventdefs.ImpalaQueryProfile;
import com.cloudera.hue.querystore.eventProcessor.processors.ProcessingStatus;
import com.cloudera.hue.querystore.eventProcessor.processors.impala.ImpalaQueryProfileProcessor;
import com.cloudera.ipe.model.impala.ImpalaRuntimeProfileTree;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ImpalaEventDispatcher implements EventDispatcher<ImpalaRuntimeProfileTree> {
  private final ImpalaQueryProfileProcessor queryProfileProcessor;

  @Inject
  public ImpalaEventDispatcher(ImpalaQueryProfileProcessor queryProfileProcessor) {
    this.queryProfileProcessor = queryProfileProcessor;
  }

  @Override
  public ProcessingStatus process(ImpalaRuntimeProfileTree event, Path filePath, Long eventOffset) {
    log.info("Processing impala profile for query {}", event.getQueryId());

    ImpalaQueryProfile profile = new ImpalaQueryProfile(event);
    ProcessingStatus processingStatus = queryProfileProcessor.process(profile, filePath, eventOffset);

    // TODO: Better handling of each of the following states
    // Successful processing of event - SUCCESS
    // When process errored - ERROR
    // After processing last file event - FINISH

    if (processingStatus.getStatus() == ProcessingStatus.Status.SUCCESS) {
      log.debug("Query {}, processed successfully", event.getQueryId());
    } else if (processingStatus.getStatus() == ProcessingStatus.Status.ERROR) {
      log.error("Failed to process query {}", event.getQueryId());
    }

    return processingStatus;
  }
}
