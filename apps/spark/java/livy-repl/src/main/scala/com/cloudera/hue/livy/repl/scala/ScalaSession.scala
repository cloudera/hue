package com.cloudera.hue.livy.repl.scala

import java.util.concurrent.SynchronousQueue

import com.cloudera.hue.livy.ExecuteResponse
import com.cloudera.hue.livy.repl.Session

import scala.collection.mutable
import scala.concurrent.duration.Duration
import scala.concurrent.{Await, ExecutionContext, Future, Promise}

object ScalaSession {
  def create(): Session = new ScalaSession()
}

private class ScalaSession extends Session {
  private implicit def executor: ExecutionContext = ExecutionContext.global

  private[this] val inQueue = new SynchronousQueue[ILoop.Request]
  private[this] var executedStatements = 0
  private[this] var statements_ = new mutable.ArrayBuffer[ExecuteResponse]

  org.apache.spark.repl.Main.interp = new ILoop(inQueue)

  // Launch the real interpreter thread.
  private[this] val thread = new Thread {
    override def run(): Unit = {
      val args = Array("-usejavacp")
      org.apache.spark.repl.Main.interp.process(args)
    }
  }
  thread.start()

  override def statements: List[ExecuteResponse] = synchronized {
    statements_.toList
  }

  override def statement(id: Int): Option[ExecuteResponse] = synchronized {
    if (id < statements_.length) {
      Some(statements_(id))
    } else {
      None
    }
  }

  override def execute(statement: String): Future[ExecuteResponse] = {
    executedStatements += 1

    val promise = Promise[ILoop.ExecuteResponse]()
    inQueue.put(ILoop.ExecuteRequest(statement, promise))

    promise.future.map {
      case rep =>
        val executeResponse = ExecuteResponse(executedStatements - 1, List(statement), List(rep.output))
        synchronized { statements_ += executeResponse }
        executeResponse
    }
  }

  override def close(): Unit = {
    val promise = Promise[ILoop.ShutdownResponse]()
    inQueue.put(ILoop.ShutdownRequest(promise))

    Await.result(promise.future, Duration.Inf)

    thread.join()
  }
}
