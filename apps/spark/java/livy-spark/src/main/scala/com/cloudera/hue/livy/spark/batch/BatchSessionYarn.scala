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

package com.cloudera.hue.livy.spark.batch

import com.cloudera.hue.livy.LineBufferedProcess
import com.cloudera.hue.livy.sessions._
import com.cloudera.hue.livy.sessions.batch.BatchSession
import com.cloudera.hue.livy.spark.SparkProcess
import com.cloudera.hue.livy.yarn._

import scala.annotation.tailrec
import scala.concurrent.{ExecutionContext, ExecutionContextExecutor, Future}

object BatchSessionYarn {
  implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  def apply(client: Client, id: Int, process: SparkProcess): BatchSession = {
    val job = Future {
      client.getJobFromProcess(process)
    }
    new BatchSessionYarn(id, process, job)
  }
}

private class BatchSessionYarn(val id: Int, process: LineBufferedProcess, jobFuture: Future[Job]) extends BatchSession {

  implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private var _state: SessionState = SessionState.Starting()

  private var _jobThread: Thread = _

  jobFuture.onComplete {
    case util.Failure(_) =>
      _state = SessionState.Error()

    case util.Success(job) =>
      _state = SessionState.Running()

      _jobThread = new Thread {
        override def run(): Unit = {
          @tailrec
          def aux(): Unit = {
            if (_state == SessionState.Running()) {
              Thread.sleep(5000)
              job.getStatus match {
                case ApplicationState.SuccessfulFinish() =>
                  _state = SessionState.Success()
                case ApplicationState.UnsuccessfulFinish() =>
                  _state = SessionState.Error()
                case _ => aux()
              }
            }
          }

          aux()
        }
      }
      _jobThread.setDaemon(true)
      _jobThread.start()
  }

  override def state: SessionState = _state

  override def stop(): Future[Unit] = {
    jobFuture.map { job =>
      job.stop()
      _state = SessionState.Success()
      ()
    }
  }

  override def logLines(): IndexedSeq[String] = process.inputLines
}
