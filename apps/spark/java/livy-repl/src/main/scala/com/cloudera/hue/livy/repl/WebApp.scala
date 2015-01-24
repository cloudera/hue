package com.cloudera.hue.livy.repl

import akka.util.Timeout
import com.cloudera.hue.livy.ExecuteRequest
import com.fasterxml.jackson.core.JsonParseException
import org.json4s.{MappingException, DefaultFormats, Formats}
import org.scalatra.json._
import org.scalatra.{Accepted, AsyncResult, FutureSupport, ScalatraServlet}

import scala.concurrent.{ExecutionContext, ExecutionContextExecutor, Future}

class WebApp(interpreter: SparkInterpreter) extends ScalatraServlet with FutureSupport with JacksonJsonSupport {

  override protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global
  override protected implicit val jsonFormats: Formats = DefaultFormats

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
    interpreter.statements
  }

  post("/statements") {
    val req = parsedBody.extract[ExecuteRequest]
    val statement = req.statement
    new AsyncResult { val is = interpreter.execute(statement) }
  }

  delete("/") {
    Future {
      state = ShuttingDown()
      interpreter.close()
      Thread.sleep(1000)
      System.exit(0)
    }
    Accepted()
  }

  error {
    case e: JsonParseException => halt(400, e.getMessage)
    case e: MappingException => halt(400, e.getMessage)
    case t => throw t
  }
}
