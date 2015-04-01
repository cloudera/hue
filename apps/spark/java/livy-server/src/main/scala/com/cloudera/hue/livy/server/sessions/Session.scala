package com.cloudera.hue.livy.server.sessions

import java.net.URL
import java.util.concurrent.TimeoutException

import com.cloudera.hue.livy.Utils
import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.sessions.{Kind, State}

import scala.concurrent._
import scala.concurrent.duration.Duration

object Session {
  class SessionFailedToStart(msg: String) extends Exception(msg)

  class StatementNotFound extends Exception
}

trait Session {
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

