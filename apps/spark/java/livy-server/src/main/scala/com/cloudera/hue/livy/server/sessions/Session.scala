package com.cloudera.hue.livy.server.sessions

import java.net.URL
import java.util.concurrent.TimeoutException

import com.cloudera.hue.livy.Utils
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.server.sessions.Statement

import scala.concurrent._
import scala.concurrent.duration.Duration

object Session {
  sealed trait State

  case class NotStarted() extends State {
    override def toString = "not_started"
  }

  case class Starting() extends State {
    override def toString = "starting"
  }

  case class Idle() extends State {
    override def toString = "idle"
  }

  case class Busy() extends State {
    override def toString = "busy"
  }

  case class Error() extends State {
    override def toString = "error"
  }

  case class Dead() extends State {
    override def toString = "dead"
  }

  sealed trait Kind

  case class Spark() extends Kind {
    override def toString = "spark"
  }

  case class PySpark() extends Kind {
    override def toString = "pyspark"
  }

  class SessionFailedToStart(msg: String) extends Exception(msg)

  class StatementNotFound extends Exception
}

trait Session {
  import Session._

  def id: String

  def kind: Kind

  def proxyUser: Option[String]

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

  @throws(classOf[TimeoutException])
  @throws(classOf[InterruptedException])
  final def waitForStateChange(oldState: State, atMost: Duration) = {
    Utils.waitUntil({ () => state != oldState }, atMost)
  }
}

