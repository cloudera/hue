package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.ExecuteResponse

import scala.concurrent.Future

trait Session {
  def statements: List[ExecuteResponse]

  def statement(id: Int): Option[ExecuteResponse]

  def execute(command: String): Future[ExecuteResponse]

  def close(): Unit
}
