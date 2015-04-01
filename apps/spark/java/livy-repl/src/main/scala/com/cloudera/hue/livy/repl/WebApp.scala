package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.sessions._
import com.fasterxml.jackson.core.JsonParseException
import org.json4s.{DefaultFormats, MappingException}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import _root_.scala.concurrent.{Future, ExecutionContext}

object WebApp extends Logging

class WebApp(session: Session) extends ScalatraServlet with FutureSupport with JacksonJsonSupport {

  override protected implicit def executor: ExecutionContext = ExecutionContext.global
  override protected implicit val jsonFormats = DefaultFormats

  before() {
    contentType = formats("json")

    session.state match {
      case ShuttingDown() => halt(500, "Shutting down")
      case _ => {}
    }
  }

  get("/") {
    val state = session.state match {
      case NotStarted() => "not_started"
      case Starting() => "starting"
      case Idle() => "idle"
      case Busy() => "busy"
      case Error() => "error"
      case ShuttingDown() => "shutting_down"
      case Dead() => "dead"
    }
    Map("state" -> state)
  }

  post("/execute") {
    val req = parsedBody.extract[ExecuteRequest]
    val rep = session.execute(req.code)
    new AsyncResult { val is = rep }
  }

  get("/history") {
    session.history()
  }

  get("/history/:statementId") {
    val statementId = params("statementId").toInt

    session.history(statementId) match {
      case Some(statement) => statement
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

