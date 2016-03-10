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
import java.nio.file.{Paths, Files}

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.repl.Interpreter
import com.cloudera.hue.livy.repl.process.ProcessInterpreter
import org.json4s.JsonAST.JObject
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{DefaultFormats, JValue}
import py4j.GatewayServer

import scala.annotation.tailrec
import scala.collection.JavaConversions._

object PythonInterpreter extends Logging {
  def apply(): Interpreter = {
    val pythonExec = sys.env.getOrElse("PYSPARK_DRIVER_PYTHON", "python")

    val gatewayServer = new GatewayServer(null, 0)
    gatewayServer.start()

    val builder = new ProcessBuilder(Seq(pythonExec, createFakeShell().toString))

    val env = builder.environment()

    val pythonPath = sys.env.getOrElse("PYTHONPATH", "")
      .split(File.pathSeparator)
      .++(findPySparkArchives())
      .++(findPyFiles())

    env.put("PYTHONPATH", pythonPath.mkString(File.pathSeparator))
    env.put("PYTHONUNBUFFERED", "YES")
    env.put("PYSPARK_GATEWAY_PORT", "" + gatewayServer.getListeningPort)
    env.put("SPARK_HOME", sys.env.getOrElse("SPARK_HOME", "."))

    builder.redirectError(Redirect.PIPE)

    val process = builder.start()

    new PythonInterpreter(process, gatewayServer)
  }

  private def findPySparkArchives(): Seq[String] = {
    sys.env.get("PYSPARK_ARCHIVES_PATH")
      .map(_.split(",").toSeq)
      .getOrElse {
        sys.env.get("SPARK_HOME").map { sparkHome =>
          val pyLibPath = Seq(sparkHome, "python", "lib").mkString(File.separator)
          val pyArchivesFile = new File(pyLibPath, "pyspark.zip")
          require(pyArchivesFile.exists(),
            "pyspark.zip not found in Spark environment; cannot run pyspark application in YARN mode.")

          val py4jFile = Files.newDirectoryStream(Paths.get(pyLibPath), "py4j-*-src.zip")
            .iterator()
            .next()
            .toFile

          require(py4jFile.exists(),
            "py4j-*-src.zip not found in Spark environment; cannot run pyspark application in YARN mode.")
          Seq(pyArchivesFile.getAbsolutePath, py4jFile.getAbsolutePath)
        }.getOrElse(Seq())
      }
  }

  private def findPyFiles(): Seq[String] = {
    val pyFiles = sys.props.getOrElse("spark.submit.pyFiles", "").split(",")

    if (sys.env.getOrElse("SPARK_YARN_MODE", "") == "true") {
      // In spark mode, these files have been localized into the current directory.
      pyFiles.map { file =>
        val name = new File(file).getName
        new File(name).getAbsolutePath
      }
    } else {
      pyFiles
    }
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
}

private class PythonInterpreter(process: Process, gatewayServer: GatewayServer)
  extends ProcessInterpreter(process)
  with Logging
{
  implicit val formats = DefaultFormats

  override def kind = "pyspark"

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

  override protected def sendExecuteRequest(code: String): Interpreter.ExecuteResponse = {
    sendRequest(Map("msg_type" -> "execute_request", "content" -> Map("code" -> code))) match {
      case Some(response) =>
        assert((response \ "msg_type").extract[String] == "execute_reply")

        val content = response \ "content"

        (content \ "status").extract[String] match {
          case "ok" =>
            Interpreter.ExecuteSuccess((content \ "data").extract[JObject])
          case "error" =>
            val ename = (content \ "ename").extract[String]
            val evalue = (content \ "evalue").extract[String]
            val traceback = (content \ "traceback").extract[Seq[String]]

            Interpreter.ExecuteError(ename, evalue, traceback)
          case status =>
            Interpreter.ExecuteError("Internal Error", f"Unknown status $status")
        }
      case None =>
        Interpreter.ExecuteAborted(takeErrorLines())
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

    Option(stdout.readLine()).map { case line =>
      parse(line)
    }
  }
}
