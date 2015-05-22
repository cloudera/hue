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

package com.cloudera.hue.livy.repl

import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.sessions._
import com.fasterxml.jackson.core.JsonParseException
import org.json4s.{DefaultFormats, JsonDSL, MappingException, _}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import _root_.scala.concurrent.duration.Duration
import _root_.scala.concurrent.{Await, ExecutionContext, Future, TimeoutException}

object WebApp extends Logging

class WebApp(session: Session) extends ScalatraServlet with FutureSupport with JacksonJsonSupport {

  override protected implicit def executor: ExecutionContext = ExecutionContext.global
  override protected implicit def jsonFormats: Formats = DefaultFormats ++ Serializers.Formats

  before() {
    contentType = formats("json")

    session.state match {
      case ShuttingDown() => halt(500, "Shutting down")
      case _ => {}
    }
  }

  get("/") {
    Serializers.serializeSession(session)
  }

  post("/execute") {
    val req = parsedBody.extract[ExecuteRequest]
    Serializers.serializeStatement(session.execute(req.code))
  }

  get("/history") {
    val from = params.get("from").map(_.toInt)
    val size = params.get("size").map(_.toInt)

    Serializers.serializeHistory(session.history, from, size)
  }

  get("/history/:statementId") {
    val statementId = params("statementId").toInt

    session.history.lift(statementId) match {
      case Some(statement) => Serializers.serializeStatement(statement)
      case None => NotFound("Statement not found")
    }
  }

  delete("/") {
    session.close()
    Future {
      Thread.sleep(1000)
      System.exit(0)
    }
  }

  error {
    case e: JsonParseException => BadRequest(e.getMessage)
    case e: MappingException => BadRequest(e.getMessage)
    case e =>
      WebApp.error("internal error", e)
      InternalServerError(e.toString)
  }
}

private object Serializers {
  import JsonDSL._

  def Formats: List[CustomSerializer[_]] = List(StatementSerializer)

  def serializeSession(session: Session): JValue = {
    val state = session.state match {
      case NotStarted() => "not_started"
      case Starting() => "starting"
      case Idle() => "idle"
      case Busy() => "busy"
      case Running() => "running"
      case Error() => "error"
      case ShuttingDown() => "shutting_down"
      case Dead() => "dead"
      case Success() => "success"
    }
    Map("state" -> state)
  }

  def serializeHistory(history: IndexedSeq[Statement],
                       fromOpt: Option[Int],
                       sizeOpt: Option[Int]): JValue = {
    val size = sizeOpt.getOrElse(100)
    var from = fromOpt.getOrElse(-1)
    if (from < 0) {
      from = math.max(0, history.length - size)
    }
    val until = from + size

    ("from", from) ~
      ("total", history.length) ~
      ("statements", history.view(from, until)
        .map(serializeStatement(_, Duration(0, TimeUnit.SECONDS))))
  }

  def serializeStatement(statement: Statement,
                         duration: Duration = Duration(10, TimeUnit.SECONDS)): JValue = {
    val result = try {
      Await.result(statement.result, duration)
    } catch {
      case _: TimeoutException => null
    }

    ("id", statement.id) ~ ("result", result)
  }

  case object SessionSerializer extends CustomSerializer[Session](
    implicit formats => ( {
      // We don't support deserialization.
      PartialFunction.empty
    }, {
      case session: Session => serializeSession(session)
    }
      )
  )

  case object StatementSerializer extends CustomSerializer[Statement](
    implicit formats => ( {
      // We don't support deserialization.
      PartialFunction.empty
    }, {
      case statement: Statement => serializeStatement(statement)
    }
      )
  )
}
