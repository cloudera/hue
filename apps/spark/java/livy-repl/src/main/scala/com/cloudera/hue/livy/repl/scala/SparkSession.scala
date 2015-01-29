package com.cloudera.hue.livy.repl.scala

import java.util.concurrent.SynchronousQueue

import com.cloudera.hue.livy.msgs.ExecuteRequest
import com.cloudera.hue.livy.repl.Session
import org.json4s.jackson.JsonMethods._
import org.json4s.jackson.Serialization.write
import org.json4s.{JValue, _}

import scala.collection.mutable
import scala.concurrent.duration.Duration
import scala.concurrent.{Await, ExecutionContext, Future, Promise}

object SparkSession {
  def create(): Session = new SparkSession()
}

private class SparkSession extends Session {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  implicit val formats = DefaultFormats

  private[this] val inQueue = new SynchronousQueue[ILoop.Request]
  private[this] var executedStatements = 0
  private[this] var statements_ = new mutable.ArrayBuffer[JValue]

  org.apache.spark.repl.Main.interp = new ILoop(inQueue)

  // Launch the real interpreter thread.
  private[this] val thread = new Thread {
    override def run(): Unit = {
      val args = Array("-usejavacp")
      org.apache.spark.repl.Main.interp.process(args)
    }
  }
  thread.start()

  override def statements: List[JValue] = synchronized {
    statements_.toList
  }

  override def statement(id: Int): Option[JValue] = synchronized {
    if (id < statements_.length) {
      Some(statements_(id))
    } else {
      None
    }
  }

  override def execute(content: ExecuteRequest): Future[JValue] = {
    executedStatements += 1

    val promise = Promise[ILoop.ExecuteResponse]()
    inQueue.put(ILoop.ExecuteRequest(content.code, promise))

    promise.future.map {
      case rep =>
        val x = executedStatements - 1
        parse(write(Map(
          "status" -> "ok",
          "execution_count" -> x,
          "payload" -> Map(
            "text/plain" -> rep.output
          )
        )))
    }
  }

  override def close(): Unit = {
    val promise = Promise[ILoop.ShutdownResponse]()
    inQueue.put(ILoop.ShutdownRequest(promise))

    Await.result(promise.future, Duration.Inf)

    thread.join()
  }
}
