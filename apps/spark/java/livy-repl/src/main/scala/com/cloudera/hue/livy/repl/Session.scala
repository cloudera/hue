package com.cloudera.hue.livy.repl

import com.cloudera.hue.livy.Utils
import org.json4s.JValue

import _root_.scala.annotation.tailrec
import _root_.scala.concurrent.duration.Duration
import _root_.scala.concurrent.{TimeoutException, Future}

object Session {
  sealed trait State
  case class NotStarted() extends State
  case class Starting() extends State
  case class Idle() extends State
  case class Busy() extends State
  case class Error() extends State
  case class ShuttingDown() extends State
  case class ShutDown() extends State

  sealed trait Kind
  case class Spark() extends Kind {
    override def toString = "spark"
  }

  case class PySpark() extends Kind {
    override def toString = "pyspark"
  }
}

trait Session {
  import Session._

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
