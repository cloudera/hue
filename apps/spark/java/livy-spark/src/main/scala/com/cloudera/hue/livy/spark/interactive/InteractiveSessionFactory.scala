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

import java.lang.ProcessBuilder.Redirect

import com.cloudera.hue.livy.sessions.interactive.InteractiveSession
import com.cloudera.hue.livy.sessions.{PySpark, SessionFactory, SessionKindSerializer}
import com.cloudera.hue.livy.spark.SparkProcessBuilder.{AbsolutePath, RelativePath}
import com.cloudera.hue.livy.spark.{SparkProcess, SparkProcessBuilder, SparkProcessBuilderFactory}
import com.cloudera.hue.livy.{LivyConf, Utils}
import org.json4s.{DefaultFormats, Formats, JValue}

object InteractiveSessionFactory {
  private val CONF_LIVY_JAR = "livy.repl.jar"
}

abstract class InteractiveSessionFactory(processFactory: SparkProcessBuilderFactory)
  extends SessionFactory[InteractiveSession] {

  override protected implicit def jsonFormats: Formats = DefaultFormats ++ List(SessionKindSerializer)

  override def create(id: Int, createRequest: JValue) =
    create(id, createRequest.extract[CreateInteractiveRequest])

  def create(id: Int, request: CreateInteractiveRequest): InteractiveSession = {
    val builder = sparkBuilder(id, request)
    val kind = request.kind.toString
    val process = builder.start(AbsolutePath(livyJar(processFactory.livyConf)), List(kind))

    create(id, process, request)
  }

  protected def create(id: Int, process: SparkProcess, request: CreateInteractiveRequest): InteractiveSession

  protected def sparkBuilder(id: Int, request: CreateInteractiveRequest): SparkProcessBuilder = {
    val builder = processFactory.builder()

    builder.className("com.cloudera.hue.livy.repl.Main")
    builder.conf(request.conf)
    request.archives.map(RelativePath).foreach(builder.archive)
    request.driverCores.foreach(builder.driverCores)
    request.driverMemory.foreach(builder.driverMemory)
    request.executorCores.foreach(builder.executorCores)
    request.executorMemory.foreach(builder.executorMemory)
    request.numExecutors.foreach(builder.numExecutors)
    request.files.map(RelativePath).foreach(builder.file)
    request.jars.map(RelativePath).foreach(builder.jar)
    request.proxyUser.foreach(builder.proxyUser)
    request.pyFiles.map(RelativePath).foreach(builder.pyFile)
    request.queue.foreach(builder.queue)
    request.name.foreach(builder.name)

    val callbackUrl = System.getProperty("livy.server.callback-url")
    val driverOptions =
      f"-Dlivy.repl.callback-url=$callbackUrl/sessions/$id/callback " +
      "-Dlivy.repl.port=0"

    builder.conf(
      "spark.driver.extraJavaOptions",
      builder.conf("spark.driver.extraJavaOptions")
        .getOrElse("") + driverOptions,
        admin = true)

    request.kind match {
      case PySpark() => builder.conf("spark.yarn.isPython", "true", admin = true)
      case _ =>
    }

    builder.env("LIVY_PORT", "0")

    builder.redirectOutput(Redirect.PIPE)
    builder.redirectErrorStream(true)

    builder
  }

  private def livyJar(livyConf: LivyConf) = {
    livyConf.getOption(InteractiveSessionFactory.CONF_LIVY_JAR)
      .getOrElse(Utils.jarOfClass(getClass).head)
  }
}
