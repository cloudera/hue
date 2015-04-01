package com.cloudera.hue.livy.server.sessions

import com.cloudera.hue.livy.msgs.ExecuteRequest
import org.json4s.JValue

import scala.concurrent.{ExecutionContext, ExecutionContextExecutor, Future}
import scala.util.{Failure, Success}

object Statement {
  sealed trait State

  case class Running() extends State {
    override def toString = "running"
  }

  case class Available() extends State {
    override def toString = "available"
  }

  case class Error() extends State {
    override def toString = "error"
  }
}

class Statement(val id: Int, val request: ExecuteRequest, val output: Future[JValue]) {
  import Statement._

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private[this] var _state: State = Running()

  def state = _state

  output.onComplete {
    case Success(_) => _state = Available()
    case Failure(_) => _state = Error()
  }
}
