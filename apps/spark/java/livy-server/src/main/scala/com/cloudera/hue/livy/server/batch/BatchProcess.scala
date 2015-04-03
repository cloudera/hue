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

import com.cloudera.hue.livy.LineBufferedProcess
import com.cloudera.hue.livy.spark.SparkSubmitProcessBuilder

import scala.concurrent.{Future, ExecutionContext, ExecutionContextExecutor}

object BatchProcess {
  def apply(id: Int, createBatchRequest: CreateBatchRequest): Batch = {
    val builder = sparkBuilder(createBatchRequest)

    val process = builder.start(createBatchRequest.file, createBatchRequest.args)
    new BatchProcess(id, new LineBufferedProcess(process))
  }

  private def sparkBuilder(createBatchRequest: CreateBatchRequest): SparkSubmitProcessBuilder = {
    val builder = SparkSubmitProcessBuilder()

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

private class BatchProcess(val id: Int,
                           process: LineBufferedProcess) extends Batch {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private[this] var isAlive = true

  override def state: State = {
    if (isAlive) {
      try {
        process.exitValue()
      } catch {
        case e: IllegalThreadStateException => return Running()
      }

      destroyProcess()
    }

    Success()
  }

  override def lines: IndexedSeq[String] = process.stdoutLines

  override def stop(): Future[Unit] = {
    Future {
      destroyProcess()
    }
  }

  private def destroyProcess() = {
    process.destroy()
    process.waitFor()
    isAlive = false
  }
}
