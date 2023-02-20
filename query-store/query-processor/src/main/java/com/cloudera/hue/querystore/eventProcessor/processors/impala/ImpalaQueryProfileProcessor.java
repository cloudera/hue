package com.cloudera.hue.querystore.eventProcessor.processors.impala;

import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.ipe.model.impala.ImpalaRuntimeProfileTree;

public class ImpalaQueryProfileProcessor {
  @DASTransaction
  public boolean process(ImpalaRuntimeProfileTree event) {
    return true;
  }
}
