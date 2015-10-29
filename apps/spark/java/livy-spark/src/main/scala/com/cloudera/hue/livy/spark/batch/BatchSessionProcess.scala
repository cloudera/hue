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
import com.cloudera.hue.livy.sessions.SessionState
import com.cloudera.hue.livy.sessions.batch.BatchSession
import com.cloudera.hue.livy.spark.SparkProcess

import scala.concurrent.{ExecutionContext, ExecutionContextExecutor, Future}

object BatchSessionProcess {
  def apply(id: Int, process: SparkProcess): BatchSession = {
    new BatchSessionProcess(id, process)
  }
}

private class BatchSessionProcess(val id: Int,
                                  process: LineBufferedProcess) extends BatchSession {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private[this] var _state: SessionState = SessionState.Running()

  override def state: SessionState = _state

  override def logLines(): IndexedSeq[String] = process.inputLines

  override def stop(): Future[Unit] = {
    Future {
      destroyProcess()
    }
  }

  private def destroyProcess() = {
    if (process.isAlive) {
      process.destroy()
      reapProcess(process.waitFor())
    }
  }

  private def reapProcess(exitCode: Int) = synchronized {
    if (_state.isActive) {
      if (exitCode == 0) {
        _state = SessionState.Success()
      } else {
        _state = SessionState.Error()
      }
    }
  }

  /** Simple daemon thread to make sure we change state when the process exits. */
  private[this] val thread = new Thread("Batch Process Reaper") {
    override def run(): Unit = {
      reapProcess(process.waitFor())
    }
  }
  thread.setDaemon(true)
  thread.start()
}
