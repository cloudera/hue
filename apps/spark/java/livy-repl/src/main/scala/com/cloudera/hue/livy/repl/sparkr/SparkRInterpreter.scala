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

import java.io.{File, FileOutputStream}
import java.lang.ProcessBuilder.Redirect
import java.nio.file.Files

import com.cloudera.hue.livy.repl
import com.cloudera.hue.livy.repl.Interpreter
import com.cloudera.hue.livy.repl.process.ProcessInterpreter
import org.apache.commons.codec.binary.Base64
import org.json4s.JsonDSL._
import org.json4s._

import scala.annotation.tailrec
import scala.collection.JavaConversions._

object SparkRInterpreter {
  private val LIVY_END_MARKER = "----LIVY_END_OF_COMMAND----"
  private val PRINT_MARKER = f"""print("$LIVY_END_MARKER")"""
  private val EXPECTED_OUTPUT = f"""[1] "$LIVY_END_MARKER""""

  private val PLOT_REGEX = (
    "(" +
      "(?:bagplot)|" +
      "(?:barplot)|" +
      "(?:boxplot)|" +
      "(?:dotchart)|" +
      "(?:hist)|" +
      "(?:lines)|" +
      "(?:pie)|" +
      "(?:pie3D)|" +
      "(?:plot)|" +
      "(?:qqline)|" +
      "(?:qqnorm)|" +
      "(?:scatterplot)|" +
      "(?:scatterplot3d)|" +
      "(?:scatterplot\\.matrix)|" +
      "(?:splom)|" +
      "(?:stripchart)|" +
      "(?:vioplot)" +
    ")"
    ).r.unanchored

  def apply(): SparkRInterpreter = {
    val executable = sparkRExecutable
      .getOrElse(throw new Exception(f"Cannot find sparkR executable"))

    val builder = new ProcessBuilder(Seq(executable.getAbsolutePath))

    val env = builder.environment()
    env.put("SPARK_HOME", sys.env.getOrElse("SPARK_HOME", "."))
    env.put("SPARKR_DRIVER_R", createFakeShell().toString)

    builder.redirectError(Redirect.PIPE)

    val process = builder.start()

    new SparkRInterpreter(process)
  }

  def sparkRExecutable: Option[File] = {
    val executable = sys.env.getOrElse("SPARKR_DRIVER_R", "sparkR")
    val executableFile = new File(executable)

    if (executableFile.exists) {
      Some(executableFile)
    } else {
      // see if sparkR is on the path.
      val path: Option[String] = sys.env.get("PATH")
      assume(path.isDefined, "PATH is not defined?")

      path.get
        .split(File.pathSeparator)
        .map(new File(_, executable))
        .find(_.exists)
    }
  }

  private def createFakeShell(): File = {
    val source = getClass.getClassLoader.getResourceAsStream("fake_R.sh")

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

    file.setExecutable(true)

    file
  }
}

class SparkRInterpreter(process: Process)
  extends ProcessInterpreter(process)
{
  import SparkRInterpreter._

  implicit val formats = DefaultFormats

  private[this] var executionCount = 0

  override def kind = "sparkR"

  final override protected def waitUntilReady(): Unit = {
    // Set the option to catch and ignore errors instead of halting.
    sendExecuteRequest("options(error = dump.frames)")
    executionCount = 0
  }

  override protected def sendExecuteRequest(command: String): Interpreter.ExecuteResponse = {
    var code = command

    // Create a image file if this command is trying to plot.
    val tempFile = PLOT_REGEX.findFirstIn(code).map { case _ =>
      val tempFile = Files.createTempFile("", ".png")
      val tempFileString = tempFile.toAbsolutePath

      code = f"""png("$tempFileString")\n$code\ndev.off()"""

      tempFile
    }

    try {
      var content: JObject = repl.TEXT_PLAIN -> (sendRequest(code) + takeErrorLines())

      // If we rendered anything, pass along the last image.
      tempFile.foreach { case file =>
        val bytes = Files.readAllBytes(file)
        if (bytes.nonEmpty) {
          val image = Base64.encodeBase64String(bytes)
          content = content ~ (repl.IMAGE_PNG -> image)
        }
      }

      Interpreter.ExecuteSuccess(content)
    } catch {
      case e: Error =>
        val message = Seq(e.output, takeErrorLines()).mkString("\n")
        Interpreter.ExecuteError("Error", message)
      case e: Exited =>
        Interpreter.ExecuteAborted(takeErrorLines())
    } finally {
      tempFile.foreach(Files.delete)
    }

  }

  private def sendRequest(code: String): String = {
    stdin.println(code)
    stdin.flush()

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
}
