#!/usr/bin/env thrift -r --gen py:new_style -o ../../
/*
 * Licensed to Cloudera, Inc. under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  Cloudera, Inc. licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Structs for interacting with the job submission daemon.

namespace py jobsubd

struct SubmissionHandle {
  /**
  Unique id for this instance of job submission.
  In practice this is a primary key in the
  database.  This struct exists so that the
  handle can evolve (for example, to multiple
  submission servers).
  */
  1: i64 id
}

// States of a given job.
enum State {
  SUBMITTED = 1,
  RUNNING = 2,
  SUCCESS = 3,
  // Indicates submission error
  ERROR = 4,
  // Like SUCCESS, but non-zero returncode
  FAILURE = 5
}

// Information about a given submission
struct JobData {
  /** Job ID that the JobTracker has for this job */
  1: list<string> hadoop_job_ids,
  /** These are "tails" of the stdout/stderr from the Java process doing the 
      job submission. */
  2: string stdout_tail,
  3: string stderr_tail,
  4: State state
}

exception SubmissionError {
  1: string message,
  2: string detail
}

/**
jar files that are included in the Hadoop distribution,
and therefore need not to be copied.
*/
enum PreFabLocalizedFiles {
  STREAMING = 1
}

/** File to be copied in a LocalizeFilesStep */
struct LocalizedFile {
  /** Name of file in current directory.
      Framework has the right to make this a symlink. */
  1: string target_name,
  /** Exactly one of the following may be set */
  2: string path_on_hdfs,
  3: PreFabLocalizedFiles pre_fab_localized_file
}

/** Places files into the working directory of "jobsub plan execution". */
struct LocalizeFilesStep {
  1: list<LocalizedFile> localize_files;
}

/** 
 * Runs bin/hadoop, with enough environment to point at the
 * configured cluster, and to assume the correct user.
 */
struct BinHadoopStep {
  // Arguments to pass to "bin/hadoop"
  1: list<string> arguments
}

/** 
  A union of all possible steps.

  Note: THRIFT-409 (committed Sep 1 09) added support for unions
  to Thrift.  After a thrift release, we could switch to that syntax.
  */
struct SubmissionPlanStep {
  /** Only one of these fields may be specified! */
  1: LocalizeFilesStep localize_files_step,
  2: BinHadoopStep bin_hadoop_step,
}

/** Plan to be executed by jobsub. */
struct SubmissionPlan {
  # Name is useful for debugging
  1: string name, 
  2: string user,
  # Note that the first group herein is the user's "primary" group.
  3: list<string> groups,
  /** Steps to execute, in order. */
  4: list<SubmissionPlanStep> steps,
  /** Directory name in HDFS where stdout and stderr will be put */
  5: string save_output
}
  
service JobSubmissionService {
  SubmissionHandle submit(1: SubmissionPlan plan) throws (1:SubmissionError error),
  JobData get_job_data(1: SubmissionHandle handle) throws (1:SubmissionError error)
}
