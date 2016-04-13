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

package com.cloudera.hue.livy.spark.interactive

import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.sessions.SessionState
import com.cloudera.hue.livy.sessions.interactive.InteractiveSession
import com.cloudera.hue.livy.spark.SparkProcess
import com.cloudera.hue.livy.yarn.Client

import scala.concurrent.duration._
import scala.concurrent.{Await, ExecutionContext, ExecutionContextExecutor, Future}

object InteractiveSessionYarn {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private lazy val regex = """Application report for (\w+)""".r.unanchored

  def apply(client: Client,
            id: Int,
            process: SparkProcess,
            request: CreateInteractiveRequest): InteractiveSession = {
    new InteractiveSessionYarn(id, client, process, request)
  }
}

private class InteractiveSessionYarn(id: Int,
                                     client: Client,
                                     process: SparkProcess,
                                     request: CreateInteractiveRequest)
  extends InteractiveWebSession(id, process, request) {

  private val job = Future {
    val job = client.getJobFromProcess(process)

    job
  }

  job.onFailure { case _ =>
    _state = SessionState.Error()
  }

  override def logLines() = process.inputLines

  override def stop(): Future[Unit] = {
    super.stop().andThen {
      case _ =>
        try {
          val job_ = Await.result(job, Duration(10, TimeUnit.SECONDS))
          job_.waitForFinish(10000).getOrElse {
            job_.stop()
          }
        } catch {
          case e: Throwable =>
            _state = SessionState.Error()
            throw e
        }
    }
  }
}
