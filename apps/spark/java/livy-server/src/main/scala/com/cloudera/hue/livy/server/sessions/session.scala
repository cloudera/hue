package com.cloudera.hue.livy.server.sessions

import com.cloudera.hue.livy.ExecuteResponse
import com.cloudera.hue.livy.server.Statement

import scala.concurrent.Future

trait Session {
  def id: String

  def lastActivity: Long

  def state: State

  def executeStatement(statement: String): Statement

  def statement(statementId: Int): Option[Statement]

  def statements(): Seq[Statement]

  def statements(fromIndex: Integer, toIndex: Integer): Seq[Statement]

  def interrupt(): Future[Unit]

  def stop(): Future[Unit]
}

sealed trait State
case class Starting() extends State
case class Idle() extends State
case class Busy() extends State
case class Dead() extends State

class SessionFailedToStart(msg: String) extends Exception(msg)

class StatementNotFound extends Exception