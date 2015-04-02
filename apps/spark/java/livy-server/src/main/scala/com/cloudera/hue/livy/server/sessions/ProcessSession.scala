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
import java.net.URL

import com.cloudera.hue.livy.sessions.Kind
import com.cloudera.hue.livy.spark.SparkSubmitProcessBuilder
import com.cloudera.hue.livy.{LivyConf, Logging, Utils}

import scala.annotation.tailrec
import scala.collection.JavaConversions._
import scala.collection.mutable.ArrayBuffer
import scala.concurrent.Future
import scala.io.Source

object ProcessSession extends Logging {

  val CONF_LIVY_REPL_JAR = "livy.repl.jar"
  val CONF_LIVY_REPL_CALLBACK_URL = "livy.repl.callback-url"
  val CONF_LIVY_REPL_DRIVER_CLASS_PATH = "livy.repl.driverClassPath"

  def create(livyConf: LivyConf, id: String, kind: Kind, proxyUser: Option[String] = None): Session = {
    val process = startProcess(livyConf, id, kind, proxyUser)
    new ProcessSession(id, kind, proxyUser, process)
  }

  // Loop until we've started a process with a valid port.
  private def startProcess(livyConf: LivyConf, id: String, kind: Kind, proxyUser: Option[String]): Process = {

    val builder = new SparkSubmitProcessBuilder()

    builder.className("com.cloudera.hue.livy.repl.Main")

    sys.env.get("LIVY_REPL_JAVA_OPTS").foreach(builder.driverJavaOptions)
    livyConf.getOption(CONF_LIVY_REPL_DRIVER_CLASS_PATH).foreach(builder.driverClassPath)
    proxyUser.foreach(builder.proxyUser)

    livyConf.getOption(CONF_LIVY_REPL_CALLBACK_URL).foreach { case callbackUrl =>
      builder.env("LIVY_CALLBACK_URL", f"$callbackUrl/sessions/$id/callback")
    }

    builder.env("LIVY_PORT", "0")

    builder.redirectOutput(Redirect.PIPE)
    builder.redirectError(Redirect.INHERIT)

    builder.start(livyJar(livyConf), List(kind.toString))
  }

  private def livyJar(conf: LivyConf): String = {
    conf.getOption(CONF_LIVY_REPL_JAR).getOrElse {
      Utils.jarOfClass(getClass).head
    }
  }
}

private class ProcessSession(id: String,
                             kind: Kind,
                             proxyUser: Option[String],
                             process: Process) extends WebSession(id, kind, proxyUser) {

  val stdoutThread = new Thread {
    override def run() = {
      val regex = """Starting livy-repl on (https?://.*)""".r

      val lines = Source.fromInputStream(process.getInputStream).getLines()

      // Loop until we find the ip address to talk to livy-repl.
      @tailrec
      def readUntilURL(): Boolean = {
        if (lines.hasNext) {
          val line = lines.next()
          println(line)

          line match {
            case regex(url_) =>
              url = new URL(url_)
              true
            case _ => readUntilURL()
          }
        } else {
          false
        }
      }

      if (readUntilURL()) {
        for (line <- lines) {
          println(line)
        }
      }
    }
  }

  stdoutThread.setName("process session stdout reader")
  stdoutThread.setDaemon(true)
  stdoutThread.start()

  override def stop(): Future[Unit] = {
    super.stop() andThen { case r =>
      // Make sure the process is reaped.
      process.waitFor()
      stdoutThread.join()

      r
    }
  }
}
