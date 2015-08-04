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

package com.cloudera.hue.livy.repl.sparkr

import java.util.concurrent.locks.ReentrantLock

import com.cloudera.hue.livy.repl.process.ProcessInterpreter
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{JValue, _}

import scala.annotation.tailrec
import scala.io.Source

private object SparkRInterpreter {
  val LIVY_END_MARKER = "# ----LIVY_END_OF_COMMAND----"
  val EXPECTED_OUTPUT = f"> $LIVY_END_MARKER"
}

private class SparkRInterpreter(process: Process)
  extends ProcessInterpreter(process)
{
  import SparkRInterpreter._

  implicit val formats = DefaultFormats

  private[this] var executionCount = 0

  final override protected def waitUntilReady(): Unit = {
    sendExecuteRequest("")
    executionCount = 0
  }

  override protected def sendExecuteRequest(commands: String): Option[JValue] = synchronized {
    commands.split("\n").map { case code =>
      stdin.println(code)
      stdin.println(LIVY_END_MARKER)
      stdin.flush()

      executionCount += 1

      // Skip the line we just entered in.
      if (!code.isEmpty) {
        readTo(code)
      }

      readTo(EXPECTED_OUTPUT)
    }.last match {
      case (true, output) =>
        val data = (output + takeErrorLines())

        Some(parse(write(Map(
          "status" -> "ok",
          "execution_count" -> (executionCount - 1),
          "data" -> Map(
            "text/plain" -> data
          )
        ))))
      case (false, output) =>
        None
    }
  }

  override protected def sendShutdownRequest() = {
    stdin.println("q()")
    stdin.flush()

    while (stdout.readLine() != null) {}
  }

  @tailrec
  private def readTo(marker: String, output: StringBuilder = StringBuilder.newBuilder): (Boolean, String) = {
    val char = stdout.read()
    if (char == -1) {
      (false, output.toString())
    } else {
      output.append(char.toChar)
      if (output.endsWith(marker)) {
        val result = output.toString()
        (
          true,
          result.substring(0, result.length - marker.length)
            .replaceAll("\033\\[[0-9;]*[mG]", "") // Remove any ANSI color codes
            .stripPrefix("\n")
            .stripSuffix("\n"))
      } else {
        readTo(marker, output)
      }
    }
  }

  private[this] val _lock = new ReentrantLock()
  private[this] var stderrLines = Seq[String]()

  private def takeErrorLines(): String = {
    var lines: Seq[String] = null
    _lock.lock()
    try {
      lines = stderrLines
      stderrLines = Seq[String]()
    } finally {
      _lock.unlock()
    }

    lines.mkString("\n")
  }

  private[this] val stderrThread = new Thread("sparkr stderr thread") {
    override def run() = {
      val lines = Source.fromInputStream(process.getErrorStream).getLines()

      for (line <- lines) {
        _lock.lock()
        try {
          stderrLines :+= line
        } finally {
          _lock.unlock()
        }
      }
    }
  }

  stderrThread.setDaemon(true)
  stderrThread.start()
}
