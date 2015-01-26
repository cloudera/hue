package com.cloudera.hue.livy.server

import scala.concurrent.{ExecutionContext, ExecutionContextExecutor, Future}
import scala.util.{Failure, Success}

class Statement(val id: Int, val input: String, val output: Future[List[String]]) {
  sealed trait State
  case class Running() extends State
  case class Available() extends State
  case class Error() extends State

  protected implicit def executor: ExecutionContextExecutor = ExecutionContext.global

  private[this] var _state: State = Running()

  def state = _state

  output.onComplete {
    case Success(_) => _state = Available()
    case Failure(_) => _state = Error()
  }
}
