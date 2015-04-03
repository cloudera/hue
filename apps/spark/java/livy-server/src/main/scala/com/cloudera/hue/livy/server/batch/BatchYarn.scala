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

package com.cloudera.hue.livy.server.batch

import java.lang.ProcessBuilder.Redirect

import com.cloudera.hue.livy.LivyConf
import com.cloudera.hue.livy.spark.SparkSubmitProcessBuilder
import com.cloudera.hue.livy.yarn._

import scala.annotation.tailrec
import scala.concurrent.{ExecutionContextExecutor, ExecutionContext, Future}
import scala.util.{Failure, Success}

object BatchYarn {

  implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  def apply(livyConf: LivyConf, client: Client, id: Int, createBatchRequest: CreateBatchRequest): Batch = {
    val builder = sparkBuilder(createBatchRequest)

    val process = builder.start(createBatchRequest.file, createBatchRequest.args)
    new BatchYarn(id, Future { client.getJobFromProcess(process) })
  }

  private def sparkBuilder(createBatchRequest: CreateBatchRequest): SparkSubmitProcessBuilder = {
    val builder = SparkSubmitProcessBuilder()

    builder.master("yarn-cluster")

    createBatchRequest.className.foreach(builder.className)
    createBatchRequest.jars.foreach(builder.jar)
    createBatchRequest.pyFiles.foreach(builder.pyFile)
    createBatchRequest.files.foreach(builder.file)
    createBatchRequest.driverMemory.foreach(builder.driverMemory)
    createBatchRequest.driverCores.foreach(builder.driverCores)
    createBatchRequest.executorMemory.foreach(builder.executorMemory)
    createBatchRequest.executorCores.foreach(builder.executorCores)
    createBatchRequest.archives.foreach(builder.archive)

    builder.redirectOutput(Redirect.PIPE)

    builder
  }
}

private class BatchYarn(val id: Int, jobFuture: Future[Job]) extends Batch {

  implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private var _state: State = Starting()

  private var _jobThread: Thread = _

  jobFuture.onComplete {
    case Failure(_) => _state = Error()
    case Success(job) =>
      _state = Running()

      _jobThread = new Thread {
        override def run(): Unit = {
          @tailrec
          def aux(): Unit = {
            if (_state == Running()) {
              Thread.sleep(5000)
              job.getStatus match {
                case Client.SuccessfulFinish() =>
                  _state = Dead()
                case Client.UnsuccessfulFinish() =>
                  _state = Error()
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

  override def state: State = _state

  override def stop(): Future[Unit] = {
    jobFuture.map { job =>
      job.stop()
      _state = Dead()
      ()
    }
  }

  override def lines: IndexedSeq[String] = IndexedSeq()
}
