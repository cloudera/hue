package com.cloudera.hue.livy.server.sessions

import com.cloudera.hue.livy.ExecuteResponse

import scala.concurrent.Future

trait Session {
  def id: String

  def lastActivity: Long

  def state: State

  def executeStatement(statement: String): Future[ExecuteResponse]

  def statement(statementId: Int): Future[ExecuteResponse]

  def statements(): Future[List[ExecuteResponse]]

  def statements(fromIndex: Integer, toIndex: Integer): Future[List[ExecuteResponse]]

  def interrupt(): Future[Unit]

  def stop(): Future[Unit]
}

sealed trait State
case class Starting() extends State
case class Idle() extends State
case class Busy() extends State
case class Dead() extends State

class SessionFailedtoStart(msg: String) extends Exception(msg) {}
