/**
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

package org.apache.hadoop.mapred;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.security.PrivilegedAction;
import java.security.PrivilegedExceptionAction;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.hadoop.conf.Configurable;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.mapreduce.Cluster;
import org.apache.hadoop.mapreduce.security.token.delegation.DelegationTokenIdentifier;
import org.apache.hadoop.io.DataOutputBuffer;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.Counters.Counter;
import org.apache.hadoop.mapred.Counters.Group;
import org.apache.hadoop.mapred.JobTracker.State;
import org.apache.hadoop.mapred.TaskStatus.Phase;
import org.apache.hadoop.mapreduce.TaskType;
import org.apache.hadoop.net.NetUtils;
import org.apache.hadoop.security.Credentials;
import org.apache.hadoop.security.UserGroupInformation;
import org.apache.hadoop.security.token.Token;
import org.apache.hadoop.thriftfs.ThriftHandlerBase;
import org.apache.hadoop.thriftfs.ThriftPluginServer;
import org.apache.hadoop.thriftfs.ThriftServerContext;
import org.apache.hadoop.thriftfs.ThriftUtils;
import org.apache.hadoop.thriftfs.api.IOException;
import org.apache.hadoop.thriftfs.api.RequestContext;
import org.apache.hadoop.thriftfs.api.ThriftDelegationToken;
import org.apache.hadoop.thriftfs.jobtracker.api.JobTrackerState;
import org.apache.hadoop.thriftfs.jobtracker.api.Jobtracker;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftClusterStatus;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftCounter;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftCounterGroup;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftGroupList;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobCounterRollups;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobID;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobInProgress;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobList;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobStatusList;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobPriority;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobProfile;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobQueueInfo;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobQueueList;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobStatus;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftJobState;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskAttemptID;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskID;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskInProgress;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskInProgressList;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskPhase;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskQueryState;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskState;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskStatus;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskTrackerStatus;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskTrackerStatusList;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftTaskType;
import org.apache.hadoop.thriftfs.jobtracker.api.ThriftUserJobCounts;
import org.apache.hadoop.thriftfs.jobtracker.api.JobNotFoundException;
import org.apache.hadoop.thriftfs.jobtracker.api.TaskNotFoundException;
import org.apache.hadoop.thriftfs.jobtracker.api.TaskAttemptNotFoundException;
import org.apache.hadoop.thriftfs.jobtracker.api.TaskTrackerNotFoundException;
import org.apache.thrift.TException;
import org.apache.thrift.TProcessor;
import org.apache.thrift.TProcessorFactory;
import org.apache.thrift.transport.TTransport;

/**
 * Exposes JobTracker APIs as a Thrift service, running by default on
 * DEFAULT_THRIFT_ADDRESS.
 */
@SuppressWarnings("deprecation")
public class ThriftJobTrackerPlugin extends JobTrackerPlugin implements Configurable {

    private static final int DEFAULT_NUM_TASKS_TO_SEND = 10;
    private static final int DEFAULT_NUM_FAILURES_TO_SEND = 5;

    /**
     * Provides lots of methods for mapping mapred objects onto their
     * Thrift equivalents, dispatched through the magic of polymorphism.
     */
    private static class JTThriftUtils {
        static ThriftJobPriority toThrift(JobPriority priority) {
            switch (priority) {
                case VERY_HIGH : return ThriftJobPriority.VERY_HIGH;
                case HIGH : return ThriftJobPriority.HIGH;
                case NORMAL : return ThriftJobPriority.NORMAL;
                case LOW : return ThriftJobPriority.LOW;
                case VERY_LOW : return ThriftJobPriority.VERY_LOW;
            }
            LOG.info("Unexpected priority in toThrift(JobPriority) - defaulting to NORMAL" );
            return ThriftJobPriority.NORMAL;
        }

        public static ThriftJobID toThrift(JobID jobId) {
            ThriftJobID ret = new ThriftJobID();
            ret.setJobID(jobId.getId());
            ret.setJobTrackerID(jobId.getJtIdentifier());
            ret.setAsString(jobId.toString());
            return ret;
        }

        public static JobID fromThrift(ThriftJobID jobId) {
            return new JobID(jobId.getJobTrackerID(),
                             jobId.getJobID());
        }

        public static TaskID fromThrift(ThriftTaskID taskId) {
            return new TaskID(fromThrift(taskId.getJobID()),
                              taskId.getTaskType() == ThriftTaskType.MAP,
                              taskId.getTaskID());
        }

        public static TaskAttemptID fromThrift(ThriftTaskAttemptID taskId) {
            JobID jid = fromThrift(taskId.getTaskID().jobID);
            String ident = jid.getJtIdentifier();
            boolean isMap = taskId.taskID.getTaskType() == ThriftTaskType.MAP;
            TaskAttemptID id = new TaskAttemptID(ident,jid.getId(),isMap,
                                                 taskId.getTaskID().getTaskID(),
                                                 taskId.getAttemptID());
            return id;
        }

        public static ThriftJobState jobRunStateToThrift(int state) {
            switch (state) {
                case JobStatus.RUNNING:
                    return ThriftJobState.RUNNING;
                case JobStatus.SUCCEEDED:
                    return ThriftJobState.SUCCEEDED;
                case JobStatus.FAILED:
                    return ThriftJobState.FAILED;
                case JobStatus.PREP:
                    return ThriftJobState.PREP;
                case JobStatus.KILLED:
                    return ThriftJobState.KILLED;
                default:
                    return null; // signify unknown
            }
        }

        public static ThriftJobStatus toThrift(JobStatus job) {
            ThriftJobStatus ret = new ThriftJobStatus();
            ret.setCleanupProgress(job.cleanupProgress());
            ret.setMapProgress(job.mapProgress());
            ret.setReduceProgress(job.reduceProgress());
            ret.setPriority(toThrift(job.getJobPriority()));
            ret.setRunState(jobRunStateToThrift(job.getRunState()));
            ret.setSchedulingInfo(job.getSchedulingInfo());
            ret.setSetupProgress(job.setupProgress());
            ret.setStartTime(job.getStartTime());
            ret.setUser(job.getUsername());
            ret.setJobID(toThrift(job.getJobID()));
            return ret;
        }

        /**
         * Convert a section of an array of TaskInProgress to a ThriftTaskInProgressList.
         * The returned list contains tasks in the range of [fromIdx, toIdx).
         * Callers should make sure that the indices are valid, and that toIdx
         * is not smaller than fromIdx.
         * @param tasks         An array of TaskInProgress objects.
         * @param tracker       The JobTracker.
         * @param fromIdx       The inclusive starting range to convert.
         * @param toIdx         The exclusive ending range to convert, i.e. [fromIdx, toIdx)
         */
        public static ThriftTaskInProgressList toThrift(TaskInProgress[] tasks,
                                                        JobTracker tracker,
                                                        int fromIdx,
                                                        int toIdx) {
            ThriftTaskInProgressList ret = new ThriftTaskInProgressList();

            if (toIdx > tasks.length)
                toIdx = tasks.length;
            if (fromIdx > toIdx) {
                assert false;           // Internal callers should not pass in bogus args
                fromIdx = toIdx;
            }

            ArrayList<ThriftTaskInProgress> taskArr = new
                ArrayList<ThriftTaskInProgress>(toIdx - fromIdx);
            for (int i = fromIdx; i < toIdx; ++i)
                taskArr.add(toThrift(tasks[i], tracker));

            ret.setTasks(taskArr);
            ret.setNumTotalTasks(tasks.length);
            return ret;
        }


        /**
         * Converts a JobInProgress object to its corresponding Thrift representation.
         * @param job Input JobInProgress object
         * @param includeTasks Include task information iff true
         */
        public static ThriftJobInProgress toThrift(JobInProgress job, boolean includeTasks, JobTracker tracker) {
            ThriftJobInProgress ret = new ThriftJobInProgress();

            // Take the lock so we can do an atomic copy
            synchronized(job) {
                ret.setDesiredMaps(job.desiredMaps());
                ret.setDesiredReduces(job.desiredReduces());
                ret.setFinishedMaps(job.finishedMaps());
                ret.setFinishedReduces(job.finishedReduces());

                ret.setJobID(toThrift(job.getJobID()));
                ret.setPriority(toThrift(job.getPriority()));
                ret.setProfile(toThrift(job.getProfile()));

                // Status lock is taken here
                ret.setStatus(toThrift(job.getStatus()));

                ret.setStartTime(job.getStartTime());
                ret.setFinishTime(job.getFinishTime());
                ret.setLaunchTime(job.getLaunchTime());
            }

            // No need to hang on to job lock now
            // TODO(henry/bc): By releasing the lock above, getInitialViewTaskList
            // may see a different view of the job and its task list. This
            // could cause inconsistency between the values copied above and
            // the tasks themselves, but no deadlocks/CMEs.
            if (includeTasks) {
                ret.setTasks(getInitialViewTaskList(job, tracker));
            }
            return ret;
        }

        /**
         * Gets as much information about a retired Job and converts it to its corresponding
         * Thrift representation.
         * @param jobProfile The profile of a job.
         * @param jobStatus The status of a job.
         */
        public static ThriftJobInProgress toThrift(JobProfile jobProfile, JobStatus jobStatus) {
            ThriftJobInProgress ret = new ThriftJobInProgress();

            ret.setJobID(toThrift(jobProfile.getJobID()));
            ret.setPriority(toThrift(jobStatus.getJobPriority()));
            ret.setProfile(toThrift(jobProfile));

            ret.setStatus(toThrift(jobStatus));

            ret.setStartTime(jobStatus.getStartTime());

            return ret;
        }

        /**
         * There are always two setup tasks and two cleanup tasks by default
         * If one succeeds, the other is killed. We choose not to report those
         * to the UI because they are spurious.
         * This method _always_ return a new array.
         */
        public static TaskInProgress[] sanitizeCleanupSetupTask(
                                            TaskInProgress[] tasks) {
            assert tasks.length <= 2;   // There should be at most 2 of them

            if (tasks.length != 2)
                return tasks.clone();

            TaskInProgress goodTip =
                (tasks[1].isRunning() || tasks[1].isComplete()) ?
                tasks[1] : tasks[0];
            return new TaskInProgress[] { goodTip };
        }

        public static ThriftJobInProgress toThrift(JobInProgress job, JobTracker tracker) {
            return toThrift(job, true, tracker);
        }

        public static ThriftJobProfile toThrift(JobProfile profile) {
            // Takes no locks
            ThriftJobProfile ret = new ThriftJobProfile();
            ret.setJobFile(profile.getJobFile());
            ret.setJobID(toThrift(profile.getJobID()));
            ret.setName(profile.getJobName());
            ret.setQueueName(profile.getQueueName());
            ret.setUser(profile.getUser());
            return ret;
        }

        public static List<ThriftCounterGroup> toThrift(Counters jcs) {
          Collection<String> groupNames = null;
          List<ThriftCounterGroup> ret = null;
          synchronized(jcs) {
            groupNames =
              new ArrayList<String>(jcs.getGroupNames());
            ret =
                new ArrayList<ThriftCounterGroup>(groupNames.size());
            for (String s : groupNames){
                Counters.Group g = jcs.getGroup(s);
                ThriftCounterGroup tcg = toThrift(g);
                ret.add(tcg);
            }
          }
          return ret;
        }

        public static ThriftCounterGroup toThrift(Group g) {
            ThriftCounterGroup ret = new ThriftCounterGroup();
            ret.setName(g.getName());
            ret.setDisplayName(g.getDisplayName());
            ret.counters = new HashMap<String, ThriftCounter>();
            for (Counters.Counter c : g) {
                ret.counters.put(c.getDisplayName(), toThrift(c));
            }
            return ret;
        }

        public static ThriftCounter toThrift(Counter c) {
            ThriftCounter ret = new ThriftCounter();
            ret.setDisplayName(c.getDisplayName());
            ret.setName(c.getName());
            ret.setValue(c.getValue());
            return ret;
        }

        public static ThriftClusterStatus toThrift(ClusterStatus cs,
                JobTracker tracker) {
            ThriftClusterStatus tcs = new ThriftClusterStatus();
            tcs.setNumActiveTrackers(cs.getTaskTrackers());
            tcs.setActiveTrackerNames(new ArrayList<String>(cs.getActiveTrackerNames()));
            tcs.setBlacklistedTrackerNames(new ArrayList<String>(cs.getBlacklistedTrackerNames()));
            tcs.setNumBlacklistedTrackers(cs.getBlacklistedTrackers());
            tcs.setNumExcludedNodes(0);
            tcs.setTaskTrackerExpiryInterval(cs.getTTExpiryInterval());
            tcs.setMapTasks(cs.getMapTasks());
            tcs.setReduceTasks(cs.getReduceTasks());
            tcs.setMaxMapTasks(cs.getMaxMapTasks());
            tcs.setMaxReduceTasks(cs.getMaxReduceTasks());
            tcs.setState(cs.getJobTrackerStatus() == Cluster.JobTrackerStatus.INITIALIZING ? JobTrackerState.INITIALIZING :
                JobTrackerState.RUNNING);
            tcs.setUsedMemory(cs.getUsedMemory());
            tcs.setMaxMemory(cs.getMaxMemory());
            tcs.setTotalSubmissions(tracker.getTotalSubmissions());

            tcs.setHasRecovered(tracker.hasRecovered());
            tcs.setHasRestarted(tracker.hasRestarted());

            tcs.setHostname(tracker.getJobTrackerMachine());
            tcs.setIdentifier(tracker.getTrackerIdentifier());

            tcs.setStartTime(tracker.getStartTime());

            tcs.setHttpPort(tracker.getInfoPort());

            return tcs;
        }

        public static ThriftTaskTrackerStatus toThrift(TaskTrackerStatus t) {
            ThriftTaskTrackerStatus ttts = new ThriftTaskTrackerStatus();
            ttts.setTrackerName(t.getTrackerName());
            ttts.setAvailableSpace(t.getResourceStatus().getAvailableSpace());
            ttts.setFailureCount(t.getFailures());
            ttts.setHost(t.getHost());
            ttts.setHttpPort(t.getHttpPort());
            ttts.setLastSeen(t.getLastSeen());
            ttts.setMapCount(t.countMapTasks());
            ttts.setReduceCount(t.countReduceTasks());
            ttts.setMaxMapTasks(t.getMaxMapSlots());
            ttts.setMaxReduceTasks(t.getMaxReduceSlots());

            ttts.setTotalPhysicalMemory(t.getResourceStatus().getTotalPhysicalMemory());
            ttts.setTotalVirtualMemory(t.getResourceStatus().getTotalVirtualMemory());
            Collection<TaskStatus> tasks = null;
            synchronized(t) {
              tasks = new ArrayList<TaskStatus>(t.getTaskReports());
            }
            for (TaskStatus tr : tasks) {
              ttts.addToTaskReports(toThrift(tr));
            }
            return ttts;
        }

        public static ThriftTaskStatus toThrift(TaskStatus ts) {
            ThriftTaskStatus tts = new ThriftTaskStatus();
            tts.setCounters(new ThriftGroupList(toThrift(ts.getCounters())));
            tts.setDiagnosticInfo(ts.getDiagnosticInfo());
            tts.setFinishTime(ts.getFinishTime());
            tts.setOutputSize(ts.getOutputSize());
            tts.setPhase(toThrift(ts.getPhase()));
            tts.setProgress(ts.getProgress());
            tts.setStartTime(ts.getStartTime());
            tts.setStateString(ts.getStateString());
            tts.setTaskID(toThrift(ts.getTaskID()));
            tts.setTaskTracker(ts.getTaskTracker());
            tts.setState(toThrift(ts.getRunState()));

            if (ts.getIsMap()) {
                // not available in 0.20: tts.setMapFinishTime(ts.getMapFinishTime());
                tts.setShuffleFinishTime(0);
                tts.setSortFinishTime(0);
            } else {
                tts.setMapFinishTime(0);
                tts.setShuffleFinishTime(ts.getShuffleFinishTime());
                tts.setSortFinishTime(ts.getSortFinishTime());
            }
            return tts;
        }

        public static ThriftTaskState toThrift(
                org.apache.hadoop.mapred.TaskStatus.State runState) {
            switch (runState) {
            case COMMIT_PENDING : return ThriftTaskState.COMMIT_PENDING;
            case RUNNING : return ThriftTaskState.RUNNING;
            case SUCCEEDED : return ThriftTaskState.SUCCEEDED;
            case FAILED : return ThriftTaskState.FAILED;
            case KILLED : return ThriftTaskState.KILLED;
            case FAILED_UNCLEAN : return ThriftTaskState.FAILED_UNCLEAN;
            case KILLED_UNCLEAN : return ThriftTaskState.KILLED_UNCLEAN;
            }
            LOG.info("Unexpected runState in toThrift(TaskStatus.State) - defaulting to FAILED_UNCLEAN" );
            return ThriftTaskState.FAILED_UNCLEAN;
        }

        private static ThriftTaskAttemptID toThrift(TaskAttemptID taskID) {
            ThriftTaskAttemptID ret =  new ThriftTaskAttemptID();
            ret.setTaskID(toThrift(taskID.getTaskID()));
            ret.setAttemptID(taskID.getId());
            ret.setAsString(taskID.toString());
            return ret;
        }

        private static ThriftTaskID toThrift(TaskID taskID) {
            ThriftTaskID ret =  new ThriftTaskID();
            ret.setJobID(toThrift(taskID.getJobID()));
            ret.setTaskID(taskID.getId());
            ret.setTaskType(getThriftTaskType(taskID));
            ret.setAsString(taskID.toString());
            return ret;
        }

        private static ThriftTaskType getThriftTaskType(TaskID task) {
          if (task.isMap()) {
            return ThriftTaskType.MAP;
          } else {
            return ThriftTaskType.REDUCE;
          }
        }

        private static ThriftTaskPhase toThrift(Phase phase) {
            switch (phase) {
            case CLEANUP : return ThriftTaskPhase.CLEANUP;
            case STARTING : return ThriftTaskPhase.STARTING;
            case MAP : return ThriftTaskPhase.MAP;
            case REDUCE : return ThriftTaskPhase.REDUCE;
            case SHUFFLE : return ThriftTaskPhase.SHUFFLE;
            case SORT : return ThriftTaskPhase.SORT;
            }
            LOG.info("Unexpected phase in toThrift(Phase) - defaulting to CLEANUP" );
            return ThriftTaskPhase.CLEANUP;
        }

        public static ThriftJobQueueInfo toThrift(JobQueueInfo q) {
            ThriftJobQueueInfo tq = new ThriftJobQueueInfo();
            tq.queueName = q.getQueueName();
            tq.schedulingInfo = q.getSchedulingInfo();
            return tq;
        }

        public static ThriftTaskType getTaskInProgressType(TaskInProgress tip) {
            // Note that the order of the tests are important, since the
            // conditions are not mutually exclusive.
            if (tip.isJobSetupTask())
                return ThriftTaskType.JOB_SETUP;
            if (tip.isJobCleanupTask())
                return ThriftTaskType.JOB_CLEANUP;
            if (tip.isMapTask())
                return ThriftTaskType.MAP;
            else
                return ThriftTaskType.REDUCE;
        }


        /**
         * Returns a TaskList to be presented with the initial view of the JobInProgress.
         * This is unfortunately very much tied to how the JobBrowser UI is presented:
         * - At most 5 most recent tasks, and
         * - At most 5 failed tasks (killed don't count).
         */
        private static ThriftTaskInProgressList getInitialViewTaskList(
                                                        JobInProgress job,
                                                        JobTracker jobTracker) {
            List<TaskInProgress> allTips = new ArrayList<TaskInProgress>();
            synchronized(job) {
                allTips.addAll(Arrays.asList(job.getTasks(TaskType.MAP)));
                allTips.addAll(Arrays.asList(job.getTasks(TaskType.REDUCE)));
                allTips.addAll(Arrays.asList(
                      JTThriftUtils.sanitizeCleanupSetupTask(job.getTasks(TaskType.JOB_CLEANUP))));
                allTips.addAll(Arrays.asList(
                      JTThriftUtils.sanitizeCleanupSetupTask(job.getTasks(TaskType.JOB_SETUP))));
            }

            // Sort by reverse time, but put all the genuine failures in front, and the
            // killed tasks at the end. After the sorting, the goal is to have this array:
            //   [ real failures ... others ... failed/killed ]  (all in reverse order)
            // Then we find the boundary between the real failures and the completed, and
            // return a chunk from that boundary, containing the earlier failures and the
            // recent tasks, which is exactly what the UI wants.
            Collections.sort(allTips, new Comparator<TaskInProgress>() {
                public int compare(TaskInProgress foo, TaskInProgress bar) {
                    if (isFailOnError(foo) && !isFailOnError(bar))
                        return -1;
                    if (!isFailOnError(foo) && isFailOnError(bar))
                        return 1;
                    if (foo.isFailed() && !bar.isFailed())
                        return 1;
                    if (!foo.isFailed() && bar.isFailed())
                        return -1;
                    long diff = foo.getExecStartTime() - bar.getExecStartTime();
                    if (diff == 0)
                        return 0;
                    return (diff > 0) ? -1 : 1;
                }});

            int offset = 0;
            int count = DEFAULT_NUM_TASKS_TO_SEND;

            // We only want DEFAULT_NUM_FAILURES_TO_SEND number of failures included.
            int nFailures = 0;
            for (TaskInProgress tip : allTips) {
                if (!isFailOnError(tip))
                    break;
                ++nFailures;
            }
            if (nFailures > DEFAULT_NUM_FAILURES_TO_SEND)
                offset = nFailures - DEFAULT_NUM_FAILURES_TO_SEND;

            return JTThriftUtils.toThrift(allTips.toArray(new TaskInProgress[allTips.size()]),
                                          jobTracker, offset, offset + count);
        }


        public static ThriftTaskInProgress toThrift(TaskInProgress t,
                                                    JobTracker tracker) {
            ThriftTaskInProgress ret = new ThriftTaskInProgress();
            TaskStatus[] sts = null;
            ThriftTaskType type = getTaskInProgressType(t);

            synchronized(t) {
                ret.setComplete(t.isComplete());
                ret.setExecFinishTime(t.getExecFinishTime());
                ret.setExecStartTime(t.getExecStartTime());
                ret.setFailed(t.isFailed());
                ret.setProgress(t.getProgress());
                ret.setStartTime(t.getStartTime());
                ret.setTaskID(toThrift(t.getTIPId()));
                // TODO(henry): This can go away when we go on to > 0.20
                ret.taskID.setTaskType(type);

                // getTaskStatuses copies a collection but is not synchronised :(
                sts = t.getTaskStatuses();
            }

            ret.setCounters(new ThriftGroupList(toThrift(t.getCounters())));

            Map<String,ThriftTaskStatus> statusMap = new HashMap<String,ThriftTaskStatus>();
            Map<String,List<String>> dataMap = new HashMap<String,List<String>>();
            for (TaskStatus ts : sts) {
              ThriftTaskAttemptID id = toThrift(ts.getTaskID());
              id.taskID.setTaskType(type);
              statusMap.put(id.getAsString(), toThrift(ts));
              try {
                  // Atomic copy
                  String[] strDiags = tracker.getTaskDiagnostics(ts.getTaskID());
                  // Thrift does not like null values in maps
                  List<String> diag = (strDiags == null ? new ArrayList<String>() :
                                                          Arrays.asList(strDiags));
                  dataMap.put(id.getAsString(), diag);
              } catch (java.io.IOException e) {
                  // tracker.getTaskDiagnostics is supposed to throw,
                  // but I can't see where it does (and removing the throws clause
                  // doesn't cause a compile failure...), so this is probably
                  // extraneous
                  LOG.warn(e);
                  throw new RuntimeException(e.getMessage());
              }
            }
            ret.setTaskStatuses(statusMap);

            // Takes lock on t
            TaskReport report = t.generateSingleReport();
            ret.setMostRecentState(report.getState());
            ret.setSuccessfulAttempt(toThrift(report.getSuccessfulTaskAttempt()).asString);
            // Because report has a reference to an array from t, we need to synchronize on
            // t to copy it :(
            Collection<TaskAttemptID> attempts = null;
            synchronized(t) {
                attempts =
                    new ArrayList<TaskAttemptID>(report.getRunningTaskAttempts());
            }
            List<String> runningAttempts = new ArrayList<String>(attempts.size());
            for (TaskAttemptID tid : attempts) {
                runningAttempts.add(toThrift(tid).asString);
            }
            ret.setRunningAttempts(runningAttempts);
            ret.setTaskDiagnosticData(dataMap);

            return ret;
        }

        public static ThriftTaskQueryState inferTaskState(TaskInProgress tip) {
            // The ordering of the checks is important
            if (tip.isComplete())
                return ThriftTaskQueryState.SUCCEEDED;
            else if (isFailOnError(tip))
                return ThriftTaskQueryState.FAILED;
            else if (tip.isFailed())
                return ThriftTaskQueryState.KILLED;
            else if (tip.getExecStartTime() == 0)
                return ThriftTaskQueryState.PENDING;
            else
                return ThriftTaskQueryState.RUNNING;
        }

        /**
         * Guess whether the TaskInProgress failed due to genuine error,
         * rather than simply aborted. It checks whether the execution has started
         * for this task. This is not always correct. A running task can still be
         * aborted.
         */
        private static boolean isFailOnError(TaskInProgress tip) {
            return tip.isFailed() && tip.getExecStartTime() != 0;
        }

    }

    public static final Log LOG = LogFactory.getLog(JobTrackerPlugin.class.getName());

    /** Name of the configuration property of the Thrift server address */
    public static final String THRIFT_ADDRESS_PROPERTY = "jobtracker.thrift.address";

    /**
     * Default address and port this server will bind to, in case nothing is found
     * in the configuration object.
     */
    public static final String DEFAULT_THRIFT_ADDRESS = "0.0.0.0:9290";

    private JobTracker jobTracker = null;

    private Configuration conf;

    private ThriftPluginServer thriftServer;

    @Override
    public void start(Object service) {
        LOG.info("Starting ThriftJobTrackerPlugin");
        this.jobTracker = (JobTracker)service;
        try {
          InetSocketAddress address = NetUtils.createSocketAddr(
            conf.get(THRIFT_ADDRESS_PROPERTY, DEFAULT_THRIFT_ADDRESS));
          this.thriftServer = new ThriftPluginServer(address, new ProcessorFactory(), conf);
          thriftServer.setConf(conf);
          thriftServer.start();
          // The port may have been 0, so we update it.
          conf.set(THRIFT_ADDRESS_PROPERTY, address.getHostName() + ":" +
              thriftServer.getPort());
        } catch (Exception e) {
            LOG.warn("Cannot start Thrift jobtracker plug-in", e);
            throw new RuntimeException("Cannot start Thrift jobtracker plug-in", e);
        }
    }

    @Override
    public void stop() {
        LOG.info("Stopping ThriftJobTrackerPlugin");
        if (thriftServer != null) {
            thriftServer.stop();
          }
    }

    public void close() {
        LOG.info("Closing ThriftJobTrackerPlugin");
        if (thriftServer != null) {
            thriftServer.close();
          }
    }

    /** Java server-side implementation of the 'Jobtracker' Thrift interface. */
    class ThriftHandler extends ThriftHandlerBase implements Jobtracker.Iface {

        public ThriftHandler(ThriftServerContext serverContext) {
            super(serverContext);
        }

        /** Returns the JobTracker's name */
        public String getJobTrackerName(RequestContext ctx) {
          return assumeUserContextAndExecute(ctx, new PrivilegedAction<String>() {
            public String run() {
              return jobTracker.getJobTrackerMachine();
            }
          });
        }

        /** Returns a large clusterstatus object, augmented with some extra
         * detail from the JobTracker
         */
        public ThriftClusterStatus getClusterStatus(RequestContext ctx) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftClusterStatus>() {
              public ThriftClusterStatus run() {
                ClusterStatus cs = jobTracker.getClusterStatus(true);
                return JTThriftUtils.toThrift(cs,jobTracker);
              }
            });
        }

        /** Returns a list of all run-queues available to the JobTracker */
        public ThriftJobQueueList getQueues(RequestContext ctx) throws IOException, TException {
            return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<ThriftJobQueueList>() {
              public ThriftJobQueueList run() throws java.io.IOException {
                JobQueueInfo queues[] = null;
                queues = jobTracker.getQueues();

                ArrayList<ThriftJobQueueInfo> ret =
                    new ArrayList<ThriftJobQueueInfo>(queues.length);

                for (JobQueueInfo q : queues) {
                    ThriftJobQueueInfo tq = JTThriftUtils.toThrift(q);
                    ret.add(tq);
                }
                return new ThriftJobQueueList(ret);
              }
            });
        }

        /** Returns job by id (including task info) */
        public ThriftJobInProgress getJob(RequestContext ctx, ThriftJobID jobID) throws JobNotFoundException {
            final JobID jid = JTThriftUtils.fromThrift(jobID);
            final JobInProgress job = assumeUserContextAndExecute(ctx, new PrivilegedAction<JobInProgress>() {
              public JobInProgress run() {
                return jobTracker.getJob(jid);
              }
            });
            if (job == null) {
              throw new JobNotFoundException();
            }

            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftJobInProgress>() {
              public ThriftJobInProgress run() {
                return JTThriftUtils.toThrift(job, jobTracker);
              }
            });
        }

        /** Returns all running jobs (does not include task info) */
        public ThriftJobList getRunningJobs(RequestContext ctx) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftJobList>() {
              public ThriftJobList run() {
                // Atomic copy
                List<JobInProgress> jobs = jobTracker.getRunningJobs();
                ArrayList<ThriftJobInProgress> ret =
                    new ArrayList<ThriftJobInProgress>(jobs.size());

                for (JobInProgress job : jobs) {
                    ret.add(JTThriftUtils.toThrift(job, false, jobTracker));
                }
                return new ThriftJobList(ret);
              }
            });
        }

        /** Returns all completed jobs (does not include task info) */
        public ThriftJobList getCompletedJobs(RequestContext ctx) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftJobList>() {
              public ThriftJobList run() {
                List<JobInProgress> jobs = null;
                synchronized(jobTracker){
                    jobs = jobTracker.completedJobs();
                }
                ArrayList<ThriftJobInProgress> ret =
                    new ArrayList<ThriftJobInProgress>(jobs.size());

                for (JobInProgress job : jobs) {
                    ret.add(JTThriftUtils.toThrift(job, false, jobTracker));
                }
                return new ThriftJobList(ret);
              }
            });
        }

        /** Returns a retired job (does not include task info, miss some fields) */
        public ThriftJobInProgress getRetiredJob(final RequestContext ctx, final ThriftJobID jobID) throws JobNotFoundException {
            final JobID jid = JTThriftUtils.fromThrift(jobID);

            final JobStatus jobStatus = assumeUserContextAndExecute(ctx, new PrivilegedAction<JobStatus>() {
              public JobStatus run() {
                return jobTracker.getJobStatus(jid);
              }
            });

            if (jobStatus == null) {
              throw new JobNotFoundException();
            }

            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftJobInProgress>() {
              public ThriftJobInProgress run() {
                return JTThriftUtils.toThrift(jobTracker.getJobProfile(jid), jobStatus);
              }
            });
        }

        /** Returns all retired jobs (does not include task info, miss some fields) */
        public ThriftJobList getRetiredJobs(RequestContext ctx, final ThriftJobState state) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftJobList>() {
              public ThriftJobList run() {
                JobStatus[] jobStatuses = null;
                Set<JobID> jobsInProgressId = new HashSet<JobID>();

                synchronized(jobTracker) {
                    jobStatuses = jobTracker.getAllJobs();
                    for (JobInProgress job : jobTracker.getRunningJobs()) {
                        jobsInProgressId.add(job.getJobID());
                    }
                    for (JobInProgress job : jobTracker.failedJobs()) {
                        jobsInProgressId.add(job.getJobID());
                    }
                    for (JobInProgress job : jobTracker.completedJobs()) {
                        jobsInProgressId.add(job.getJobID());
                    }
                    for (JobStatus job : jobTracker.jobsToComplete()) {
                      jobsInProgressId.add(job.getJobID());
                    }
                }

                ArrayList<ThriftJobInProgress> ret = new ArrayList<ThriftJobInProgress>();

                for (JobStatus jobStatus : jobStatuses) {
                    JobID jobID = jobStatus.getJobID();
                    if (!jobsInProgressId.contains(jobID) &&
                        (state == null || state == JTThriftUtils.jobRunStateToThrift(jobStatus.getRunState()))) {
                        // No need to lock
                        ret.add(JTThriftUtils.toThrift(jobTracker.getJobProfile(jobID), jobStatus));
                    }
                }
                return new ThriftJobList(ret);
              }
            });
        }

        /** Returns all failed jobs (does not include task info) */
        public ThriftJobList getFailedJobs(RequestContext ctx) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftJobList>() {
              public ThriftJobList run() {
                List<JobInProgress> jobs = null;
                synchronized(jobTracker){
                    jobs = jobTracker.failedJobs();
                }
                List<ThriftJobInProgress> ret =
                    new ArrayList<ThriftJobInProgress>(jobs.size());
                for (JobInProgress job : jobs) {
                    if (job.getStatus().getRunState() == JobStatus.FAILED) {
                        ret.add(JTThriftUtils.toThrift(job, false, jobTracker));
                    }
                }
                return new ThriftJobList(ret);
              }
            });
        }

        /** Returns all killed jobs (does not include task info) */
        public ThriftJobList getKilledJobs(RequestContext ctx) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftJobList>() {
              public ThriftJobList run() {
                List<JobInProgress> jobs = null;
                synchronized(jobTracker){
                    jobs = jobTracker.failedJobs();
                }
                List<ThriftJobInProgress> ret =
                    new ArrayList<ThriftJobInProgress>(jobs.size());
                for (JobInProgress job : jobs) {
                    if (job.getStatus().getRunState() == JobStatus.KILLED) {
                        ret.add(JTThriftUtils.toThrift(job, false, jobTracker));
                    }
                }
                return new ThriftJobList(ret);
              }
            });
        }

        /** Returns all running / failed / completed jobs (does not include task info) */
        public ThriftJobList getAllJobs(RequestContext ctx) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftJobList>() {
              public ThriftJobList run() {
                List<JobInProgress> jobList = new ArrayList<JobInProgress>();
                jobList.addAll(jobTracker.getRunningJobs());
                synchronized(jobTracker){
                    jobList.addAll(jobTracker.failedJobs());
                    jobList.addAll(jobTracker.completedJobs());
                }
                List<ThriftJobInProgress> ret =
                    new ArrayList<ThriftJobInProgress>();
                for (JobInProgress job : jobList) {
                        ret.add(JTThriftUtils.toThrift(job, false, jobTracker));
                    }
                return new ThriftJobList(ret);
              }
            });
        }

        /**
         * Return the count of jobs, broken down by status, for a given user.
         */
        public ThriftUserJobCounts getUserJobCounts(RequestContext ctx, final String user) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftUserJobCounts>() {
              public ThriftUserJobCounts run() {
                ThriftUserJobCounts ret = new ThriftUserJobCounts(0, 0, 0, 0, 0);

                JobStatus[] allJobs = jobTracker.getAllJobs();
                for (JobStatus js : allJobs) {
                    if (!js.getUsername().equals(user))
                        continue;
                    switch (js.getRunState()) {
                        case JobStatus.PREP:
                            ++ret.nPrep;
                            break;
                        case JobStatus.RUNNING:
                            ++ret.nRunning;
                            break;
                        case JobStatus.SUCCEEDED:
                            ++ret.nSucceeded;
                            break;
                        case JobStatus.FAILED:
                            ++ret.nFailed;
                            break;
                        case JobStatus.KILLED:
                            ++ret.nKilled;
                            break;
                        default:
                            LOG.error("Unknown JobStatus " + js.getRunState() +
                                      " for job id " + js.getJobID().getId());
                    }
                }
                return ret;
              }
            });
        }

        /**
         * Return a (possibly incomplete) list of tasks.
         */
        public ThriftTaskInProgressList getTaskList(
                                  RequestContext ctx,
                                  ThriftJobID thriftJobID,
                                  Set<ThriftTaskType> types,
                                  Set<ThriftTaskQueryState> states,
                                  String text,
                                  int count,
                                  int offset) throws JobNotFoundException {
            final JobID jid = JTThriftUtils.fromThrift(thriftJobID);
            JobInProgress job = assumeUserContextAndExecute(ctx, new PrivilegedAction<JobInProgress>() {
              public JobInProgress run() {
                return jobTracker.getJob(jid);
              }
            });

            if (job == null)
              throw new JobNotFoundException();

            // Gather all the tasks of the matching type
            List<TaskInProgress> allTips = new ArrayList<TaskInProgress>();
            synchronized(job) {
                if (types.contains(ThriftTaskType.MAP))
                    allTips.addAll(Arrays.asList(job.getTasks(TaskType.MAP)));
                if (types.contains(ThriftTaskType.REDUCE))
                    allTips.addAll(Arrays.asList(job.getTasks(TaskType.REDUCE)));
                if (types.contains(ThriftTaskType.JOB_CLEANUP))
                    allTips.addAll(Arrays.asList(
                          JTThriftUtils.sanitizeCleanupSetupTask(job.getTasks(TaskType.JOB_CLEANUP))));
                if (types.contains(ThriftTaskType.JOB_SETUP))
                    allTips.addAll(Arrays.asList(
                          JTThriftUtils.sanitizeCleanupSetupTask(job.getTasks(TaskType.JOB_SETUP))));
            }

            // Are the arguments out of bound?
            if (count < 0 || offset < 0 || offset >= allTips.size()) {
                LOG.error("Bad arguments to getTaskList(): count " + count +
                          "; offset " + offset +
                          "; while total tasks count is " + allTips.size());
                return JTThriftUtils.toThrift(new TaskInProgress[0], jobTracker, 0, 0);
            }

            List<TaskInProgress> matches = null;
            if (text == null)
                text = "";
            else
                text = text.trim();

            boolean doFilterStates = (states.size() !=
                                      ThriftTaskQueryState.class.getEnumConstants().length);
            boolean doFilterText = !text.isEmpty();

            if (doFilterStates || doFilterText) {
                text = text.toUpperCase();
                matches = new ArrayList<TaskInProgress>();

                // Note that it's important to finish all matching, regardless
                // of the requested count, because we need to report the total
                // number of matches.
                for (TaskInProgress tip : allTips) {
                    ThriftTaskQueryState qstate = null;

                    if (doFilterStates) {
                        // Do filter by states
                        qstate = JTThriftUtils.inferTaskState(tip);
                        if (!states.contains(qstate))
                            continue;
                    }

                    if (doFilterText) {
                        // Match against (1) state, (2) most recent state, (3) ID
                        if (qstate == null)
                            qstate = JTThriftUtils.inferTaskState(tip);
                        String qstateStr = qstate.toString();
                        if (!qstateStr.contains(text) &&
                                !tip.getTIPId().toString().toUpperCase().contains(text) &&
                                !tip.generateSingleReport().getState().toUpperCase().contains(text))
                            continue;
                    }

                    matches.add(tip);
                }
            } else {
              // If not filtering, we just do offset/limit into the full list
              matches = allTips;
            }

            return JTThriftUtils.toThrift(matches.toArray(new TaskInProgress[matches.size()]),
                                          jobTracker, offset, offset + count);
        }


        /** Returns the task identified by the id */
        public ThriftTaskInProgress getTask(RequestContext ctx, ThriftTaskID ttaskId)
                throws JobNotFoundException, TaskNotFoundException {
            final TaskID taskId = JTThriftUtils.fromThrift(ttaskId);
            final JobID jobId = JTThriftUtils.fromThrift(ttaskId.getJobID());
            final JobInProgress job = assumeUserContextAndExecute(ctx, new PrivilegedAction<JobInProgress>() {
              public JobInProgress run() {
                return jobTracker.getJob(jobId);
              }
            });
            if (job == null)
                throw new JobNotFoundException();
            TaskInProgress tip = assumeUserContextAndExecute(ctx, new PrivilegedAction<TaskInProgress>() {
              public TaskInProgress run() {
                return job.getTaskInProgress(taskId);
              }
            });
            if (tip == null)
                throw new TaskNotFoundException();
            return JTThriftUtils.toThrift(tip, jobTracker);
        }


        /** Returns the set of counters associated with a given job */
        public ThriftGroupList getJobCounters(RequestContext ctx, final ThriftJobID jobID)
            throws JobNotFoundException
        {
            Counters jcs;
            try {
              jcs = assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Counters>() {
                public Counters run() throws java.io.IOException {
                    JobInProgress job = jobTracker.getJob(JTThriftUtils.fromThrift(jobID));
                    if (job != null) {
                        if (jobTracker.areACLsEnabled()) {
                            UserGroupInformation ugi = UserGroupInformation.getCurrentUser();
                            // check the job-access
                            jobTracker.getACLsManager().checkAccess(job, ugi,
                                    Operation.VIEW_JOB_COUNTERS);
                        }
                        return job.inited() ? job.getCounters() : new Counters();
                    } else {
                        return jobTracker.getJobCounters(JTThriftUtils.fromThrift(jobID));
                    }
                }
              });
            } catch (IOException e) {
              throw new JobNotFoundException();
            }
            if (jcs == null) {
                throw new JobNotFoundException();
            }
            return new ThriftGroupList(JTThriftUtils.toThrift(jcs));
        }

        public ThriftJobCounterRollups getJobCounterRollups(RequestContext ctx, final ThriftJobID jobID)
            throws JobNotFoundException
        {
            JobInProgress jip = assumeUserContextAndExecute(ctx, new PrivilegedAction<JobInProgress>() {
              public JobInProgress run() {
                return jobTracker.getJob(JTThriftUtils.fromThrift(jobID));
              }
            });
            if (jip == null) {
                throw new JobNotFoundException();
            }

            ThriftJobCounterRollups ret = new ThriftJobCounterRollups();
            Counters mapCounters = jip.getMapCounters();
            Counters reduceCounters = jip.getReduceCounters();
            ret.mapCounters = new ThriftGroupList(
                JTThriftUtils.toThrift(mapCounters));
            ret.reduceCounters = new ThriftGroupList(
                JTThriftUtils.toThrift(reduceCounters));
            ret.jobCounters = new ThriftGroupList(
                JTThriftUtils.toThrift(jip.getJobCounters()));

            return ret;
        }


        /** Returns only active TaskTrackerStatus objects */
        public ThriftTaskTrackerStatusList getActiveTrackers(RequestContext ctx) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftTaskTrackerStatusList>() {
              public ThriftTaskTrackerStatusList run() {
                Collection<TaskTrackerStatus> active = jobTracker.activeTaskTrackers();
                List<ThriftTaskTrackerStatus> trackers =
                    new ArrayList<ThriftTaskTrackerStatus>(active.size());
                for (TaskTrackerStatus t : active) {
                    trackers.add(JTThriftUtils.toThrift(t));
                }
                return new ThriftTaskTrackerStatusList(trackers);
              }
            });
        }

        /** Returns only blacklisted TaskTrackerStatus objects */
        public ThriftTaskTrackerStatusList getBlacklistedTrackers(RequestContext ctx) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftTaskTrackerStatusList>() {
              public ThriftTaskTrackerStatusList run() {
                Collection<TaskTrackerStatus> black = jobTracker.blacklistedTaskTrackers();
                List<ThriftTaskTrackerStatus> trackers =
                    new ArrayList<ThriftTaskTrackerStatus>(black.size());
                for (TaskTrackerStatus t : black) {
                    trackers.add(JTThriftUtils.toThrift(t));
                }
                return new ThriftTaskTrackerStatusList(trackers);
              }
            });
        }

        /** Returns all TaskTrackerStatus objects */
        public ThriftTaskTrackerStatusList getAllTrackers(RequestContext ctx) {
            return assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftTaskTrackerStatusList>() {
              public ThriftTaskTrackerStatusList run() {
                Collection<TaskTrackerStatus> all = jobTracker.taskTrackers();
                List<ThriftTaskTrackerStatus> trackers =
                    new ArrayList<ThriftTaskTrackerStatus>(all.size());
                for (TaskTrackerStatus t : all) {
                    trackers.add(JTThriftUtils.toThrift(t));
                }
                return new ThriftTaskTrackerStatusList(trackers);
              }
            });
        }

        /** Returns a single TaskTrackerStatus object by name */
        public ThriftTaskTrackerStatus getTracker(RequestContext ctx, final String name)
            throws TaskTrackerNotFoundException {
            ThriftTaskTrackerStatus ret = assumeUserContextAndExecute(ctx, new PrivilegedAction<ThriftTaskTrackerStatus>() {
              public ThriftTaskTrackerStatus run() {
                Collection<TaskTrackerStatus> all = jobTracker.taskTrackers();
                for (TaskTrackerStatus t : all) {
                    if (t.getTrackerName().equals(name))
                        return JTThriftUtils.toThrift(t);
                }
                return null;
              }
            });
            if (ret != null)
              return ret;
            else
              throw new TaskTrackerNotFoundException();
        }

        /** Returns the current time in ms on this machine */
        public long getCurrentTime(RequestContext ctx) {
            // This is the call that the JT uses to determine the current time
            return System.currentTimeMillis();
        }

        /** Reads the local jobconf XML file for a given job */
        public String getJobConfXML(RequestContext ctx, final ThriftJobID jobID) throws IOException {
            return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<String>() {
              public String run() throws java.io.IOException {
                /* This always returns a filename of hadoop.log.dir + "/" + jobid + "_conf.xml"
                 * Better check that jobid doesn't contain anything nasty.
                 */
                JobID jid = JTThriftUtils.fromThrift(jobID);
                String jidstring = jid.toString();
                if (jidstring.contains(File.separator) || jidstring.contains(File.pathSeparator)) {
                    throw new IllegalArgumentException("jobConf arguments can't contain path separators");
                }
                String jobFilePath = JobTracker.getLocalJobFilePath(jid);

                StringBuffer fileData = new StringBuffer(1000);
                BufferedReader reader;
                reader = new BufferedReader(
                        new FileReader(jobFilePath));
                char[] buf = new char[1024];
                int numRead=0;
                while((numRead=reader.read(buf)) > 0){
                    fileData.append(buf, 0, numRead);
                }
                reader.close();
                return fileData.toString();
              }
            });
        }

        /** Kill a job by jobid */
        public void killJob(final RequestContext ctx, final ThriftJobID jobID) throws IOException, JobNotFoundException {
            ThriftJobInProgress job = assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<ThriftJobInProgress>() {
              public ThriftJobInProgress run() throws JobNotFoundException {
                return getJob(ctx, jobID);
              }
            });
            if (job == null) {
                throw new JobNotFoundException();
            }

            try {
                final JobID jid = JTThriftUtils.fromThrift(jobID);

                assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
                    public Void run() throws JobNotFoundException {
                        try {
                            jobTracker.killJob(jid);
                        } catch (java.io.IOException e) {
                            throw new JobNotFoundException();
                        }
                        return null;
                    }
                });
            } catch (Throwable t) {
                LOG.info("killJob failed", t);
                throw ThriftUtils.toThrift(t);
            }
        }

        /** Kill a task attempt by taskattemptid */
        public void killTaskAttempt(RequestContext ctx, ThriftTaskAttemptID attemptID)
            throws IOException, TaskAttemptNotFoundException, JobNotFoundException {
            final TaskAttemptID taskid = JTThriftUtils.fromThrift(attemptID);
            final JobID jid = JTThriftUtils.fromThrift(attemptID.taskID.jobID);

            final JobInProgress job = assumeUserContextAndExecute(ctx, new PrivilegedAction<JobInProgress>() {
              public JobInProgress run() {
                return jobTracker.getJob(jid);
              }
            });
            if (job == null) {
              throw new JobNotFoundException();
            }

            final TaskInProgress tip = assumeUserContextAndExecute(ctx, new PrivilegedAction<TaskInProgress>() {
              public TaskInProgress run() {
                return job.getTaskInProgress(taskid.getTaskID());
              }
            });
            if (tip == null) {
                throw new TaskAttemptNotFoundException();
            }

            TaskStatus status = assumeUserContextAndExecute(ctx, new PrivilegedAction<TaskStatus>() {
              public TaskStatus run() {
                return tip.getTaskStatus(taskid);
              }
            });
            if (status == null) {
                throw new TaskAttemptNotFoundException();
            }

            assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
              public Void run() throws java.io.IOException {
                // Second parameter means always kill, don't fail
                if (!jobTracker.killTask(taskid, true)) {
                    throw new RuntimeException();
                }
                return null;
              }
            });
        }

        /** Set a job's priority */
        public void setJobPriority(RequestContext ctx, final ThriftJobID jobID, final ThriftJobPriority priority)
            throws IOException, JobNotFoundException {
            final JobID jid = JTThriftUtils.fromThrift(jobID);
            JobInProgress job = assumeUserContextAndExecute(ctx, new PrivilegedAction<JobInProgress>() {
              public JobInProgress run() {
                return jobTracker.getJob(jid);
              }
            });
            if (job == null) {
              throw new JobNotFoundException();
            }
            assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<Void>() {
              public Void run() throws java.io.IOException {
                jobTracker.setJobPriority(jid, priority.toString());
                return null;
              }
            });
        }

        @Override
        public ThriftDelegationToken getDelegationToken(RequestContext ctx, final String renewer)
            throws IOException, TException {
          return assumeUserContextAndExecute(ctx, new PrivilegedExceptionAction<ThriftDelegationToken>() {
            public ThriftDelegationToken run() throws java.io.IOException {
              Token<DelegationTokenIdentifier> delegationToken;
              try {
                delegationToken = jobTracker.getDelegationToken(new Text(renewer));
              } catch (InterruptedException e) {
                throw new java.io.IOException(e);
              }

              return ThriftUtils.toThrift(delegationToken, JobTracker.getAddress(conf));
            }
          });
        }
    }

    /** Implementation of configurable interface */
    public Configuration getConf() {
        return conf;
    }

    /** Implementation of configurable interface */
    public void setConf(Configuration conf) {
        this.conf = conf;
    }

    /** Creates Thrift processors to handle incoming requests */
    class ProcessorFactory extends TProcessorFactory {

        ProcessorFactory() {
          super(null);
        }

        @Override
        public TProcessor getProcessor(TTransport t) {
          ThriftServerContext context = new ThriftServerContext(t);
          Jobtracker.Iface impl =
            ThriftUtils.SecurityCheckingProxy.create(
              conf,
              new ThriftHandler(context),
              Jobtracker.Iface.class);
          return new Jobtracker.Processor(impl);
        }
    }
}
