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

import com.cloudera.hue.livy.repl.process.ProcessInterpreter
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{JValue, _}

import scala.annotation.tailrec

private object SparkRInterpreter {
  val LIVY_END_MARKER = "# ----LIVY_END_OF_COMMAND----"
  val EXPECTED_OUTPUT = f"\n> $LIVY_END_MARKER"
}

private class SparkRInterpreter(process: Process)
  extends ProcessInterpreter(process)
{
  import SparkRInterpreter._

  implicit val formats = DefaultFormats

  private var executionCount = 0

  final override protected def waitUntilReady(): Unit = {
    readTo("\n> ")
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
        Some(parse(write(Map(
          "status" -> "ok",
          "execution_count" -> (executionCount - 1),
          "data" -> Map(
            "text/plain" -> output
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
        (true, result.substring(0, result.length - marker.length).stripPrefix("\n"))
      } else {
        readTo(marker, output)
      }
    }
  }
}
