package com.cloudera.hue.livy.repl

import _root_.akka.util.Timeout
import com.cloudera.hue.livy.{ExecuteRequest, Logging}
import com.fasterxml.jackson.core.JsonParseException
import org.json4s.{DefaultFormats, Formats, MappingException}
import org.scalatra._
import org.scalatra.json.JacksonJsonSupport

import _root_.scala.concurrent.{ExecutionContextExecutor, Future, ExecutionContext}

object WebApp extends Logging {}

class WebApp(session: Session) extends ScalatraServlet with FutureSupport with JacksonJsonSupport {

  override protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  override protected implicit val jsonFormats = DefaultFormats

  protected implicit def defaultTimeout: Timeout = Timeout(10)

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

  get("/statements") {
    session.statements
  }

  post("/statements") {
    val req = parsedBody.extract[ExecuteRequest]
    val statement: String = req.statement
    val rep = session.execute(statement)
    new AsyncResult { val is = rep }
  }

  get("/statements/:statementId") {
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
