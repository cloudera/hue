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

package com.cloudera.hue.livy.server.interactive

import java.lang.ProcessBuilder.Redirect
import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.sessions.Error
import com.cloudera.hue.livy.spark.{SparkProcess, SparkSubmitProcessBuilder}
import com.cloudera.hue.livy.spark.SparkSubmitProcessBuilder.{RelativePath, AbsolutePath}
import com.cloudera.hue.livy.yarn.{Client, Job}
import com.cloudera.hue.livy.{LineBufferedProcess, LivyConf, Utils}

import scala.concurrent.duration._
import scala.concurrent.{Await, ExecutionContext, ExecutionContextExecutor, Future}

object InteractiveSessionYarn {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private val CONF_LIVY_JAR = "livy.yarn.jar"
  private lazy val regex = """Application report for (\w+)""".r.unanchored

  def create(livyConf: LivyConf,
             client: Client,
             id: Int,
             createInteractiveRequest: CreateInteractiveRequest): InteractiveSession = {
    val callbackUrl = System.getProperty("livy.server.callback-url")
    val url = f"$callbackUrl/sessions/$id/callback"

    val builder = SparkSubmitProcessBuilder(livyConf)

    builder.master("yarn-cluster")
    builder.className("com.cloudera.hue.livy.repl.Main")
    builder.driverJavaOptions(f"-Dlivy.repl.callback-url=$url -Dlivy.repl.port=0")
    createInteractiveRequest.archives.map(RelativePath).foreach(builder.archive)
    createInteractiveRequest.driverCores.foreach(builder.driverCores)
    createInteractiveRequest.driverMemory.foreach(builder.driverMemory)
    createInteractiveRequest.executorCores.foreach(builder.executorCores)
    createInteractiveRequest.executorMemory.foreach(builder.executorMemory)
    createInteractiveRequest.files.map(RelativePath).foreach(builder.file)
    createInteractiveRequest.jars.map(RelativePath).foreach(builder.jar)
    createInteractiveRequest.proxyUser.foreach(builder.proxyUser)
    createInteractiveRequest.pyFiles.map(RelativePath).foreach(builder.pyFile)

    builder.redirectOutput(Redirect.PIPE)
    builder.redirectErrorStream(true)

    val process = builder.start(AbsolutePath(livyJar(livyConf)), List(createInteractiveRequest.kind.toString))

    new InteractiveSessionYarn(id, client, process, createInteractiveRequest)
  }

  private def livyJar(livyConf: LivyConf) = {
    if (livyConf.contains(CONF_LIVY_JAR)) {
      livyConf.get(CONF_LIVY_JAR)
    } else {
      Utils.jarOfClass(classOf[Client]).head
    }
  }
}

private class InteractiveSessionYarn(id: Int,
                                     client: Client,
                                     process: SparkProcess,
                                     createInteractiveRequest: CreateInteractiveRequest)
  extends InteractiveWebSession(id, createInteractiveRequest) {

  private val job = Future {
    val job = client.getJobFromProcess(process)

    job
  }

  job.onFailure { case _ =>
    _state = Error()
  }

  override def logLines() = process.inputLines

  override def stop(): Future[Unit] = {
    process.destroy()

    super.stop().andThen {
      case _ =>
        try {
          val job_ = Await.result(job, Duration(10, TimeUnit.SECONDS))
          job_.waitForFinish(10000).getOrElse {
            job_.stop()
          }
        } catch {
          case e: Throwable =>
            _state = Error()
            throw e
        }
    }
  }
}
