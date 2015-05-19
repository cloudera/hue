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

package com.cloudera.hue.livy.server.interactive

import com.cloudera.hue.livy.msgs.ExecuteRequest
import org.json4s.JValue
import org.json4s.JsonAST.{JArray, JObject, JField, JString}

import scala.concurrent.{ExecutionContext, ExecutionContextExecutor, Future}
import scala.util.{Failure, Success}

object Statement {
  sealed trait State

  case class Running() extends State {
    override def toString = "running"
  }

  case class Available() extends State {
    override def toString = "available"
  }

  case class Error() extends State {
    override def toString = "error"
  }
}

class Statement(val id: Int, val request: ExecuteRequest, _output: Future[JValue]) {
  import Statement._

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private[this] var _state: State = Running()

  def state = _state

  def output(from: Option[Int] = None, size: Option[Int] = None): Future[JValue] = {
    _output.map { case output =>
      if (from.isEmpty && size.isEmpty) {
        output
      } else {
        val from_ = from.getOrElse(0)
        val size_ = size.getOrElse(100)
        val until = from_ + size_

        output \ "data" match {
          case JObject(JField("text/plain", JString(text)) :: Nil) =>
            val lines = text.split('\n').slice(from_, until)
            output.replace(
              "data" :: "text/plain" :: Nil,
              JString(lines.mkString("\n")))
          case JObject(JField("application/json", JArray(items)) :: Nil) =>
            output.replace(
              "data" :: "application/json" :: Nil,
              JArray(items.slice(from_, until)))
          case _ =>
            output
        }
      }
    }
  }

  _output.onComplete {
    case Success(_) => _state = Available()
    case Failure(_) => _state = Error()
  }
}
