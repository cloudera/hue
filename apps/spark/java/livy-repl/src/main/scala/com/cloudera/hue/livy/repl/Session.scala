package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.msgs.ExecuteRequest
import org.json4s.JValue

import _root_.scala.concurrent.Future

trait Session {
  def statements: Seq[JValue]

  def statement(id: Int): Option[JValue]

  def execute(request: ExecuteRequest): Future[JValue]

  def close(): Unit
}
