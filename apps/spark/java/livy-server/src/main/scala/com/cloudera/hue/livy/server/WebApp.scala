package com.cloudera.hue.livy.server

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.server.sessions.{SessionFailedToStart, Session}
import com.fasterxml.jackson.core.JsonParseException
import org.json4s.{DefaultFormats, Formats, MappingException}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import scala.concurrent._
import scala.concurrent.duration._

object WebApp extends Logging {
  case class CreateSessionRequest(lang: String)
}

class WebApp(sessionManager: SessionManager)
  extends ScalatraServlet
  with FutureSupport
  with MethodOverride
  with JacksonJsonSupport
  with UrlGeneratorSupport {

  import WebApp._

  override protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  override protected implicit def jsonFormats: Formats = DefaultFormats

  before() {
    contentType = formats("json")
  }

  get("/sessions") {
    sessionManager.getSessionIds
  }

  val getSession = get("/sessions/:sessionId") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) => formatSession(session)
      case None => NotFound("Session not found")
    }
  }

  post("/sessions") {
    val createSessionRequest = parsedBody.extract[CreateSessionRequest]

    val sessionFuture = createSessionRequest.lang match {
      case "scala" => sessionManager.createSession(createSessionRequest.lang)
      case "python" => sessionManager.createSession(createSessionRequest.lang)
      case lang => halt(400, "unsupported language: " + lang)
    }

    val rep = sessionFuture.map {
      case session =>
        Created(formatSession(session),
          headers = Map("Location" -> url(getSession, "sessionId" -> session.id.toString)))
    }

    new AsyncResult { val is = rep }
  }

  post("/sessions/:sessionId/stop") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        val future = session.stop()

        new AsyncResult() { val is = for { _ <- future } yield NoContent }
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
        new AsyncResult() { val is = for { _ <- future } yield NoContent }
      case None => NotFound("Session not found")
    }
  }

  delete("/sessions/:sessionId") {
    val future = for {
      _ <- sessionManager.delete(params("sessionId"))
    } yield Accepted()

    new AsyncResult() { val is = for { _ <- future } yield NoContent }
  }

  get("/sessions/:sessionId/statements") {
    sessionManager.get(params("sessionId")) match {
      case Some(session: Session) => session.statements().map(formatStatement)
      case None => NotFound("Session not found")
    }
  }

  val getStatement = get("/sessions/:sessionId/statements/:statementId") {
    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        session.statement(params("statementId").toInt) match {
          case Some(statement) => formatStatement(statement)
          case None => NotFound("Statement not found")
        }
      case None => NotFound("Session not found")
    }
  }

  post("/sessions/:sessionId/statements") {
    val req = parsedBody.extract[ExecuteRequest]

    sessionManager.get(params("sessionId")) match {
      case Some(session) =>
        val statement = session.executeStatement(req)

        Created(formatStatement(statement),
          headers = Map(
            "Location" -> url(getStatement,
              "sessionId" -> session.id.toString,
              "statementId" -> statement.id.toString)))
      case None => NotFound("Session not found")
    }
  }

  error {
    case e: JsonParseException => BadRequest(e.getMessage)
    case e: MappingException => BadRequest(e.getMessage)
    case e: SessionFailedToStart => InternalServerError(e.getMessage)
    case e: dispatch.StatusCode => ActionResult(ResponseStatus(e.code), e.getMessage, Map.empty)
    case e =>
      WebApp.error("internal error", e)
      InternalServerError(e.toString)
  }

  private def formatSession(session: Session) = {
    Map(
      "id" -> session.id,
      "state" -> session.state.getClass.getSimpleName.toLowerCase
    )
  }

  private def formatStatement(statement: Statement) = {
    // Take a couple milliseconds to see if the statement has finished.
    val output = try {
      Await.result(statement.output, 100 milliseconds)
    } catch {
      case _: TimeoutException => null
    }

    Map(
      "id" -> statement.id,
      "state" -> statement.state.getClass.getSimpleName.toLowerCase,
      "output" -> output
    )
  }
}
