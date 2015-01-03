package com.cloudera.hue.livy.server

import com.cloudera.hue.livy.ExecuteResponse

import scala.concurrent.Future

trait Session {
  sealed trait State
  case class Running() extends State
  case class Stopping() extends State
  case class Stopped() extends State

  def id: String

  def lastActivity: Long

  def state: State

  def executeStatement(statement: String): Future[ExecuteResponse]

  def statement(statementId: Int): Future[ExecuteResponse]

  def statements(): Future[List[ExecuteResponse]]

  def statements(fromIndex: Integer, toIndex: Integer): Future[List[ExecuteResponse]]

  def interrupt(): Future[Unit]

  def close(): Future[Unit]
}
