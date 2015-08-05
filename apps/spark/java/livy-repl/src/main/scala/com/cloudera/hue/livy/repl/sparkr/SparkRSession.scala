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

import com.cloudera.hue.livy.repl.{Session, Statement}
import com.cloudera.hue.livy.sessions._

import scala.collection.JavaConversions._

object SparkRSession {
  def create(): Session = {
    val sparkrExec = sys.env.getOrElse("SPARKR_DRIVER_R", "sparkR")

    val builder = new ProcessBuilder(Seq(
      sparkrExec
    ))

    val env = builder.environment()
    env.put("SPARK_HOME", sys.env.getOrElse("SPARK_HOME", "."))
    env.put("SPARKR_DRIVER_R", createFakeShell().toString)

    builder.redirectError(Redirect.PIPE)

    val process = builder.start()

    val interpreter = new SparkRInterpreter(process)

    new SparkRSession(interpreter)
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

private class SparkRSession(interpreter: SparkRInterpreter) extends Session {
  private var _history = IndexedSeq[Statement]()

  override def kind: Kind = SparkR()

  override def state: State = interpreter.state

  override def execute(code: String): Statement = {
    val result = interpreter.execute(code)
    val statement = Statement(_history.length, result)
    _history :+= statement
    statement
  }

  override def close(): Unit = interpreter.close()

  override def history: IndexedSeq[Statement] = _history
}


