package com.cloudera.hue.livy.server

import com.fasterxml.jackson.core.JsonParseException
import org.json4s.{MappingException, DefaultFormats, Formats}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import scala.concurrent.{ExecutionContext, ExecutionContextExecutor}

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

    val rep = for {
      session <- sessionFuture
    } yield redirect(url(getSession, "sessionId" -> session.id))

    new AsyncResult { val is = rep }
  }

  val getStatements = get("/sessions/:sessionId/statements") {
    sessionManager.get(params("sessionId")) match {
      case Some(session: Session) =>
        val statements = session.statements()
        new AsyncResult() { val is = statements }
      case None => NotFound("Session not found")
    }
  }

  val getSession = get("/sessions/:sessionId") {
    redirect(url(getStatements, "sessionId" -> params("sessionId")))
  }

  delete("/sessions/:sessionId") {
    new AsyncResult() {
      val is = for {
      _ <- sessionManager.close(params("sessionId"))
      } yield NoContent
    }
  }

  post("/sessions/:sessionId/statements") {
    val req = parsedBody.extract[ExecuteStatementRequest]

    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        val statement = session.executeStatement(req.statement)
        new AsyncResult() { val is = statement }
      case None => NotFound("Session not found")
    }
  }

  val getStatement = get("/sessions/:sessionId/statements/:statementId") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        val statement = session.statement(params("statementId").toInt)
        new AsyncResult() { val is = statement }
      case None => NotFound("Session not found")
    }
  }

  error {
    case e: JsonParseException => halt(400, e.getMessage)
    case e: MappingException => halt(400, e.getMessage)
    case t => throw t
  }
}
