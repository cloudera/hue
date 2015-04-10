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

package com.cloudera.hue.livy.server.sessions

import java.lang.ProcessBuilder.Redirect
import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.spark.SparkSubmitProcessBuilder
import com.cloudera.hue.livy.{LineBufferedProcess, Utils, LivyConf}
import com.cloudera.hue.livy.sessions.{Kind, Error}
import com.cloudera.hue.livy.yarn.{Client, Job}

import scala.concurrent.{Await, ExecutionContext, ExecutionContextExecutor, Future}
import scala.concurrent.duration._

object YarnSession {
  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private val CONF_LIVY_JAR = "livy.yarn.jar"
  private lazy val regex = """Application report for (\w+)""".r.unanchored

  def create(livyConf: LivyConf, client: Client, id: Int, kind: Kind, proxyUser: Option[String] = None): Session = {
    val callbackUrl = System.getProperty("livy.server.callback-url")
    val url = f"$callbackUrl/sessions/$id/callback"

    val builder = SparkSubmitProcessBuilder()

    builder.master("yarn-cluster")
    builder.className("com.cloudera.hue.livy.repl.Main")
    builder.driverJavaOptions(f"-Dlivy.repl.callback-url=$url -Dlivy.repl.port=0")
    proxyUser.foreach(builder.proxyUser)

    builder.redirectOutput(Redirect.PIPE)
    builder.redirectErrorStream(redirect = true)

    val process = builder.start(livyJar(livyConf), List(kind.toString))

    val job = Future {
      val proc = new LineBufferedProcess(process)
      val job = client.getJobFromProcess(proc)

      // We don't need the process anymore.
      proc.destroy()

      job
    }

    new YarnSession(id, kind, proxyUser, job)
  }

  private def livyJar(livyConf: LivyConf) = {
    if (livyConf.contains(CONF_LIVY_JAR)) {
      livyConf.get(CONF_LIVY_JAR)
    } else {
      Utils.jarOfClass(classOf[Client]).head
    }
  }
}

private class YarnSession(id: Int,
                          kind: Kind,
                          proxyUser: Option[String],
                          job: Future[Job]) extends WebSession(id, kind, proxyUser) {
  job.onFailure { case _ =>
    _state = Error()
  }

  override def stop(): Future[Unit] = {
    super.stop().andThen {
      case _ =>
        try {
          val job_ = Await.result(job, Duration(1, TimeUnit.SECONDS))
          job_.waitForFinish(10000)
        } catch {
          case e: Throwable =>
            _state = Error()
            throw e
        }
    }
  }
}
