package com.cloudera.hue.livy.server

import com.cloudera.hue.livy.server.sessions.{SessionFailedToStart, Session}
import com.fasterxml.jackson.core.JsonParseException
import org.json4s.{DefaultFormats, Formats, MappingException}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import scala.concurrent.duration.Duration
import scala.concurrent.{Future, Await, ExecutionContext, ExecutionContextExecutor}

object WebApp {
  case class CreateSessionRequest(lang: String)
  case class ExecuteStatementRequest(statement: String)
}

class WebApp(sessionManager: SessionManager)
  extends ScalatraServlet
  with FutureSupport
  with MethodOverride
  with JacksonJsonSupport
  with UrlGeneratorSupport {

  import com.cloudera.hue.livy.server.WebApp._

  override protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  override protected implicit def jsonFormats: Formats = DefaultFormats

  before() {
    contentType = formats("json")
  }

  get("/sessions") {
    sessionManager.getSessionIds
  }

  post("/sessions") {
    val createSessionRequest = parsedBody.extract[CreateSessionRequest]

    val sessionFuture = createSessionRequest.lang match {
      case "scala" => sessionManager.createSparkSession()
      case lang => halt(400, "unsupported language: " + lang)
    }

    val rep = sessionFuture.map {
      case session => formatSession(session)
    }

    // FIXME: this is silently eating exceptions.
    //new AsyncResult { val is = rep }
    Await.result(rep, Duration.Inf)
  }

  get("/sessions/:sessionId") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) => formatSession(session)
      case None => NotFound("Session not found")
    }
  }

  post("/sessions/:sessionId/stop") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        val future = session.stop()

        // FIXME: this is silently eating exceptions.
        //new AsyncResult() { val is = for { _ <- future } yield NoContent }
        Await.result(future, Duration.Inf)
      case None => NotFound("Session not found")
    }
  }

  post("/sessions/:sessionId/interrupt") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        val future = for {
          _ <- session.interrupt()
        } yield Accepted()

        // FIXME: this is silently eating exceptions.
        //new AsyncResult() { val is = for { _ <- future } yield NoContent }
        Await.result(future, Duration.Inf)
      case None => NotFound("Session not found")
    }
  }

  delete("/sessions/:sessionId") {
    val future = for {
      _ <- sessionManager.delete(params("sessionId"))
    } yield Accepted()

    // FIXME: this is silently eating exceptions.
    //new AsyncResult() { val is = for { _ <- future } yield NoContent }
    Await.result(future, Duration.Inf)
  }

  get("/sessions/:sessionId/statements") {
    sessionManager.get(params("sessionId")) match {
      case Some(session: Session) => session.statements().map(formatStatement)
      case None => NotFound("Session not found")
    }
  }

  post("/sessions/:sessionId/statements") {
    val req = parsedBody.extract[ExecuteStatementRequest]

    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        Future {
          val statement: Statement = session.executeStatement(req.statement)

          // FIXME: this is silently eating exceptions.
          //new AsyncResult() { val is = statement }
          Await.result(statement.output, Duration.Inf)
        }

        Accepted()
      case None => NotFound("Session not found")
    }
  }

  get("/sessions/:sessionId/statements/:statementId") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        session.statement(params("statementId").toInt) match {
          case Some(statement) => formatStatement(statement)
          case None => NotFound("Statement not found")
        }
      case None => NotFound("Session not found")
    }
  }

  error {
    case e: JsonParseException => halt(400, e.getMessage)
    case e: MappingException => halt(400, e.getMessage)
    case e: SessionFailedToStart => halt(500, e.getMessage)
    case e: dispatch.StatusCode => halt(e.code, e.getMessage)
    case t => throw t
  }

  private def formatSession(session: Session) = {
    Map(
      "id" -> session.id,
      "state" -> session.state.getClass.getSimpleName.toLowerCase
    )
  }

  private def formatStatement(statement: Statement) = {
    Map(
      "id" -> statement.id,
      "state" -> statement.state.getClass.getSimpleName.toLowerCase,
      "output" -> statement.output
    )
  }
}
