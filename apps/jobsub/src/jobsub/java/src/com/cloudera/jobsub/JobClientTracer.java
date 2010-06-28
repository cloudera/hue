// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
package com.cloudera.jobsub;

import org.apache.hadoop.mapred.RunningJob;
import java.io.PrintStream;
import java.io.IOException;

/**
 * Records JobIDs into a file specified by $DEFAULT_JOB_LOG.
 */
public class JobClientTracer {
  private static JobClientTracer instance = new JobClientTracer();
  private PrintStream reportStream;

  public static final String DEFAULT_JOB_LOG="reported-jobs.txt";

  public synchronized static JobClientTracer getInstance() {
    return instance;
  }

  private JobClientTracer() {
    try {
      String filename = System.getenv("HUE_JOBTRACE_LOG");
      if (filename == null) {
        filename = DEFAULT_JOB_LOG;
      }
      reportStream = new PrintStream(filename);
    } catch (IOException ioe) {
      throw new RuntimeException(ioe);
    }
  }

  public void submittedJob(RunningJob job) {
    reportStream.println(job.getJobID());
    reportStream.flush();
  }
}
