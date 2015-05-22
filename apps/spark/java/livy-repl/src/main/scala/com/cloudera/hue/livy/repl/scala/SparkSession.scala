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

package com.cloudera.hue.livy.repl.scala

import com.cloudera.hue.livy.repl.{Statement, Session}
import com.cloudera.hue.livy.repl.scala.interpreter._
import com.cloudera.hue.livy.sessions._
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{JValue, _}

import scala.collection.mutable
import scala.concurrent.{ExecutionContext, Future}

object SparkSession {
  def create(): Session = new SparkSession()
}

private class SparkSession extends Session {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  implicit val formats = DefaultFormats

  private var _history = IndexedSeq[Statement]()
  private val interpreter = new Interpreter()
  interpreter.start()

  override def kind: Kind = Spark()

  override def state: State = interpreter.state match {
    case Interpreter.NotStarted() => NotStarted()
    case Interpreter.Starting() => Starting()
    case Interpreter.Idle() => Idle()
    case Interpreter.Busy() => Busy()
    case Interpreter.ShuttingDown() => ShuttingDown()
    case Interpreter.ShutDown() => Dead()
  }

  override def history: IndexedSeq[Statement] = _history

  override def execute(code: String): Statement = synchronized {
    val result = Future {
      val content = interpreter.execute(code) match {
        case ExecuteComplete(executeCount, output) =>
          Map(
            "status" -> "ok",
            "execution_count" -> executeCount,
            "data" -> Map(
              "text/plain" -> output
            )
          )
        case ExecuteIncomplete(executeCount, output) =>
          Map(
            "status" -> "error",
            "execution_count" -> executeCount,
            "ename" -> "Error",
            "evalue" -> output
          )
        case ExecuteError(executeCount, output) =>
          Map(
            "status" -> "error",
            "execution_count" -> executeCount,
            "ename" -> "Error",
            "evalue" -> output
          )
      }

      parse(write(content))
    }

    val statement = Statement(_history.length, result)
    _history :+= statement
    statement
  }

  override def close(): Unit = {
    interpreter.shutdown()
  }
}
