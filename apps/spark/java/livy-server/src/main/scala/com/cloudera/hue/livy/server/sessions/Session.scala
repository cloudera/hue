package com.cloudera.hue.livy.server.sessions

import java.net.URL

import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.server.Statement

import scala.annotation.tailrec
import scala.concurrent.Future

object Session {
  sealed trait State
  case class NotStarted() extends State
  case class Starting() extends State
  case class Idle() extends State
  case class Busy() extends State
  case class Error() extends State
  case class Dead() extends State

  class SessionFailedToStart(msg: String) extends Exception(msg)

  class StatementNotFound extends Exception
}

trait Session {
  import Session._

  def id: String

  def lastActivity: Long

  def state: State

  def url: Option[URL]

  def url_=(url: URL)

  def executeStatement(content: ExecuteRequest): Statement

  def statement(statementId: Int): Option[Statement]

  def statements(): Seq[Statement]

  def statements(fromIndex: Integer, toIndex: Integer): Seq[Statement]

  def interrupt(): Future[Unit]

  def stop(): Future[Unit]

  @tailrec
  final def waitForStateChange[A](oldState: State, f: => A): A = {
    if (state == oldState) {
      Thread.sleep(1000)
      waitForStateChange(oldState, f)
    } else {
      f
    }
  }
}

