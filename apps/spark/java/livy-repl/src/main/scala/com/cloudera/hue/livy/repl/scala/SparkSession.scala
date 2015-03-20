package com.cloudera.hue.livy.repl.scala

import com.cloudera.hue.livy.repl.Session
import com.cloudera.hue.livy.repl.scala.interpreter._
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
  interpreter.start()

  override def state: Session.State = interpreter.state match {
    case Interpreter.NotStarted() => Session.NotStarted()
    case Interpreter.Starting() => Session.Starting()
    case Interpreter.Idle() => Session.Idle()
    case Interpreter.Busy() => Session.Busy()
    case Interpreter.ShuttingDown() => Session.ShuttingDown()
    case Interpreter.ShutDown() => Session.ShutDown()
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
    Future {
      val content = interpreter.execute(code) match {
        case ExecuteComplete(executeCount, output) =>
          Map(
            "status" -> "ok",
            "execution_count" -> executeCount,
            "data" -> Map(
              "text/plain" -> output
            )
          )
        case ExecuteIncomplete(executeCount, output) =>
          Map(
            "status" -> "error",
            "execution_count" -> executeCount,
            "ename" -> "Error",
            "evalue" -> output
          )
        case ExecuteError(executeCount, output) =>
          Map(
            "status" -> "error",
            "execution_count" -> executeCount,
            "ename" -> "Error",
            "evalue" -> output
          )
      }

      val jsonContent = parse(write(content))

      _history += jsonContent

      jsonContent
    }
  }

  override def close(): Future[Unit] = {
    Future {
      interpreter.shutdown()
    }
  }
}
