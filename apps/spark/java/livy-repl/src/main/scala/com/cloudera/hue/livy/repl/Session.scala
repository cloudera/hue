package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.ExecuteResponse

import _root_.scala.concurrent.Future

trait Session {
  def statements: Seq[ExecuteResponse]

  def statement(id: Int): Option[ExecuteResponse]

  def execute(command: String): Future[ExecuteResponse]

  def close(): Unit
}
