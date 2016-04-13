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

import java.io.{File, IOException}
import javax.servlet.ServletContext

import com.cloudera.hue.livy._
import com.cloudera.hue.livy.server.batch.BatchSessionServlet
import com.cloudera.hue.livy.server.interactive.InteractiveSessionServlet
import com.cloudera.hue.livy.spark.SparkManager
import org.scalatra._
import org.scalatra.metrics.MetricsBootstrap
import org.scalatra.metrics.MetricsSupportExtensions._
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
    testSparkHome(livyConf)
    testSparkSubmit(livyConf)

    val server = new WebServer(livyConf, host, port)

    server.context.setResourceBase("src/main/com/cloudera/hue/livy/server")
    server.context.setInitParameter(ScalatraListener.LifeCycleKey, classOf[ScalatraBootstrap].getCanonicalName)
    server.context.addEventListener(new ScalatraListener)

    server.start()

    try {
      if (!sys.props.contains("livy.server.serverUrl")) {
        sys.props("livy.server.serverUrl") = f"http://${server.host}:${server.port}"
      }
    } finally {
      server.join()
      server.stop()

      // Make sure to close all our outstanding http requests.
      dispatch.Http.shutdown()
    }
  }

  /**
   * Sets the spark-submit path if it's not configured in the LivyConf
   */
  private def testSparkHome(livyConf: LivyConf) = {
    val sparkHome = livyConf.sparkHome().getOrElse {
      System.err.println("Livy requires the SPARK_HOME environment variable")
      sys.exit(1)
    }

    val sparkHomeFile = new File(sparkHome)

    if (!sparkHomeFile.exists) {
      System.err.println("SPARK_HOME path does not exist")
      sys.exit(1)
    }
  }

  /**
   * Test that the configured `spark-submit` executable exists.
   *
   * @param livyConf
   */
  private def testSparkSubmit(livyConf: LivyConf) = {
    try {
      val versions_regex = (
        """^(?:""" +
          """(1\.3\.0)|""" +
          """(1\.3\.1)|""" +
          """(1\.4\.0)|""" +
          """(1\.4\.1)|""" +
          """(1\.5\.0)|""" +
          """(1\.5\.1)""" +
        """)(-.*)?"""
      ).r

      val version = sparkSubmitVersion(livyConf)

      versions_regex.findFirstIn(version) match {
        case Some(_) =>
          logger.info(f"Using spark-submit version $version")
        case None =>
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

    val regex = """version (.*)""".r.unanchored

    output match {
      case regex(version) => version
      case _ => throw new IOException(f"Unable to determine spark-submit version [$exitCode]:\n$output")
    }
  }

}

class ScalatraBootstrap
  extends LifeCycle
  with Logging
  with MetricsBootstrap {

  var sparkManager: SparkManager = null

  override def init(context: ServletContext): Unit = {
    try {
      val livyConf = new LivyConf()
      sparkManager = SparkManager(livyConf)

      context.mount(new InteractiveSessionServlet(sparkManager.interactiveManager), "/sessions/*")
      context.mount(new BatchSessionServlet(sparkManager.batchManager), "/batches/*")
      context.mountMetricsAdminServlet("/")

      context.initParameters(org.scalatra.EnvironmentKey) = livyConf.get("livy.environment", "development")
    } catch {
      case e: Throwable =>
        println(f"Exception thrown when initializing server: $e")
        sys.exit(1)
    }
  }

  override def destroy(context: ServletContext): Unit = {
    if (sparkManager != null) {
      sparkManager.shutdown()
      sparkManager = null
    }
  }
}
