package com.cloudera.hue.livy.server

import com.fasterxml.jackson.core.JsonParseException
import org.json4s.{DefaultFormats, Formats, MappingException}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import scala.concurrent.duration.Duration
import scala.concurrent.{Await, ExecutionContext, ExecutionContextExecutor}

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
      case session => Map("id" -> session.id, "state" -> session.state)
    }

    // FIXME: this is silently eating exceptions.
    //new AsyncResult { val is = rep }
    Await.result(rep, Duration.Inf)
  }

  val getStatements = get("/sessions/:sessionId/statements") {
    sessionManager.get(params("sessionId")) match {
      case Some(session: Session) =>
        val statements = session.statements()

        // FIXME: this is silently eating exceptions.
        //new AsyncResult() { val is = statements }
        Await.result(statements, Duration.Inf)
      case None => NotFound("Session not found")
    }
  }

  val getSession = get("/sessions/:sessionId") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) => Map("id" -> session.id, "state" -> session.state)
      case None => NotFound("Session not found")
    }
  }

  delete("/sessions/:sessionId") {
    val future = sessionManager.close(params("sessionId"))

    // FIXME: this is silently eating exceptions.
    //new AsyncResult() { val is = for { _ <- future } yield NoContent }
    Await.result(future, Duration.Inf)
  }

  post("/sessions/:sessionId/statements") {
    val req = parsedBody.extract[ExecuteStatementRequest]

    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        val statement = session.executeStatement(req.statement)

        // FIXME: this is silently eating exceptions.
        //new AsyncResult() { val is = statement }
        Await.result(statement, Duration.Inf)
      case None => NotFound("Session not found")
    }
  }

  val getStatement = get("/sessions/:sessionId/statements/:statementId") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        val statement = session.statement(params("statementId").toInt)

        // FIXME: this is silently eating exceptions.
        //new AsyncResult() { val is = statement }
        Await.result(statement, Duration.Inf)
      case None => NotFound("Session not found")
    }
  }

  error {
    case e: JsonParseException => halt(400, e.getMessage)
    case e: MappingException => halt(400, e.getMessage)
    case e: SessionFailedtoStart => halt(500, e.getMessage)
    case t => throw t
  }
}
