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

package com.cloudera.hue.livy.repl.python

import java.io._
import java.lang.ProcessBuilder.Redirect
import java.nio.file.Files

import com.cloudera.hue.livy.repl.Interpreter
import com.cloudera.hue.livy.repl.process.ProcessInterpreter
import com.cloudera.hue.livy.{Logging, Utils}
import org.apache.spark.SparkContext
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, JValue}
import py4j.GatewayServer

import scala.annotation.tailrec
import scala.collection.JavaConversions._
import scala.collection.mutable.ArrayBuffer
import scala.concurrent.ExecutionContext

object PythonInterpreter {
  def create(): Interpreter = {
    val pythonExec = sys.env.getOrElse("PYSPARK_DRIVER_PYTHON", "python")

    val gatewayServer = new GatewayServer(null, 0)
    gatewayServer.start()

    val builder = new ProcessBuilder(Seq(
      pythonExec,
      createFakeShell().toString
    ))

    val env = builder.environment()
    env.put("PYTHONPATH", pythonPath)
    env.put("PYTHONUNBUFFERED", "YES")
    env.put("PYSPARK_GATEWAY_PORT", "" + gatewayServer.getListeningPort)
    env.put("SPARK_HOME", sys.env.getOrElse("SPARK_HOME", "."))

    builder.redirectError(Redirect.INHERIT)

    val process = builder.start()

    new PythonInterpreter(process, gatewayServer)
  }

  private def pythonPath = {
    val pythonPath = new ArrayBuffer[String]
    for (sparkHome <- sys.env.get("SPARK_HOME")) {
      pythonPath += Seq(sparkHome, "python", "lib", "pyspark.zip").mkString(File.separator)
      pythonPath += Seq(sparkHome, "python", "lib", "py4j-0.8.2.1-src.zip").mkString(File.separator)
    }
    pythonPath ++= Utils.jarOfClass(classOf[SparkContext])
    pythonPath.mkString(File.pathSeparator)
  }

  private def createFakeShell(): File = {
    val source: InputStream = getClass.getClassLoader.getResourceAsStream("fake_shell.py")

    val file = Files.createTempFile("", "").toFile
    file.deleteOnExit()

    val sink = new FileOutputStream(file)
    val buf = new Array[Byte](1024)
    var n = source.read(buf)

    while (n > 0) {
      sink.write(buf, 0, n)
      n = source.read(buf)
    }

    source.close()
    sink.close()

    file
  }

  private def createFakePySpark(): File = {
    val source: InputStream = getClass.getClassLoader.getResourceAsStream("fake_pyspark.sh")

    val file = Files.createTempFile("", "").toFile
    file.deleteOnExit()

    file.setExecutable(true)

    val sink = new FileOutputStream(file)
    val buf = new Array[Byte](1024)
    var n = source.read(buf)

    while (n > 0) {
      sink.write(buf, 0, n)
      n = source.read(buf)
    }

    source.close()
    sink.close()

    file
  }
}

private class PythonInterpreter(process: Process, gatewayServer: GatewayServer)
  extends ProcessInterpreter(process)
  with Logging
{
  implicit val formats = DefaultFormats

  override def close(): Unit = {
    try {
      super.close()
    } finally {
      gatewayServer.shutdown()
    }
  }

  @tailrec
  final override protected def waitUntilReady(): Unit = {
    val line = stdout.readLine()
    line match {
      case null | "READY" =>
      case _ => waitUntilReady()
    }
  }

  override protected def sendExecuteRequest(code: String): Option[JValue] = {
    val rep = sendRequest(Map("msg_type" -> "execute_request", "content" -> Map("code" -> code)))
    rep.map { case rep =>
      assert((rep \ "msg_type").extract[String] == "execute_reply")

      val content: JValue = rep \ "content"

      content
    }
  }

  override protected def sendShutdownRequest(): Unit = {
    sendRequest(Map(
      "msg_type" -> "shutdown_request",
      "content" -> ()
    )).foreach { case rep =>
      warn(f"process failed to shut down while returning $rep")
    }
  }

  private def sendRequest(request: Map[String, Any]): Option[JValue] = {
    stdin.println(write(request))
    stdin.flush()

    Option(stdout.readLine()).map { case line => parse(line) }
  }
}
