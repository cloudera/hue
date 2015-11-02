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

import java.lang.ProcessBuilder.Redirect

import com.cloudera.hue.livy.sessions.SessionFactory
import com.cloudera.hue.livy.sessions.batch.BatchSession
import com.cloudera.hue.livy.spark.SparkProcessBuilder.RelativePath
import com.cloudera.hue.livy.spark.{SparkProcess, SparkProcessBuilder, SparkProcessBuilderFactory}
import org.json4s.JValue

abstract class BatchSessionFactory(factory: SparkProcessBuilderFactory) extends SessionFactory[BatchSession] {
  override def create(id: Int, createRequest: JValue) =
    create(id, createRequest.extract[CreateBatchRequest])

  def create(id: Int, request: CreateBatchRequest): BatchSession = {
    val builder = sparkBuilder(request)
    val process = builder.start(RelativePath(request.file), request.args)
    create(id, process)
  }

  protected def create(id: Int, process: SparkProcess): BatchSession

  protected def sparkBuilder(request: CreateBatchRequest): SparkProcessBuilder = {
    val builder = factory.builder()
    builder.conf(request.conf)
    request.proxyUser.foreach(builder.proxyUser)
    request.className.foreach(builder.className)
    request.jars.map(RelativePath).foreach(builder.jar)
    request.pyFiles.map(RelativePath).foreach(builder.pyFile)
    request.files.map(RelativePath).foreach(builder.file)
    request.driverMemory.foreach(builder.driverMemory)
    request.driverCores.foreach(builder.driverCores)
    request.executorMemory.foreach(builder.executorMemory)
    request.executorCores.foreach(builder.executorCores)
    request.numExecutors.foreach(builder.numExecutors)
    request.archives.map(RelativePath).foreach(builder.archive)
    request.queue.foreach(builder.queue)
    request.name.foreach(builder.name)

    builder.redirectOutput(Redirect.PIPE)
    builder.redirectErrorStream(true)

    builder
  }
}
