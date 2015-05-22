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
import java.util.concurrent.{SynchronousQueue, TimeUnit}

import com.cloudera.hue.livy.repl.Interpreter
import com.cloudera.hue.livy.sessions._
import com.cloudera.hue.livy.{Logging, Utils}
import org.apache.spark.SparkContext
import org.json4s.{DefaultFormats, JValue}
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import py4j.GatewayServer

import scala.annotation.tailrec
import scala.collection.JavaConversions._
import scala.collection.mutable.ArrayBuffer
import scala.concurrent.duration.Duration
import scala.concurrent.{Await, Future, Promise}

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
    env.put("PYTHONPATH", pythonPath.mkString(File.pathSeparator))
    env.put("PYTHONUNBUFFERED", "YES")
    env.put("PYSPARK_GATEWAY_PORT", "" + gatewayServer.getListeningPort)
    env.put("SPARK_HOME", sys.env.getOrElse("SPARK_HOME", "."))

    builder.redirectError(Redirect.INHERIT)

    val process = builder.start()

    new PythonInterpreter(process, gatewayServer)
  }

  private def pythonPath = {
    val pythonPath = new ArrayBuffer[String]
    pythonPath ++= Utils.jarOfClass(classOf[SparkContext])
    pythonPath
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
  extends Interpreter
  with Logging
{
  implicit val formats = DefaultFormats

  private val stdin = new PrintWriter(process.getOutputStream)
  private val stdout = new BufferedReader(new InputStreamReader(process.getInputStream), 1)

  private[this] var _state: State = Starting()
  private[this] val _queue = new SynchronousQueue[Request]

  override def state: State = _state

  override def execute(code: String): Future[JValue] = {
    val promise = Promise[JValue]()
    _queue.put(ExecuteRequest(code, promise))
    promise.future
  }

  override def close(): Unit = {
    _state match {
      case Dead() =>
      case ShuttingDown() =>
        // Another thread must be tearing down the process.
        waitForStateChange(ShuttingDown(), Duration(10, TimeUnit.SECONDS))
      case _ =>
        val promise = Promise[Unit]()
        _queue.put(ShutdownRequest(promise))

        // Give ourselves 10 seconds to tear down the process.
        try {
          Await.result(promise.future, Duration(10, TimeUnit.SECONDS))
          thread.join()
        } finally {
          gatewayServer.shutdown()
        }
    }
  }

  @tailrec
  private def waitUntilReady(): Unit = {
    val line = stdout.readLine()
    line match {
      case null | "READY" =>
      case _ => waitUntilReady()
    }
  }

  private[this] val thread = new Thread {
    override def run() = {
      waitUntilReady()

      _state = Idle()

      loop()
    }

    @tailrec
    private def waitUntilReady(): Unit = {
      val line = stdout.readLine()
      line match {
        case null | "READY" =>
        case _ => waitUntilReady()
      }
    }

    private def sendRequest(request: Map[String, Any]): Option[JValue] = {
      stdin.println(write(request))
      stdin.flush()

      Option(stdout.readLine()).map { case line => parse(line) }
    }

    @tailrec
    def loop(): Unit = {
      (_state, _queue.take()) match {
        case (Error(), ExecuteRequest(code, promise)) =>
          promise.failure(new Exception("session has been terminated"))
          loop()

        case (state, ExecuteRequest(code, promise)) =>
          require(state == Idle())

          _state = Busy()

          sendRequest(Map("msg_type" -> "execute_request", "content" -> Map("code" -> code))) match {
            case Some(rep) =>
              assert((rep \ "msg_type").extract[String] == "execute_reply")

              val content: JValue = rep \ "content"

              _state = Idle()

              promise.success(content)
              loop()
            case None =>
              _state = Error()
              promise.failure(new Exception("session has been terminated"))
          }

        case (_, ShutdownRequest(promise)) =>
          require(state == Idle() || state == Error())

          _state = ShuttingDown()

          try {
            sendRequest(Map("msg_type" -> "shutdown_request", "content" -> ())) match {
              case Some(rep) =>
                warn(f"process failed to shut down while returning $rep")
              case None =>
            }

            // Ignore IO errors, such as if the stream is already closed.
            try {
              process.getInputStream.close()
              process.getOutputStream.close()
            } catch {
              case _: IOException =>
            }

            try {
              process.destroy()
            } finally {
              _state = Dead()
              promise.success(())
            }
          }
      }
    }
  }

  thread.start()
}
