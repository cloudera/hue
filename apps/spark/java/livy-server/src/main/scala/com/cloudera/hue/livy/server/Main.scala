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

package com.cloudera.hue.livy.server

import java.io.IOException
import javax.servlet.ServletContext

import com.cloudera.hue.livy._
import com.cloudera.hue.livy.server.batch._
import com.cloudera.hue.livy.server.interactive._
import org.scalatra._
import org.scalatra.servlet.ScalatraListener
import org.slf4j.LoggerFactory

object Main {

  val SESSION_KIND = "livy-server.session.kind"
  val PROCESS_SESSION = "process"
  val YARN_SESSION = "yarn"
  lazy val logger = LoggerFactory.getLogger(this.getClass)

  def main(args: Array[String]): Unit = {
    val livyConf = new LivyConf()
    Utils.loadDefaultLivyProperties(livyConf)

    val host = livyConf.get("livy.server.host", "0.0.0.0")
    val port = livyConf.getInt("livy.server.port", 8998)

    // Make sure the `spark-submit` program exists, otherwise much of livy won't work.
    testSparkSubmit(livyConf)

    val server = new WebServer(host, port)

    server.context.setResourceBase("src/main/com/cloudera/hue/livy/server")
    server.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
    server.context.addEventListener(new ScalatraListener)

    server.start()

    try {
      System.setProperty("livy.server.callback-url", f"http://${server.host}:${server.port}")
    } finally {
      server.join()
      server.stop()

      // Make sure to close all our outstanding http requests.
      dispatch.Http.shutdown()
    }
  }

  /**
   * Test that the configured `spark-submit` executable exists.
   *
   * @param livyConf
   */
  private def testSparkSubmit(livyConf: LivyConf) = {
    try {
      // Ignore the version for now.
      val version = sparkSubmitVersion(livyConf)
      version match {
        case "1.3.0" | "1.3.1" =>
          logger.info(f"Using spark-submit version $version")
        case _ =>
          logger.warn(f"Warning, livy has not been tested with spark-submit version $version")
      }
    } catch {
      case e: IOException =>
        System.err.println("Failed to run spark-submit executable: " + e.toString)
        System.exit(1)
    }
  }

  /**
   * Return the version of the configured `spark-submit` version.
   *
   * @param livyConf
   * @return the version
   */
  private def sparkSubmitVersion(livyConf: LivyConf): String = {
    val sparkSubmit = livyConf.sparkSubmit()
    val pb = new ProcessBuilder(sparkSubmit, "--version")
    pb.redirectErrorStream(true)
    pb.redirectInput(ProcessBuilder.Redirect.PIPE)

    val process = new LineBufferedProcess(pb.start())
    val exitCode = process.waitFor()
    val output = process.inputIterator.mkString("\n")

    if (exitCode != 1) {
      throw new IOException(f"spark-submit had an unexpected exit [$exitCode]:\n$output]")
    }

    val regex = """version (.*)""".r.unanchored

    output match {
      case regex(version) => version
      case _ => throw new IOException(f"Unable to determing spark-submit version:\n$output")
    }
  }
}

class ScalatraBootstrap extends LifeCycle with Logging {

  var sessionManager: SessionManager[InteractiveSession] = null
  var batchManager: SessionManager[BatchSession] = null

  override def init(context: ServletContext): Unit = {
    val livyConf = new LivyConf()

    val sessionFactoryKind = try {
      livyConf.sessionKind()
    } catch {
      case e: IllegalStateException =>
        println(f"Unknown session factory: $e}")
        sys.exit(1)
    }

    info(f"Using $sessionFactoryKind sessions")

    val (sessionFactory, batchFactory) = sessionFactoryKind match {
      case LivyConf.Process() =>
        (new InteractiveSessionProcessFactory(livyConf), new BatchSessionProcessFactory(livyConf))
      case LivyConf.Yarn() =>
        (new InteractiveSessionYarnFactory(livyConf), new BatchSessionYarnFactory(livyConf))
    }

    sessionManager = new SessionManager(sessionFactory)
    batchManager = new SessionManager(batchFactory)

    context.mount(new InteractiveSessionServlet(sessionManager), "/sessions/*")
    context.mount(new BatchSessionServlet(batchManager), "/batches/*")
  }

  override def destroy(context: ServletContext): Unit = {
    if (sessionManager != null) {
      sessionManager.shutdown()
    }

    if (batchManager != null) {
      batchManager.shutdown()
    }
  }
}
