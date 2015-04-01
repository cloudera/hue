package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.Utils
import com.cloudera.hue.livy.sessions.{Kind, State}
import org.json4s.JValue

import _root_.scala.concurrent.duration.Duration
import _root_.scala.concurrent.{Future, TimeoutException}

trait Session {
  def kind: Kind

  def state: State

  def execute(code: String): Future[JValue]

  def history(): Seq[JValue]

  def history(id: Int): Option[JValue]

  def close(): Unit

  @throws(classOf[TimeoutException])
  @throws(classOf[InterruptedException])
  final def waitForStateChange(oldState: State, atMost: Duration) = {
    Utils.waitUntil({ () => state != oldState }, atMost)
  }
}
