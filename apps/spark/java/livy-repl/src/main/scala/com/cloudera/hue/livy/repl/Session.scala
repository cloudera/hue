package com.cloudera.hue.livy.repl

import org.json4s.JValue

import _root_.scala.annotation.tailrec
import _root_.scala.concurrent.Future

object Session {
  sealed trait State
  case class NotStarted() extends State
  case class Starting() extends State
  case class Idle() extends State
  case class Busy() extends State
  case class Error() extends State
  case class ShuttingDown() extends State
  case class ShutDown() extends State
}

trait Session {
  import Session._

  def state: State

  def execute(code: String): Future[JValue]

  def history(): Seq[JValue]

  def history(id: Int): Option[JValue]

  def close(): Future[Unit]

  @tailrec
  final def waitForStateChange(oldState: State): Unit = {
    if (state == oldState) {
      Thread.sleep(1000)
      waitForStateChange(oldState)
    }
  }
}
