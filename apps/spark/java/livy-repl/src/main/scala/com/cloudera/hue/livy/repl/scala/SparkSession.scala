package com.cloudera.hue.livy.repl.scala

import com.cloudera.hue.livy.repl.Session
import com.cloudera.hue.livy.repl.scala.interpreter.Interpreter
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{JValue, _}

import scala.collection.mutable
import scala.concurrent.{ExecutionContext, Future}

object SparkSession {
  def create(): Session = new SparkSession()
}

private class SparkSession extends Session {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  implicit val formats = DefaultFormats

  private var _history = new mutable.ArrayBuffer[JValue]
  private val interpreter = new Interpreter()

  override def state: Session.State = interpreter.state match {
    case Interpreter.Starting() => Session.Starting()
    case Interpreter.Idle() => Session.Idle()
    case Interpreter.Busy() => Session.Busy()
    case Interpreter.ShuttingDown() => Session.ShuttingDown()
  }

  override def history(): Seq[JValue] = _history

  override def history(id: Int): Option[JValue] = synchronized {
    if (id < _history.length) {
      Some(_history(id))
    } else {
      None
    }
  }

  override def execute(code: String): Future[JValue] = {
    interpreter.execute(code).map {
      case rep =>
        val content = parse(write(Map(
          "status" -> "ok",
          "execution_count" -> rep.executionCount,
          "data" -> Map(
            "text/plain" -> rep.data
          )
        )))

        _history += content
        content
    }
  }

  override def close(): Future[Unit] = {
    interpreter.shutdown()
  }
}
