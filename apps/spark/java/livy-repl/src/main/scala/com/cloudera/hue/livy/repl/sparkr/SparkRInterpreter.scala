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

import java.nio.file.Files
import java.util.concurrent.locks.ReentrantLock

import com.cloudera.hue.livy.repl.process.ProcessInterpreter
import org.apache.commons.codec.binary.Base64
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{JValue, _}

import scala.annotation.tailrec
import scala.io.Source

private object SparkRInterpreter {
  val LIVY_END_MARKER = "----LIVY_END_OF_COMMAND----"
  val PRINT_MARKER = f"""print("$LIVY_END_MARKER")"""
  val EXPECTED_OUTPUT = f"""\n$PRINT_MARKER\n[1] "$LIVY_END_MARKER""""
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
    try {
      commands.split("\n").map { case command =>
        executionCount += 1

        val content = sendSingleExecuteRequest(command)
        Some(parse(write(
          Map(
            "status" -> "ok",
            "execution_count" -> (executionCount - 1),
            "data" -> content
          ))))
      }.last
    } catch {
      case e: Error =>
        Some(parse(write(
        Map(
          "status" -> "error",
          "ename" -> "Error",
          "evalue" -> e.output,
          "data" -> Map(
            "text/plain" -> takeErrorLines()
          )
        ))))
      case e: Exited =>
        None
    }
  }

  private val plotRegex = (
    "%(" +
      "(?:" +
        "(?:stripchart)|" +
        "(?:hist)|" +
        "(?:boxplot)|" +
        "(?:plot)|" +
        "(?:qqnorm)|" +
        "(?:qqline)" +
      ")" +
      "\\([^;)]*\\)" +
    ")"
  ).r

  private def sendSingleExecuteRequest(command: String) = {
    if (command.startsWith("%")) {
      command match {
        case plotRegex(plotCommand) =>
          val tempFile = Files.createTempFile("", ".png")
          try {
            val tempFileString = tempFile.toAbsolutePath.toString

            val output = Seq(
              f"""png("$tempFileString")""",
              f"""$plotCommand""",
              "dev.off()"
            ).map { case code =>
              sendRequest(code)
            }.mkString("\n")

            // Encode the image as a base64 image.
            Map(
              "image/png" -> Base64.encodeBase64String(Files.readAllBytes(tempFile))
            )
          } finally {
            Files.delete(tempFile)
          }
        case _ =>
          throw new Error(f"unknown magic command `$command`")
      }
    } else {
      Map(
        "text/plain" -> (sendRequest(command) + takeErrorLines())
      )
    }
  }

  private def sendRequest(code: String): String = {
    stdin.println(code)
    stdin.flush()

    // Skip the line we just entered in.
    if (!code.isEmpty) {
      readTo(code)
    }

    stdin.println(PRINT_MARKER)
    stdin.flush()

    readTo(EXPECTED_OUTPUT)
  }

  override protected def sendShutdownRequest() = {
    stdin.println("q()")
    stdin.flush()

    while (stdout.readLine() != null) {}
  }

  @tailrec
  private def readTo(marker: String, output: StringBuilder = StringBuilder.newBuilder): String = {
    var char = readChar(output)

    // Remove any ANSI color codes which match the pattern "\u001b\\[[0-9;]*[mG]".
    // It would be easier to do this with a regex, but unfortunately I don't see an easy way to do
    // without copying the StringBuilder into a string for each character.
    if (char == '\u001b') {
      if (readChar(output) == '[') {
        char = readDigits(output)

        if (char == 'm' || char == 'G') {
          output.delete(output.lastIndexOf('\u001b'), output.length)
        }
      }
    }

    if (output.endsWith(marker)) {
      val result = output.toString()
      result.substring(0, result.length - marker.length)
        .stripPrefix("\n")
        .stripSuffix("\n")
    } else {
      readTo(marker, output)
    }
  }

  private def readChar(output: StringBuilder): Char = {
    val byte = stdout.read()
    if (byte == -1) {
      throw new Exited(output.toString())
    } else {
      val char = byte.toChar
      output.append(char)
      char
    }
  }

  @tailrec
  private def readDigits(output: StringBuilder): Char = {
    val byte = stdout.read()
    if (byte == -1) {
      throw new Exited(output.toString())
    }

    val char = byte.toChar

    if (('0' to '9').contains(char)) {
      output.append(char)
      readDigits(output)
    } else {
      char
    }
  }

  private class Exited(val output: String) extends Exception {}
  private class Error(val output: String) extends Exception {}

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
