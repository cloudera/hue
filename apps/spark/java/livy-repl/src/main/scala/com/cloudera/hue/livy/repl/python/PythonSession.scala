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

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.repl.{Interpreter, Session, Statement}
import com.cloudera.hue.livy.sessions._
import org.json4s.JValue

import scala.concurrent._

object PythonSession {
  def create(): Session = {
    new PythonSession(PythonInterpreter.create())
  }
}

private class PythonSession(interpreter: Interpreter) extends Session with Logging {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  private var _history = IndexedSeq[Statement]()

  override def kind = PySpark()

  override def state = interpreter.state

  override def history: IndexedSeq[Statement] = _history

  override def execute(code: String): Statement = synchronized {
    val result = interpreter.execute(code)
    val statement = Statement(_history.length, result)
    _history :+= statement
    statement
  }

  override def close(): Unit = interpreter.close()
}

private sealed trait Request
private case class ExecuteRequest(code: String, promise: Promise[JValue]) extends Request
private case class ShutdownRequest(promise: Promise[Unit]) extends Request

case class ExecuteResponse(content: JValue)
