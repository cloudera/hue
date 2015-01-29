package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.Logging
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.fasterxml.jackson.core.JsonParseException
import org.json4s.{DefaultFormats, MappingException}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import _root_.scala.concurrent.{ExecutionContext, ExecutionContextExecutor, Future}

object WebApp extends Logging

class WebApp(session: Session) extends ScalatraServlet with FutureSupport with JacksonJsonSupport {

  override protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  override protected implicit val jsonFormats = DefaultFormats

  sealed trait State
  case class Starting() extends State
  case class Running() extends State
  case class ShuttingDown() extends State

  var state: State = Starting()

  before() {
    contentType = formats("json")

    state match {
      case ShuttingDown() => halt(500, "Shutting down")
      case _ => {}
    }
  }

  get("/") {
    Map("state" -> state)
  }

  post("/execute") {
    val req = parsedBody.extract[ExecuteRequest]
    val rep = session.execute(req)
    new AsyncResult { val is = rep }
  }

  get("/history") {
    session.statements
  }

  get("/history/:statementId") {
    val statementId = params("statementId").toInt

    session.statement(statementId) match {
      case Some(statement) => statement
      case None => NotFound("Statement not found")
    }
  }

  delete("/") {
    Future {
      state = ShuttingDown()
      session.close()
      Thread.sleep(1000)
      System.exit(0)
    }
    Accepted()
  }

  error {
    case e: JsonParseException => BadRequest(e.getMessage)
    case e: MappingException => BadRequest(e.getMessage)
    case e =>
      WebApp.error("internal error", e)
      InternalServerError(e.toString)
  }
}
