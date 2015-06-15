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

import com.cloudera.hue.livy.sessions.{Success, Running, State}
import com.cloudera.hue.livy.spark.SparkSubmitProcessBuilder.RelativePath
import com.cloudera.hue.livy.{LivyConf, LineBufferedProcess}
import com.cloudera.hue.livy.spark.SparkSubmitProcessBuilder

import scala.concurrent.{Future, ExecutionContext, ExecutionContextExecutor}

object BatchSessionProcess {
  def apply(livyConf: LivyConf, id: Int, createBatchRequest: CreateBatchRequest): BatchSession = {
    val builder = sparkBuilder(livyConf, createBatchRequest)

    val process = builder.start(RelativePath(createBatchRequest.file), createBatchRequest.args)
    new BatchSessionProcess(id, process)
  }

  private def sparkBuilder(livyConf: LivyConf, createBatchRequest: CreateBatchRequest): SparkSubmitProcessBuilder = {
    val builder = SparkSubmitProcessBuilder(livyConf)

    createBatchRequest.className.foreach(builder.className)
    createBatchRequest.jars.map(RelativePath).foreach(builder.jar)
    createBatchRequest.pyFiles.map(RelativePath).foreach(builder.pyFile)
    createBatchRequest.files.map(RelativePath).foreach(builder.file)
    createBatchRequest.driverMemory.foreach(builder.driverMemory)
    createBatchRequest.driverCores.foreach(builder.driverCores)
    createBatchRequest.executorMemory.foreach(builder.executorMemory)
    createBatchRequest.executorCores.foreach(builder.executorCores)
    createBatchRequest.numExecutors.foreach(builder.numExecutors)
    createBatchRequest.archives.map(RelativePath).foreach(builder.archive)
    createBatchRequest.proxyUser.foreach(builder.proxyUser)

    builder.redirectOutput(Redirect.PIPE)
    builder.redirectErrorStream(true)

    builder
  }
}

private class BatchSessionProcess(val id: Int,
                           process: LineBufferedProcess) extends BatchSession {
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

  override def logLines(): IndexedSeq[String] = process.inputLines

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
