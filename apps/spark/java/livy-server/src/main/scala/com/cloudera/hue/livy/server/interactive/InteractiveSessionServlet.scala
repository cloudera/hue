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

import java.net.URL
import java.util.concurrent.TimeUnit

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.server.{SessionManager, SessionServlet}
import com.cloudera.hue.livy.server.interactive.InteractiveSession.SessionFailedToStart
import com.cloudera.hue.livy.sessions._
import com.fasterxml.jackson.core.JsonParseException
import org.json4s.JsonAST.JString
import org.json4s.JsonDSL._
import org.json4s._
import org.scalatra._

import scala.concurrent._
import scala.concurrent.duration._

object InteractiveSessionServlet extends Logging

class InteractiveSessionServlet(sessionManager: SessionManager[InteractiveSession])
  extends SessionServlet(sessionManager)
{
  override protected implicit def jsonFormats: Formats = DefaultFormats ++ Serializers.Formats

  override protected def serializeSession(session: InteractiveSession) = Serializers.serializeSession(session)

  post("/:sessionId/callback") {
    val sessionId = params("sessionId").toInt
    val callback = parsedBody.extract[CallbackRequest]

    sessionManager.get(sessionId) match {
      case Some(session) =>
        if (session.state == Starting()) {
          session.url = new URL(callback.url)
          Accepted()
        } else {
          BadRequest("Session is in wrong state")
        }
      case None => NotFound("Session not found")
    }
  }

  post("/:sessionId/stop") {
    val sessionId = params("sessionId").toInt
    sessionManager.get(sessionId) match {
      case Some(session) =>
        val future = session.stop()

        new AsyncResult() { val is = for { _ <- future } yield NoContent() }
      case None => NotFound("Session not found")
    }
  }

  post("/:sessionId/interrupt") {
    val sessionId = params("sessionId").toInt
    sessionManager.get(sessionId) match {
      case Some(session) =>
        val future = for {
          _ <- session.interrupt()
        } yield Ok(Map("msg" -> "interrupted"))

        // FIXME: this is silently eating exceptions.
        new AsyncResult() { val is = future }
      case None => NotFound("Session not found")
    }
  }

  get("/:sessionId/statements") {
    val sessionId = params("sessionId").toInt

    sessionManager.get(sessionId) match {
      case None => NotFound("Session not found")
      case Some(session: InteractiveSession) =>
        val from = params.get("from").map(_.toInt).getOrElse(0)
        val size = params.get("size").map(_.toInt).getOrElse(session.statements.length)

        Map(
          "total_statements" -> session.statements.length,
          "statements" -> session.statements.view(from, from + size)
        )
    }
  }

  val getStatement = get("/:sessionId/statements/:statementId") {
    val sessionId = params("sessionId").toInt
    val statementId = params("statementId").toInt

    val from = params.get("from").map(_.toInt)
    val size = params.get("size").map(_.toInt)

    sessionManager.get(sessionId) match {
      case None => NotFound("Session not found")
      case Some(session) =>
        session.statements.lift(statementId) match {
          case None => NotFound("Statement not found")
          case Some(statement) =>
            Serializers.serializeStatement(statement, from, size)
        }
    }
  }

  post("/:sessionId/statements") {
    val sessionId = params("sessionId").toInt
    val req = parsedBody.extract[ExecuteRequest]

    sessionManager.get(sessionId) match {
      case Some(session) =>
        val statement = session.executeStatement(req)

        Created(statement,
          headers = Map(
            "Location" -> url(getStatement,
              "sessionId" -> session.id.toString,
              "statementId" -> statement.id.toString)))
      case None => NotFound("Session not found")
    }
  }
}

private case class CallbackRequest(url: String)

private object Serializers {
  import JsonDSL._

  def SessionFormats: List[CustomSerializer[_]] = List(SessionSerializer, SessionKindSerializer, SessionStateSerializer)
  def StatementFormats: List[CustomSerializer[_]] = List(StatementSerializer, StatementStateSerializer)
  def Formats: List[CustomSerializer[_]] = SessionFormats ++ StatementFormats

  private def serializeSessionState(state: State) = JString(state.toString)

  private def serializeSessionKind(kind: Kind) = JString(kind.toString)

  private def serializeStatementState(state: Statement.State) = JString(state.toString)

  def serializeSession(session: InteractiveSession): JValue = {
    ("id", session.id) ~
      ("state", serializeSessionState(session.state)) ~
      ("kind", serializeSessionKind(session.kind)) ~
      ("proxyUser", session.proxyUser) ~
      ("log", getLogs(session, None, Some(10))._3)
  }
  
  def getLogs(session: InteractiveSession, fromOpt: Option[Int], sizeOpt: Option[Int]) = {
    val lines = session.logLines()

    val size = sizeOpt.getOrElse(100)
    var from = fromOpt.getOrElse(-1)
    if (from < 0) {
      from = math.max(0, lines.length - size)
    }
    val until = from + size

    (from, lines.length, lines.view(from, until))
  }

  def serializeStatement(statement: Statement, from: Option[Int], size: Option[Int]): JValue = {
    // Take a couple milliseconds to see if the statement has finished.
    val output = try {
      Await.result(statement.output(), Duration(100, TimeUnit.MILLISECONDS))
    } catch {
      case _: TimeoutException => null
    }

    ("id" -> statement.id) ~
      ("state" -> serializeStatementState(statement.state)) ~
      ("output" -> output)
  }

  case object SessionSerializer extends CustomSerializer[InteractiveSession](implicit formats => ( {
    // We don't support deserialization.
    PartialFunction.empty
  }, {
    case session: InteractiveSession =>
      serializeSession(session)
  }
    )
  )

  case object SessionStateSerializer extends CustomSerializer[State](implicit formats => ( {
    // We don't support deserialization.
    PartialFunction.empty
  }, {
    case state: State => JString(state.toString)
  }
    )
  )

  case object StatementSerializer extends CustomSerializer[Statement](implicit formats => ( {
    // We don't support deserialization.
    PartialFunction.empty
  }, {
    case statement: Statement =>
      serializeStatement(statement, None, None)
  }))

  case object StatementStateSerializer extends CustomSerializer[Statement.State](implicit formats => ( {
    // We don't support deserialization.
    PartialFunction.empty
  }, {
    case state: Statement.State => JString(state.toString)
  }
    )
  )
}
